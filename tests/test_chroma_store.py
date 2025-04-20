"""Tests for the ChromaDB store implementation."""
import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil
import os
import time
from rag.store.chroma_store import ChromaStore

@pytest.fixture
def temp_db_dir():
    """Create a temporary directory for the ChromaDB."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after tests - add a small delay to ensure files are released
    time.sleep(0.1)
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        # If files are still locked, try again after a longer delay
        time.sleep(0.5)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # If still failing, log but don't fail the test
            print(f"Warning: Could not remove temporary directory {temp_dir}")

@pytest.fixture
def chroma_store(temp_db_dir):
    """Create a ChromaStore instance for testing."""
    store = ChromaStore(persist_directory=temp_db_dir)
    yield store
    # Cleanup after tests
    store.close()
    # Add a small delay to ensure files are released
    time.sleep(0.1)

def test_chroma_store_initialization(chroma_store):
    """Test that ChromaStore initializes correctly."""
    assert chroma_store.collection is not None

def test_chroma_store_store_and_search(chroma_store):
    """Test storing and searching vectors."""
    # Create test vectors
    vectors = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0]
    ]
    ids = ["doc1", "doc2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    
    # Store vectors
    chroma_store.store(vectors, ids, metadatas)
    
    # Search for similar vectors
    query_vector = [1.0, 2.0, 3.0]
    results = chroma_store.search(query_vector, n_results=2)
    
    assert len(results) == 2
    assert results[0]["id"] == "doc1"  # Should be most similar
    assert results[1]["id"] == "doc2"

def test_chroma_store_empty_search(chroma_store):
    """Test searching when no vectors are stored."""
    query_vector = [1.0, 2.0, 3.0]
    results = chroma_store.search(query_vector, n_results=2)
    assert len(results) == 0

def test_chroma_store_duplicate_ids(chroma_store):
    """Test storing vectors with duplicate IDs."""
    # Store initial vector
    vectors1 = [[1.0, 2.0, 3.0]]
    ids1 = ["doc1"]
    metadatas1 = [{"source": "test1"}]
    chroma_store.store(vectors1, ids1, metadatas1)
    
    # Store vector with same ID
    vectors2 = [[4.0, 5.0, 6.0]]
    ids2 = ["doc1"]
    metadatas2 = [{"source": "test2"}]
    chroma_store.store(vectors2, ids2, metadatas2)
    
    # Search should return the updated vector
    query_vector = [4.0, 5.0, 6.0]
    results = chroma_store.search(query_vector, n_results=1)
    
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
    assert results[0]["metadata"]["source"] == "test2" 