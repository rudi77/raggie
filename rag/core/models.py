from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Document:
    """Represents a source document in the RAG system."""
    id: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    source: str  # e.g., file path, URL, etc.

    def __init__(self, id: str, content: str, metadata: Optional[Dict[str, Any]] = None, 
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None, 
                 source: Optional[str] = None):
        self.id = id
        self.content = content
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.source = source or self.metadata.get('source', '')

@dataclass
class Chunk:
    """Represents a chunk of text from a document."""
    id: str
    content: str
    document_id: str
    metadata: Dict[str, Any]
    start_index: int
    end_index: int

    def __init__(self, id: str, document_id: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.document_id = document_id
        self.content = content
        self.metadata = metadata or {}

@dataclass
class Vector:
    """Represents a vector embedding."""
    id: str
    values: List[float]
    metadata: Dict[str, Any]

    def __init__(self, id: str, values: List[float], metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.values = values
        self.metadata = metadata or {}

@dataclass
class Prompt:
    """Represents a prompt template with variables."""
    template: str
    variables: Dict[str, Any]

@dataclass
class Response:
    """Represents a response from the LLM."""
    content: str
    sources: List[Dict[str, Any]]  # List of source documents used
    metadata: Dict[str, Any]

@dataclass
class FinalAnswer:
    """Represents the final answer with sources and metadata."""
    content: str
    sources: List[Dict[str, Any]]
    confidence: float
    metadata: Dict[str, Any]
    created_at: datetime 