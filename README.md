# RAG System

A simple and efficient Retrieval-Augmented Generation (RAG) system for document ingestion and querying.

## Features

- Document ingestion with configurable chunking
- Vector-based semantic search
- CLI interface for easy interaction
- Support for multiple document types
- Efficient storage using ChromaDB

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rag-system.git
cd rag-system
```

2. Install the package using `uv`:
```bash
uv venv
uv pip install -e .
```

For development, install with additional dependencies:
```bash
uv pip install -e ".[dev]"
```

## Usage

The RAG system provides a CLI interface with the following commands:

### Ingest Documents

```bash
# Ingest a single document
rag ingest path/to/document.pdf

# Ingest a directory recursively
rag ingest path/to/directory --recursive

# Customize chunk size and overlap
rag ingest path/to/document.pdf --chunk-size 1000 --chunk-overlap 200
```

### Query Documents

```bash
# Search with default settings (5 results)
rag query "your search query"

# Specify number of results
rag query "your search query" --num-results 10
```

### Clear Documents

```bash
# Clear all documents (with confirmation)
rag clear

# Force clear without confirmation
rag clear --force
```

## Configuration

The system uses environment variables for configuration. Create a `.env` file in your project root:

```env
OPENAI_API_KEY=your_api_key_here
CHROMA_DB_PATH=path/to/your/chroma/db
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

The project uses several tools to maintain code quality:

- `ruff` for linting
- `black` for code formatting
- `mypy` for type checking

Run all checks:
```bash
ruff check .
black .
mypy .
```

## License

MIT License - see LICENSE file for details
