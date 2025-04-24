from typing import List, Dict, Any
from .chunker import BaseChunker
from ..core.models import Document, Chunk
import uuid

class PageWiseChunker(BaseChunker):
    """Page-based chunking strategy that splits documents at page boundaries."""
    
    def __init__(self, min_page_size: int = 100):
        """
        Initialize the chunker.
        
        Args:
            min_page_size: Minimum size of a page to be considered valid.
                          Pages smaller than this will be merged with the next page.
        """
        super().__init__(chunk_size=0, chunk_overlap=0)  # Not used for this chunker
        self.min_page_size = min_page_size
    
    def chunk(self, document: Document) -> List[Chunk]:
        """Split document into chunks based on page boundaries."""
        # Get page markers from document metadata if available
        page_markers = document.metadata.get('page_markers', [])
        if not page_markers:
            # If no page markers, try to detect pages using common markers
            content = document.content
            # Common page break markers
            markers = ['\f', '\n\n---\n\n', '\n\n***\n\n', '\n\nPage ', '\n\n[Page']
            
            current_pos = 0
            for marker in markers:
                while True:
                    pos = content.find(marker, current_pos)
                    if pos == -1:
                        break
                    page_markers.append(pos)
                    current_pos = pos + len(marker)
        
        # Add start and end positions
        page_markers = [0] + sorted(page_markers) + [len(document.content)]
        
        # Create chunks from pages
        chunks = []
        for i in range(len(page_markers) - 1):
            start_idx = page_markers[i]
            end_idx = page_markers[i + 1]
            
            # Extract page content
            page_content = document.content[start_idx:end_idx].strip()
            
            # Skip empty pages or those below minimum size
            if not page_content or len(page_content) < self.min_page_size:
                continue
            
            # Create chunk for this page
            chunk = self._create_chunk(
                content=page_content,
                document=document,
                start_idx=start_idx,
                end_idx=end_idx
            )
            
            # Add page-specific metadata
            chunk.metadata.update({
                "chunk_type": "page",
                "page_number": i + 1,
                "page_markers": {
                    "start": start_idx,
                    "end": end_idx
                }
            })
            
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, content: str, document: Document, start_idx: int, end_idx: int) -> Chunk:
        """Create a chunk with the given content and metadata."""
        return Chunk(
            id=str(uuid.uuid4()),
            content=content,
            document_id=document.id,
            metadata={
                "start_index": start_idx,
                "end_index": end_idx,
                "source": document.source
            }
        ) 