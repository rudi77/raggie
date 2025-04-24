from typing import List, Dict, Any, Optional
from .chunker import BaseChunker
from ..core.models import Document, Chunk
import uuid
from langchain.text_splitter import MarkdownHeaderTextSplitter

class MarkdownChunker(BaseChunker):
    """Markdown-based chunking strategy using langchain's MarkdownHeaderTextSplitter."""
    
    def __init__(self, headers_to_split_on: Optional[List[Dict[str, str]]] = None):
        """
        Initialize the chunker.
        
        Args:
            headers_to_split_on: List of header configurations to split on.
                Each config is a dict with 'level' and 'name' keys.
                Example: [{"level": 1, "name": "h1"}, {"level": 2, "name": "h2"}]
        """
        super().__init__(chunk_size=0, chunk_overlap=0)  # Not used for this chunker
        
        # Default headers to split on if none provided
        self.headers_to_split_on = headers_to_split_on or [
            {"level": 1, "name": "h1"},
            {"level": 2, "name": "h2"},
            {"level": 3, "name": "h3"}
        ]
        
        self.text_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split document into chunks based on markdown headers."""
        # Use langchain's text splitter to get the chunks
        markdown_docs = self.text_splitter.split_text(document.content)
        
        # Convert to our Chunk model
        chunks = []
        
        for i, md_doc in enumerate(markdown_docs):
            # Extract the content and metadata
            content = md_doc.page_content
            metadata = md_doc.metadata
            
            # Find the position of this chunk in the original text
            # This is approximate since we don't have exact positions
            chunk_start = document.content.find(content)
            if chunk_start == -1:
                # If we can't find the exact position, estimate it
                chunk_start = i * 1000  # Rough estimate
            
            chunk_end = chunk_start + len(content)
            
            # Create our Chunk model
            chunk = self._create_chunk(
                content=content,
                document=document,
                start_idx=chunk_start,
                end_idx=chunk_end
            )
            
            # Add the markdown header metadata
            chunk.metadata.update({
                "chunk_index": i,
                "markdown_headers": metadata
            })
            
            chunks.append(chunk)
        
        return chunks 