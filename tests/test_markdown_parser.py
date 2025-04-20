import pytest
from rag.ingestion.markdown_parser import MarkdownParser
from rag.core.models import Document

def test_markdown_parser_initialization():
    """Test that the MarkdownParser initializes correctly."""
    parser = MarkdownParser()
    assert ".md" in parser.supported_extensions
    assert ".markdown" in parser.supported_extensions

def test_markdown_parser_can_parse():
    """Test that the parser correctly identifies markdown files."""
    parser = MarkdownParser()
    assert parser.can_parse("test.md") is True
    assert parser.can_parse("test.markdown") is True
    assert parser.can_parse("test.txt") is False

def test_markdown_parser_parse():
    """Test that the parser correctly parses markdown content."""
    parser = MarkdownParser()
    content = "# Test Heading\n\nThis is a test paragraph."
    metadata = {"source": "test.md"}
    
    doc = parser.parse(content, metadata)
    
    assert isinstance(doc, Document)
    assert doc.content == content
    assert "html_content" in doc.metadata
    assert "<h1>Test Heading</h1>" in doc.metadata["html_content"]
    assert "<p>This is a test paragraph.</p>" in doc.metadata["html_content"] 