# rag/ingestion/deepdoc_pdf_loader.py

from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator
from io import BytesIO
import base64 # For image encoding

from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document as LangchainDocument


from rag.third_party_rag.rag.app.manual import Pdf as RagflowManualPdfParser
# CV model wrapper for image descriptions (Example: GPT-4 Vision)
from rag.third_party_rag.rag.llm.cv_model import GptV4 as RagflowGptV4Vision # Adjust this to your chosen VLM
# Helper function for image descriptions
from rag.third_party_rag.rag.app.picture import vision_llm_chunk
from rag.third_party_rag.rag.prompts import vision_llm_figure_describe_prompt # Prompt for figures

class DeepDocLangchainPDFLoader(BaseLoader):
    """
    A langchain loader for deepdoc pdf files.
    """
    def __init__(
        self,
        file_path: str,
        ragflow_parser_config: Optional[Dict[str, Any]] = None,
        tenant_id: str = "standalone_tenant", # Dummy, if needed for CV model
        cv_llm_name: Optional[str] = None, # e.g. "gpt-4-vision-preview"
        cv_llm_key: Optional[str] = None,
        cv_llm_base_url: Optional[str] = None,
        include_images: bool = True, # Whether to process images
        include_tables_as_text: bool = True
    ):
        self.file_path = file_path
        self.pdf_parser = RagflowManualPdfParser() # Instance of deepdoc PDF parser
        self.ragflow_parser_config = ragflow_parser_config if ragflow_parser_config else {}
        self._callback = lambda prog, msg: print(f"DeepDocLangchainPDFLoader - Progress: {prog}, Message: {msg}")
        self.include_images = include_images
        self.include_tables_as_text = include_tables_as_text

        self.vision_model = None
        if self.include_images and cv_llm_name and cv_llm_key:
            try:
                # Direct instantiation of the CV model
                # Adjust this to the specific CV model you want to use.
                if "gpt-4-vision" in cv_llm_name: # Example
                    self.vision_model = RagflowGptV4Vision(key=cv_llm_key, model_name=cv_llm_name, base_url=cv_llm_base_url, lang="English") # Adjust language for VLM
                # Add logic for other CV models from rag.llm.cv_model here if needed
                print(f"Vision model {cv_llm_name} initialized for {self.file_path}.")
            except Exception as e:
                print(f"Could not load vision model '{cv_llm_name}' for {self.file_path}: {e}. Image description will be skipped.")
                self.vision_model = None
        elif self.include_images and not (cv_llm_name and cv_llm_key):
            print(f"No CV model or key configured for {self.file_path}. Image description will be skipped.")
            self.include_images = False


    def lazy_load(self) -> Iterator[LangchainDocument]:
        """A lazy implementation that loads documents one by one."""
        try:
            with open(self.file_path, "rb") as f:
                binary_content = f.read()

            filename_str = Path(self.file_path).name

            # Use the RAG-Flow PdfParser
            # The __call__ method of RagflowManualPdfParser returns:
            # sections: List[(text_content, layout_no, positions_list)]
            # tbls_figs: List[((img_obj, table_html_or_desc_list), positions_list)]
            sections, tbls_figs = self.pdf_parser(
                filename=filename_str,
                binary=binary_content,
                callback=self._callback,
                from_page=self.ragflow_parser_config.get("from_page", 0),
                to_page=self.ragflow_parser_config.get("to_page", 100000),
                zoomin=self.ragflow_parser_config.get("zoomin", 3)
            )

            # 1. Process text sections
            # Here you can decide whether to treat each section extracted by deepdoc as
            # its own Langchain document or combine them per page.
            # For finer control by subsequent Langchain splitters, it's often better
            # to create larger coherent text blocks (e.g., per page).
            # The RAG-Flow `manual.chunk` already combines them into larger chunks.
            # Here we create a document for each text section returned by RAG-Flow PdfParser.
            # Positions are stored in metadata.

            doc_counter = 0
            for text_content, layout_no, positions_list in sections:
                if not text_content.strip():
                    continue

                page_num_zero_based = positions_list[0][0] if positions_list else -1
                metadata = {
                    "source": filename_str,
                    "page_number": page_num_zero_based + 1, # 1-based page number
                    "content_type": "text_section",
                    "layout_type": layout_no,
                    "positions": positions_list # Stores the exact coordinates of the text block
                }
                doc_counter += 1
                yield LangchainDocument(page_content=text_content, metadata=metadata)

            # 2. Process extracted tables and figures
            for (img_obj, content_list_or_html), positions_list in tbls_figs:
                if not content_list_or_html and not (self.include_images and img_obj and self.vision_model):
                    continue

                page_num_zero_based = positions_list[0][0] if positions_list else -1
                item_type = "table" if isinstance(content_list_or_html, str) and "<table>" in content_list_or_html.lower() else "figure"

                text_for_embedding = ""
                image_b64 = None

                if isinstance(content_list_or_html, list): # Often image captions
                    text_for_embedding = "\n".join(content_list_or_html)
                elif isinstance(content_list_or_html, str): # Often HTML for tables
                    if self.include_tables_as_text or item_type != "table":
                        text_for_embedding = content_list_or_html

                metadata_item = {
                    "source": filename_str,
                    "page_number": page_num_zero_based + 1,
                    "content_type": item_type,
                    "original_positions": positions_list,
                }

                if self.include_images and img_obj and self.vision_model:
                    try:
                        print(f"Processing image for {filename_str} page {page_num_zero_based + 1} ({item_type})...")
                        # Store the image as Base64 in metadata
                        img_byte_arr = BytesIO()
                        img_obj.save(img_byte_arr, format='JPEG' if img_obj.mode == 'RGB' else 'PNG')
                        image_b64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
                        metadata_item["image_base64"] = image_b64 # Only for display/reference, not directly for embedding

                        # Generate a description with the VLM
                        # The `vision_llm_chunk` function from RAG-Flow is useful here.
                        # It expects the PIL Image object.
                        figure_prompt_text = vision_llm_figure_describe_prompt()
                        vlm_description = vision_llm_chunk(
                            binary=img_obj, # PIL Image object
                            vision_model=self.vision_model,
                            prompt=figure_prompt_text,
                            callback=self._callback
                        )

                        if vlm_description:
                            # Combine original caption (if available) and VLM description
                            if text_for_embedding and item_type == "figure": # Only for figures, table HTML remains as is
                                text_for_embedding = f"Image caption: {text_for_embedding}\nAI-generated description of the figure: {vlm_description}"
                            else:
                                text_for_embedding = vlm_description
                            metadata_item["vlm_description_available"] = True
                        print(f"Image description for {filename_str} page {page_num_zero_based + 1} created: {text_for_embedding[:100]}...")

                    except Exception as e_vlm:
                        print(f"Error in VLM processing for {filename_str} page {page_num_zero_based + 1}: {e_vlm}")
                        # Fallback to original text if VLM fails

                if text_for_embedding.strip(): # Only create documents with content
                    doc_counter += 1
                    yield LangchainDocument(page_content=text_for_embedding.strip(), metadata=metadata_item)

        except Exception as e:
            import traceback
            print(f"Critical error while processing file {self.file_path} with DeepDocLangchainPDFLoader: {e}")
            traceback.print_exc()
            # Here you could decide to yield an empty document or an error message
            # yield LangchainDocument(page_content=f"Error processing PDF: {e}", metadata={"source": str(self.file_path)})

    def load(self) -> List[LangchainDocument]:
        """Loads all documents."""
        return list(self.lazy_load())