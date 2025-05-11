from typing import List, Dict, Any, Optional, Union, Iterator
from pathlib import Path, PurePath
from io import BytesIO
import base64
import pdfplumber
from PIL import Image
from langchain_core.documents import Document
from langchain_community.document_loaders.pdf import BasePDFLoader
from rag.llm.vision_model import create_vision_model, VisionModel

class AdvancedPDFLoader(BasePDFLoader):
    """Advanced PDF loader that handles text, tables, and images with optional vision model support."""
    
    def __init__(
        self,
        file_path: Union[str, PurePath],
        include_images: bool = True,
        include_tables: bool = True,
        vision_model: Optional[VisionModel] = None,
        headers: Optional[dict] = None
    ):
        """Initialize the loader.
        
        Args:
            file_path: Path to the PDF file (local, S3, or web path)
            include_images: Whether to process images
            include_tables: Whether to process tables
            vision_model: Optional vision model for image descriptions
            headers: Optional headers for web requests
        """
        super().__init__(file_path, headers=headers)
        self.include_images = include_images
        self.include_tables = include_tables
        self.vision_model = vision_model

    def _process_image(self, image: Image.Image) -> Dict[str, Any]:
        """Process an image and get its description if vision model is available."""
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG' if image.mode == 'RGB' else 'PNG')
        image_b64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
        
        description = ""
        if self.vision_model:
            try:
                description = self.vision_model.describe_image(image)
            except Exception as e:
                print(f"Error getting image description: {e}")
        
        return {
            "image_base64": image_b64,
            "description": description
        }

    def _process_table(self, table: List[List[str]]) -> str:
        """Convert a table to a readable text format."""
        if not table:
            return ""
        
        # Convert table to markdown format
        markdown_table = []
        # Add header
        markdown_table.append("| " + " | ".join(str(cell) for cell in table[0]) + " |")
        markdown_table.append("| " + " | ".join(["---"] * len(table[0])) + " |")
        # Add rows
        for row in table[1:]:
            markdown_table.append("| " + " | ".join(str(cell) for cell in row) + " |")
        
        return "\n".join(markdown_table)

    # Please look at the BaseLoader. There it is stated that this method shall
    # be implemented in all the existing subclasses. Do not implement the load method!!!!!!
    def lazy_load(self) -> Iterator[Document]:
        """Lazily load and process the PDF file page by page.
        
        Yields:
            Document objects containing text, tables, and images for each page.
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                print(f"Processing PDF: {self.file_path}")
                print(f"Total pages: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages):
                    print(f"\nProcessing page {page_num + 1}/{len(pdf.pages)}")
                    
                    # Extract text
                    text_content = page.extract_text() or ""                    
                    word_count = len(text_content.split())
                    print(f"Extracted {word_count} words from page {page_num + 1}")
                    
                    # Initialize metadata
                    file_name_path = Path(self.file_path)
                    metadata = {
                        "source": str(self.source),
                        "file_name": file_name_path.name,
                        "page_number": page_num + 1,
                        "content_type": "text",
                        "has_tables": False,
                        "has_images": False,
                        "image_count": 0
                    }
                    
                    if self.include_tables:
                        tables = page.extract_tables()
                        if tables:
                            print(f"Found {len(tables)} tables on page {page_num + 1}")
                            table_texts = [self._process_table(table) for table in tables]
                            text_content += "\n\nTables:\n" + "\n\n".join(table_texts)
                            metadata["has_tables"] = True
                        else:
                            print(f"No tables found on page {page_num + 1}")
                                        
                    if self.include_images or word_count < 100:
                        image_descriptions = []
                        processed_images = []
                        
                        # Process page as image if text is sparse, otherwise process embedded images
                        images_to_process = []
                        if word_count < 100:
                            try:
                                print(f"Converting page {page_num + 1} to image due to sparse text")
                                images_to_process.append(page.to_image().original)
                            except Exception as e:
                                print(f"Error converting page {page_num + 1} to image: {str(e)}")
                        elif page.images:
                            print(f"Found {len(page.images)} embedded images on page {page_num + 1}")
                            for img_num, img in enumerate(page.images, 1):
                                try:
                                    images_to_process.append(Image.open(BytesIO(img['stream'].get_data())))
                                except Exception as e:
                                    print(f"Error processing image {img_num} on page {page_num + 1}: {str(e)}")
                        
                        for img_num, image in enumerate(images_to_process, 1):
                            print(f"Processing image {img_num}/{len(images_to_process)} on page {page_num + 1}")
                            processed = self._process_image(image)
                            if processed["description"]:
                                print(f"Generated description for image {img_num}")
                                image_descriptions.append(processed["description"])
                            processed_images.append(processed)
                        
                        if image_descriptions:
                            print(f"Added {len(image_descriptions)} image descriptions to page {page_num + 1}")
                            text_content += "\n\n" + "\n".join(image_descriptions)
                            metadata["has_images"] = True
                            metadata["image_count"] = len(processed_images)
                    
                    if text_content.strip():
                        yield Document(
                            page_content=text_content.strip(),
                            metadata=metadata
                        )
                    else:
                        print(f"No content extracted from page {page_num + 1}")
        
        except Exception as e:
            print(f"Error processing PDF {self.file_path}: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

# Example usage:
def load_pdf_for_rag(
    file_path: Union[str, PurePath],
    vision_model: Optional[Any] = None,
    include_images: bool = True,
    include_tables: bool = True,
    headers: Optional[dict] = None
) -> List[Document]:
    """
    Load a PDF file and prepare it for RAG.
    
    Args:
        file_path: Path to the PDF file (local, S3, or web path)
        vision_model: Optional vision model for image descriptions
        include_images: Whether to process images
        include_tables: Whether to process tables
        headers: Optional headers for web requests
    
    Returns:
        List of Document objects ready for RAG
    """
    loader = AdvancedPDFLoader(
        file_path=file_path,
        include_images=include_images,
        include_tables=include_tables,
        vision_model=vision_model,
        headers=headers
    )
    return loader.load()


if __name__ == "__main__":
    import os

    file_path = r"YOUR_PDF_PATH"
    vision_model = create_vision_model(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-4.1-nano",
        max_tokens=300,
    )

    documents = load_pdf_for_rag(
        file_path=file_path,
        vision_model=vision_model,
        include_images=True,
        include_tables=True
    )
    for document in documents:
        print(document.page_content)
        print("\n--------------------------------\n")
