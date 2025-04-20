# Create main project directory
New-Item -ItemType Directory -Path "rag-system" -Force

# Create all subdirectories
$directories = @(
    "rag-system/rag",
    "rag-system/rag/core",
    "rag-system/rag/ingestion",
    "rag-system/rag/chunking",
    "rag-system/rag/embedding",
    "rag-system/rag/store",
    "rag-system/rag/retrieval",
    "rag-system/rag/prompt",
    "rag-system/rag/llm",
    "rag-system/rag/post",
    "rag-system/rag/cli",
    "rag-system/tests"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force
}

# Create all Python files
$pythonFiles = @(
    "rag-system/rag/__init__.py",
    "rag-system/rag/core/__init__.py",
    "rag-system/rag/core/models.py",
    "rag-system/rag/core/interfaces.py",
    "rag-system/rag/ingestion/__init__.py",
    "rag-system/rag/ingestion/file_parser.py",
    "rag-system/rag/ingestion/markdown_parser.py",
    "rag-system/rag/ingestion/pdf_parser.py",
    "rag-system/rag/chunking/__init__.py",
    "rag-system/rag/chunking/chunker.py",
    "rag-system/rag/chunking/token_chunker.py",
    "rag-system/rag/chunking/semantic_chunker.py",
    "rag-system/rag/chunking/layout_chunker.py",
    "rag-system/rag/embedding/__init__.py",
    "rag-system/rag/embedding/embedder.py",
    "rag-system/rag/embedding/text_embedder.py",
    "rag-system/rag/store/__init__.py",
    "rag-system/rag/store/vector_store.py",
    "rag-system/rag/store/chroma_store.py",
    "rag-system/rag/retrieval/__init__.py",
    "rag-system/rag/retrieval/retriever.py",
    "rag-system/rag/retrieval/semantic_retriever.py",
    "rag-system/rag/retrieval/hybrid_retriever.py",
    "rag-system/rag/prompt/__init__.py",
    "rag-system/rag/prompt/prompt_builder.py",
    "rag-system/rag/llm/__init__.py",
    "rag-system/rag/llm/llm_client.py",
    "rag-system/rag/llm/openai_client.py",
    "rag-system/rag/llm/local_client.py",
    "rag-system/rag/post/__init__.py",
    "rag-system/rag/post/post_processor.py",
    "rag-system/rag/cli/__init__.py",
    "rag-system/rag/cli/main.py"
)

foreach ($file in $pythonFiles) {
    New-Item -ItemType File -Path $file -Force
}

# Create test files
$testFiles = @(
    "rag-system/tests/test_models.py",
    "rag-system/tests/test_interfaces.py",
    "rag-system/tests/test_ingestion.py",
    "rag-system/tests/test_chunking.py",
    "rag-system/tests/test_embedding.py",
    "rag-system/tests/test_store.py",
    "rag-system/tests/test_retrieval.py",
    "rag-system/tests/test_prompt_builder.py",
    "rag-system/tests/test_llm_client.py",
    "rag-system/tests/test_post_processing.py",
    "rag-system/tests/test_cli.py"
)

foreach ($file in $testFiles) {
    New-Item -ItemType File -Path $file -Force
}

# Create project configuration files
New-Item -ItemType File -Path "rag-system/Dockerfile" -Force
New-Item -ItemType File -Path "rag-system/docker-compose.yml" -Force
New-Item -ItemType File -Path "rag-system/pyproject.toml" -Force
New-Item -ItemType File -Path "rag-system/README.md" -Force 