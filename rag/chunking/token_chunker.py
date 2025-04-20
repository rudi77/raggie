from typing import List
from .chunker import BaseChunker
from ..core.models import Document, Chunk

class TokenChunker(BaseChunker):
    """Token-based chunking strategy."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        super().__init__(chunk_size, chunk_overlap)
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split document into chunks based on token count."""
        chunks = []
        content = document.content
        start_idx = 0
        
        while start_idx < len(content):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.chunk_size, len(content))
            
            # Find the last space before the end to avoid cutting words
            if end_idx < len(content):
                last_space = content.rfind(' ', start_idx, end_idx)
                if last_space != -1:
                    end_idx = last_space
            
            # Create chunk
            chunk_content = content[start_idx:end_idx]
            chunk = self._create_chunk(chunk_content, document, start_idx, end_idx)
            chunks.append(chunk)
            
            # Move start index for next chunk, considering overlap
            start_idx = end_idx - self.chunk_overlap
        
        return chunks 