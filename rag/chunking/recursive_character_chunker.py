from typing import List, Dict, Any
from .chunker import BaseChunker
from ..core.models import Document, Chunk
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter

class RecursiveCharacterChunker(BaseChunker):
    """Recursive character-based chunking strategy using langchain's RecursiveCharacterTextSplitter."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, 
                 separators: List[str] = None, keep_separator: bool = False):
        """
        Initialize the chunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting text
            keep_separator: Whether to keep the separator in the chunk
        """
        super().__init__(chunk_size, chunk_overlap)
        self.separators = separators or ["\n\n", "\n", " ", ""]
        self.keep_separator = keep_separator
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self.separators,
            keep_separator=keep_separator
        )
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split document into chunks using recursive character splitting."""
        # Use langchain's text splitter to get the chunks
        text_chunks = self.text_splitter.split_text(document.content)
        
        # Convert to our Chunk model
        chunks = []
        current_position = 0
        
        for i, text_chunk in enumerate(text_chunks):
            # Find the position of this chunk in the original text
            chunk_start = document.content.find(text_chunk, current_position)
            if chunk_start == -1:
                # If we can't find the exact position, estimate it
                chunk_start = current_position
            
            chunk_end = chunk_start + len(text_chunk)
            current_position = chunk_end
            
            # Create our Chunk model
            chunk = self._create_chunk(
                content=text_chunk,
                document=document,
                start_idx=chunk_start,
                end_idx=chunk_end
            )
            
            # Add additional metadata
            chunk.metadata.update({
                "chunk_index": i,
                "separator_used": self._find_used_separator(text_chunk, document.content, chunk_start)
            })
            
            chunks.append(chunk)
        
        return chunks
    
    def _find_used_separator(self, chunk: str, full_text: str, start_pos: int) -> str:
        """Find which separator was used to create this chunk."""
        # Look at the text before and after the chunk to determine the separator
        if start_pos > 0:
            before_text = full_text[max(0, start_pos - 10):start_pos]
            for sep in self.separators:
                if before_text.endswith(sep):
                    return sep
        
        # If we couldn't find a separator before, look after
        end_pos = start_pos + len(chunk)
        if end_pos < len(full_text):
            after_text = full_text[end_pos:min(end_pos + 10, len(full_text))]
            for sep in self.separators:
                if after_text.startswith(sep):
                    return sep
        
        return "unknown" 