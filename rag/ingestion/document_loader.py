from pathlib import Path
from typing import List, Optional, Union

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangchainDocument

class DocumentLoader:
    """Handles loading and processing of various document types."""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter()

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
            return PyPDFLoader(str(file_path))
        elif suffix == ".txt":
            return TextLoader(str(file_path))
        elif suffix == ".md":
            return UnstructuredMarkdownLoader(str(file_path))
        return None

    def chunk_document(
        self, document: LangchainDocument, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> List[LangchainDocument]:
        """Split a document into chunks."""
        self.text_splitter.chunk_size = chunk_size
        self.text_splitter.chunk_overlap = chunk_overlap
        
        return self.text_splitter.split_documents([document]) 