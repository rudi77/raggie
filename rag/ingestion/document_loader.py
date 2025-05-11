import os
from pathlib import Path
from typing import List, Optional, Union
import uuid
from datetime import datetime

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.schema import Document as LangchainDocument

from rag.core.models import Document as RagDocument, Chunk
from rag.chunking import ChunkerFactory
from rag.llm.vision_model import create_vision_model
from .advanced_pdf_loader import AdvancedPDFLoader

class DocumentLoader:
    """Handles loading and processing of various document types."""

    def __init__(self):
        # We'll create the appropriate chunker when needed
        self.chunker = None

    def load_documents(
        self, path: Union[str, Path], recursive: bool = False
    ) -> List[LangchainDocument]:
        """Load documents from the given path."""
        path = Path(path)
        documents = []

        if path.is_file():
            documents.extend(self._load_single_file(path))
        elif path.is_dir():
            pattern = "**/*" if recursive else "*"
            for file_path in path.glob(pattern):
                if file_path.is_file():
                    documents.extend(self._load_single_file(file_path))

        return documents

    def _load_single_file(self, file_path: Path) -> List[LangchainDocument]:
        """Load a single file based on its extension."""
        loader = self._get_loader(file_path)
        if loader:
            return loader.load()
        return []

    def _get_loader(self, file_path: Path):
        """Get the appropriate loader for the file type."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            # return PyPDFLoader(str(file_path))
            vision_model = create_vision_model(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name="gpt-4.1-nano",
                max_tokens=300,
            )

            return AdvancedPDFLoader(
                file_path=file_path,
                vision_model=vision_model,
                include_images=True,
                include_tables=True
            )
        elif suffix == ".txt":
            return TextLoader(str(file_path))
        elif suffix == ".md":
            return UnstructuredMarkdownLoader(str(file_path))
        return None

    def chunk_document(
        self, document: LangchainDocument, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> List[LangchainDocument]:
        """Split a document into chunks using the appropriate chunker."""
        # Get the source file path from metadata
        source_path = document.metadata.get('source', '')
        
        # Create the appropriate chunker based on the file type
        self.chunker = ChunkerFactory.get_chunker_for_file(
            source_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        print(f"Using chunker: {self.chunker.__class__.__name__} for document: {source_path}")
        
        # Convert LangchainDocument to our RagDocument
        rag_document = RagDocument(
            id=str(uuid.uuid4()),
            content=document.page_content,
            metadata=document.metadata,
            source=source_path,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Use our custom chunker
        chunks = self.chunker.chunk(rag_document)
        
        # Convert our Chunks back to LangchainDocuments
        langchain_chunks = []
        for chunk in chunks:
            langchain_chunk = LangchainDocument(
                page_content=chunk.content,
                metadata={
                    **document.metadata,
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "start_index": chunk.metadata.get("start_index", 0),
                    "end_index": chunk.metadata.get("end_index", 0),
                    "chunker_type": self.chunker.__class__.__name__
                }
            )
            langchain_chunks.append(langchain_chunk)
        
        return langchain_chunks 