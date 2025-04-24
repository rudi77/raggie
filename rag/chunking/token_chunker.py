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
        
        print(f"Chunking document: {document.id}")
        
        while start_idx < len(content):
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.chunk_size, len(content))
            
            print(f"Chunking document: {document.id} from {start_idx} to {end_idx}")

            # Find the last space before the end to avoid cutting words
            if end_idx < len(content):
                last_space = content.rfind(' ', start_idx, end_idx)
                if last_space != -1:
                    end_idx = last_space
            
            # Create chunk
            chunk_content = content[start_idx:end_idx]
            chunk = self._create_chunk(chunk_content, document, start_idx, end_idx)
            
            print(f"Created chunk with length: {len(chunk_content)}")
            chunks.append(chunk)
            
            # Move start index for next chunk, considering overlap
            # Ensure we always advance at least one character to prevent infinite loops
            new_start_idx = end_idx - self.chunk_overlap
            if new_start_idx <= start_idx:
                # If we're not advancing, force advancement by at least one character
                new_start_idx = start_idx + 1
                print(f"Warning: Chunk overlap too large, forcing advancement to {new_start_idx}")
            
            start_idx = new_start_idx
            
            # Safety check to prevent infinite loops
            if start_idx >= len(content):
                break
        
        print(f"Finished chunking document: {document.id} into {len(chunks)} chunks")
        return chunks 