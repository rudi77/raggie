from typing import List, Dict, Any
from ..core.interfaces import IChunker
from ..core.models import Document, Chunk
import uuid

class BaseChunker(IChunker):
    """Base class for chunking strategies."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split a document into chunks."""
        raise NotImplementedError("Subclasses must implement chunk()")
    
    def _create_chunk(self, content: str, document: Document, start_idx: int, end_idx: int) -> Chunk:
        """Create a new chunk with metadata."""
        return Chunk(
            id=str(uuid.uuid4()),
            document_id=document.id,
            content=content,
            metadata={
                "start_index": start_idx,
                "end_index": end_idx,
                "chunk_size": len(content),
                "document_source": document.source
            }
        ) 