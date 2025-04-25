import pytest
from datetime import datetime
from rag.chunking.token_chunker import TokenChunker
from rag.core.models import Document, Chunk

def test_token_chunker_initialization():
    """Test that the TokenChunker initializes correctly."""
    chunker = TokenChunker(chunk_size=10, chunk_overlap=2)
    assert chunker.chunk_size == 10
    assert chunker.chunk_overlap == 2

def test_token_chunker_chunk_simple():
    """Test chunking a simple document."""
    chunker = TokenChunker(chunk_size=10, chunk_overlap=2)
    doc = Document(
        id="test-id",
        content="This is a test document with multiple words.",
        metadata={}
    )
    
    chunks = chunker.chunk(doc)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert all(chunk.document_id == doc.id for chunk in chunks)
    
    # Check that chunks don't exceed the size limit
    for chunk in chunks:
        assert len(chunk.content) <= chunker.chunk_size

def test_token_chunker_chunk_empty():
    """Test chunking an empty document."""
    chunker = TokenChunker()
    doc = Document(
        id="test-id",
        content="",
        metadata={}
    )
    
    chunks = chunker.chunk(doc)
    assert len(chunks) == 0

def test_token_chunker_chunk_smaller_than_size():
    """Test chunking a document smaller than chunk size."""
    chunker = TokenChunker(chunk_size=100)
    doc = Document(
        id="test-id",
        content="This is a small document.",
        metadata={}
    )
    
    chunks = chunker.chunk(doc)
    assert len(chunks) == 1
    assert chunks[0].content == doc.content
    assert chunks[0].document_id == doc.id 