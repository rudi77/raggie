import pytest
import numpy as np
from rag.embedding.text_embedder import TextEmbedder
from rag.core.models import Vector

def test_text_embedder_initialization():
    """Test that the TextEmbedder initializes correctly."""
    embedder = TextEmbedder(model_name="all-MiniLM-L6-v2")
    assert embedder.model_name == "all-MiniLM-L6-v2"
    assert embedder.model is not None

def test_text_embedder_embed():
    """Test that the embedder generates embeddings."""
    embedder = TextEmbedder()
    text = "This is a test sentence."
    metadata = {"source": "test"}
    
    vector = embedder.embed(text, metadata)
    
    assert isinstance(vector, Vector)
    assert len(vector.values) > 0
    assert vector.metadata["text_length"] == len(text)
    assert vector.metadata["embedding_type"] == "text"
    assert vector.metadata["model_name"] == "all-MiniLM-L6-v2"

def test_text_embedder_embed_empty():
    """Test embedding an empty string."""
    embedder = TextEmbedder()
    text = ""
    metadata = {}
    
    vector = embedder.embed(text, metadata)
    
    assert isinstance(vector, Vector)
    assert len(vector.values) > 0
    assert vector.metadata["text_length"] == 0

def test_text_embedder_embed_long_text():
    """Test embedding a longer text."""
    embedder = TextEmbedder()
    text = " ".join(["This is a test sentence."] * 10)
    metadata = {"source": "test"}
    
    vector = embedder.embed(text, metadata)
    
    assert isinstance(vector, Vector)
    assert len(vector.values) > 0
    assert vector.metadata["text_length"] == len(text) 