# RAG System with Text2SQL

A comprehensive system combining Retrieval-Augmented Generation (RAG) for document processing and Text2SQL for natural language database queries.

## Components

### 1. RAG System
A simple and efficient Retrieval-Augmented Generation system for document ingestion and querying.

**Features:**
- Document ingestion with configurable chunking
- Vector-based semantic search
- CLI interface for easy interaction
- Support for multiple document types
- Efficient storage using ChromaDB

### 2. Text2SQL
A natural language to SQL query engine that allows users to query databases using plain language.

**Features:**
- Natural language to SQL query conversion
- Support for multiple database types (SQLite, PostgreSQL)
- Multiple output formats (Text, JSON, CSV)
- CLI interface for easy interaction
- Comprehensive test coverage
- Error handling and validation

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

### RAG System

#### Ingest Documents
```bash
# Ingest a single document
rag ingest path/to/document.pdf

# Ingest a directory recursively
rag ingest path/to/directory --recursive

# Customize chunk size and overlap
rag ingest path/to/document.pdf --chunk-size 1000 --chunk-overlap 200
```

#### Query Documents
```bash
# Search with default settings (5 results)
rag query "your search query"

# Specify number of results
rag query "your search query" --num-results 10
```

#### Clear Documents
```bash
# Clear all documents (with confirmation)
rag clear

# Force clear without confirmation
rag clear --force
```

### Text2SQL

#### Query Database
```bash
# Query using natural language
t2s query "Show me all transactions from last month"

# Get SQL explanation
t2s explain "What were the total sales by customer in 2024?"

# Check database status
t2s status

# Configure settings
t2s config
```

#### Output Formats
The system supports multiple output formats:
- Text (default): Human-readable format
- JSON: For API integration
- CSV: For data export

## Configuration

The system uses environment variables for configuration. Create a `.env` file in your project root:

```env
# RAG System Configuration
OPENAI_API_KEY=your_api_key_here
CHROMA_DB_PATH=path/to/your/chroma/db

# Text2SQL Configuration
DATABASE_URL=sqlite:///path/to/your/database.db
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific component tests
pytest rag/tests  # RAG system tests
pytest text2sql/tests  # Text2SQL tests
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

## Starting the Application

### Backend Service

To start the backend service, run the following command from the root directory:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

This will start the FastAPI server on http://localhost:8000.

### Frontend Service

To start the frontend service, navigate to the frontend directory and run:

```bash
cd frontend
npm install  # Only needed the first time or when dependencies change
npm run dev
```

This will start the Vite development server, typically on http://localhost:5173.

## Using the Text2SQL Query Interface

1. Start both the backend and frontend services as described above.
2. Open your browser and navigate to http://localhost:5173.
3. In the text area, enter your question in natural language (e.g., "Show me the total sales by product category").
4. Click the "Submit Query" button.
5. The application will display:
   - The SQL query that was generated
   - The results in a table format (if the results are tabular data)
   - A formatted text representation of the results

## API Endpoints

The backend provides the following endpoints:

- `POST /text2sql/query` - Converts a natural language question to SQL and executes it
- `POST /text2sql/explain` - Converts a natural language question to SQL without executing it
