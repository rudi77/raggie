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
        
        # If content is empty, return empty list
        if not content:
            return chunks
            
        # If content is smaller than chunk size, return single chunk
        if len(content) <= self.chunk_size:
            return [Chunk(
                id=f"{document.id}-0",
                content=content,
                document_id=document.id,
                metadata=document.metadata
            )]
        
        start_idx = 0
        chunk_idx = 0
        
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
            chunk = Chunk(
                id=f"{document.id}-{chunk_idx}",
                content=chunk_content,
                document_id=document.id,
                metadata=document.metadata
            )
            chunks.append(chunk)
            
            # Move start index for next chunk, considering overlap
            start_idx = end_idx - self.chunk_overlap
            if start_idx >= end_idx:
                # If we're not advancing, force advancement by at least one character
                start_idx = end_idx + 1
            
            chunk_idx += 1
            
            # Safety check to prevent infinite loops
            if start_idx >= len(content):
                break
        
        return chunks 