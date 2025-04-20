import pytest
from datetime import datetime
from rag.core.models import Document, Chunk, Vector, Prompt, Response, FinalAnswer

def test_document_creation():
    """Test creating a Document object."""
    doc = Document(
        id="test-id",
        content="Test content",
        metadata={"source": "test"}
    )
    
    assert doc.id == "test-id"
    assert doc.content == "Test content"
    assert doc.metadata["source"] == "test"

def test_chunk_creation():
    """Test creating a Chunk object."""
    chunk = Chunk(
        id="chunk-id",
        document_id="doc-id",
        content="Chunk content",
        metadata={"position": 0}
    )
    
    assert chunk.id == "chunk-id"
    assert chunk.content == "Chunk content"
    assert chunk.document_id == "doc-id"
    assert chunk.metadata["position"] == 0

def test_vector_creation():
    """Test creating a Vector object."""
    vector = Vector(
        id="vector-id",
        values=[0.1, 0.2, 0.3],
        metadata={"dim": 3}
    )
    
    assert vector.id == "vector-id"
    assert len(vector.values) == 3
    assert vector.metadata["dim"] == 3

def test_prompt_creation():
    """Test creating a Prompt object."""
    prompt = Prompt(
        template="Test {variable}",
        variables={"variable": "value"}
    )
    
    assert prompt.template == "Test {variable}"
    assert prompt.variables["variable"] == "value"

def test_response_creation():
    """Test creating a Response object."""
    response = Response(
        content="Test response",
        sources=[{"id": "doc1", "text": "source text"}],
        metadata={"model": "test"}
    )
    
    assert response.content == "Test response"
    assert len(response.sources) == 1
    assert response.metadata["model"] == "test"

def test_final_answer_creation():
    """Test creating a FinalAnswer object."""
    answer = FinalAnswer(
        content="Final answer",
        sources=[{"id": "doc1"}],
        confidence=0.95,
        metadata={"processed": True},
        created_at=datetime.utcnow()
    )
    
    assert answer.content == "Final answer"
    assert len(answer.sources) == 1
    assert answer.confidence == 0.95
    assert answer.metadata["processed"] is True 