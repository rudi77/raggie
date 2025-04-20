"""Common test fixtures and configuration."""
import pytest
import os
import shutil
from pathlib import Path
import tempfile
from rag.store.chroma_store import ChromaStore

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after all tests
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def chroma_store(test_data_dir):
    """Create a ChromaStore instance for testing with proper cleanup."""
    store = ChromaStore(
        collection_name="test_collection",
        persist_directory=os.path.join(test_data_dir, "chroma_db")
    )
    yield store
    # Cleanup after each test
    store.close()

@pytest.fixture
def sample_markdown_file(test_data_dir):
    """Create a sample markdown file for testing."""
    content = """# Sample Document
    
This is a test document with some content.
It has multiple lines and some formatting.

## Section 1
- Point 1
- Point 2

## Section 2
Some more text here.
"""
    file_path = Path(test_data_dir) / "sample.md"
    file_path.write_text(content)
    return str(file_path)

@pytest.fixture
def sample_text():
    """Return a sample text for testing."""
    return """This is a sample text.
It contains multiple lines.
And some basic content for testing.""" 