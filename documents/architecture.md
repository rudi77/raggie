# RAG System Architecture

This document describes the architecture and components of the RAG (Retrieval-Augmented Generation) system.

## Core Components

### Data Models (`rag/core/models.py`)

The system is built around several core data models:

- **Document**: Represents a source document with content, metadata, and source information
- **Chunk**: Represents a chunk of text from a document, including position information
- **Vector**: Represents a vector embedding with values and metadata
- **Prompt**: Represents a prompt template with variables
- **Response**: Represents an LLM response with content and source information
- **FinalAnswer**: Represents the final answer with sources, confidence, and metadata

### Interfaces (`rag/core/interfaces.py`)

The system defines several interfaces that components must implement:

- **IParser**: Interface for document parsers
- **IChunker**: Interface for text chunking strategies
- **IVectorStore**: Interface for vector storage implementations
- **IRetriever**: Interface for document retrieval
- **ILLMClient**: Interface for LLM interactions
- **IEmbedder**: Interface for embedding implementations
- **IPromptBuilder**: Interface for prompt construction
- **IPostProcessor**: Interface for response post-processing

## Component Structure

The system is organized into the following main directories:

- **core/**: Contains core data models and interfaces
- **chunking/**: Implements text chunking strategies
  - `chunker.py`: Base chunker interface
  - `token_chunker.py`: Token-based chunking implementation
  - `recursive_character_chunker.py`: Character-based recursive chunking
  - `markdown_chunker.py`: Markdown-aware chunking
  - `html_chunker.py`: HTML-aware chunking
  - `chunker_factory.py`: Factory for creating appropriate chunkers
- **embedding/**: Implements vector embedding generation
- **store/**: Implements vector storage and retrieval
- **llm/**: Implements LLM client interactions
- **ingestion/**: Handles document ingestion and parsing
- **cli/**: Command-line interface implementation

## Design Principles

1. **Modularity**: Each component is designed to be independent and replaceable
2. **Interface-based**: Components communicate through well-defined interfaces
3. **Extensibility**: New implementations can be added by implementing the appropriate interfaces
4. **Configuration-driven**: System behavior is controlled through configuration
5. **Type Safety**: Strong typing throughout the codebase

## Data Flow

1. Documents are ingested and parsed into Document objects
2. Documents are chunked into smaller pieces using appropriate chunking strategies:
   - Text files use recursive character chunking
   - Markdown files use markdown-aware chunking
   - HTML files use HTML-aware chunking
   - The chunker factory selects the best chunker based on file type
3. Chunks are embedded into vectors
4. Vectors are stored in the vector store
5. Queries are processed through the same pipeline
6. Relevant chunks are retrieved
7. LLM generates responses using retrieved context
8. Responses are post-processed and returned

## Configuration

The system uses a Settings class for configuration management, allowing for flexible deployment in different environments.

## Dependencies

The project uses `uv` for package and project management, with dependencies defined in `pyproject.toml`. 