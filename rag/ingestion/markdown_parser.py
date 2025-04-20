from typing import Dict, Any
from datetime import datetime
import uuid
import markdown
from .file_parser import BaseFileParser
from ..core.models import Document

class MarkdownParser(BaseFileParser):
    """Parser for Markdown files."""
    
    def __init__(self):
        super().__init__(supported_extensions=[".md", ".markdown"])
        self.md = markdown.Markdown(extensions=['extra'])
    
    def parse(self, content: str, metadata: Dict[str, Any]) -> Document:
        """Parse Markdown content into a Document object."""
        # Convert markdown to HTML for better text extraction
        html_content = self.md.convert(content)
        
        # Create document with metadata
        doc = Document(
            id=str(uuid.uuid4()),
            content=content,  # Store original markdown
            metadata={
                **metadata,
                "html_content": html_content,
                "parsed_at": datetime.utcnow().isoformat()
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            source=metadata.get("source", "unknown")
        )
        
        return doc 