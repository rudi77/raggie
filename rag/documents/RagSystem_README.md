Nachgedacht für ein paar Sekunden


Below is a README-style overview you can drop into your project’s `README.md`. It walks through the RAG system’s architecture, core components, and high-level data flows.

---

## Retrieval-Augmented Generation (RAG) System

A modular Python framework for building a retrieval-augmented generation pipeline:

* **Ingest** documents of various formats (PDF, Markdown, text), optionally performing OCR and image description.
* **Chunk** large documents into manageable pieces via pluggable strategies (page-wise, header-based, token- or character-based).
* **Embed** each chunk into a high-dimensional vector using OpenAI or sentence-transformers.
* **Store** embeddings and metadata in a ChromaDB vector store.
* **Retrieve** the top-k most similar chunks at query time.
* **Generate** an answer with context using an LLM (e.g. OpenAI Chat models).

---

### 📦 Project Structure

```
rag/  
├─ core/  
│  ├─ config.py            # Settings via Pydantic  
│  ├─ interfaces.py        # Abstract contracts (IParser, IChunker, IEmbedder…)  
│  └─ models.py            # Document, Chunk, Vector, Prompt, Response, FinalAnswer  
│  
├─ ingestion/  
│  ├─ document_loader.py   # Orchestrates loading and chunking via ChunkerFactory  
│  ├─ advanced_pdf_loader.py  # Extracts text, tables, images + optional VisionModel  
│  ├─ markdown_parser.py    # Converts raw markdown → Document  
│  └─ ocr.py                # Azure Document Intelligence OCR processor  
│  
├─ chunking/  
│  ├─ chunker.py           # BaseChunker, helper to assemble Chunk objects  
│  ├─ token_chunker.py     # Fixed-size token/character splits  
│  ├─ recursive_character_chunker.py  
│  ├─ markdown_chunker.py  
│  ├─ html_chunker.py  
│  ├─ page_wise_chunker.py  
│  └─ chunker_factory.py   # Picks chunker by file extension or type  
│  
├─ embedding/  
│  ├─ embedder.py          # BaseEmbedder, common vector wrapper logic  
│  ├─ text_embedder.py     # sentence-transformers implementation  
│  └─ embeddings.py        # LangChain OpenAIEmbeddings wrapper  
│  
├─ store/  
│  ├─ vector_store.py      # BaseVectorStore interface, similarity helper  
│  └─ chroma_store.py      # ChromaDB-backed persistence & search  
│  
├─ llm/  
│  ├─ llm_client.py        # Wraps ChatOpenAI; builds prompts with retrieved chunks  
│  └─ vision_model.py      # Uses GPT-4 Vision (litellm) to describe images  
│  
└─ cli/  
   └─ main.py              # Typer-based CLI: `ingest`, `query`, `clear`, `chunks`  
```

---

### 🔍 High-Level Data Flow

1. **Ingestion**

   * CLI → `DocumentLoader.load_documents(path)`
   * File-type loaders produce LangChain Documents (text + metadata).
   * Each Document is converted to a `core.models.Document` and passed to a chunker.

2. **Chunking**

   * `ChunkerFactory.get_chunker_for_file(...)` picks the right strategy.
   * Chunks carry `id`, `document_id`, content, and metadata (`start_index`, headers, page no., etc.).

3. **Embedding & Storage**

   * Each chunk’s text is embedded via `EmbeddingModel` (OpenAI) or `TextEmbedder`.
   * Resulting vector + metadata stored in ChromaDB (`ChromaStore`).

4. **Querying**

   * CLI → `LLMClient`
   * Query text → embedding → ChromaDB top-k vector search → retrieve chunk texts.
   * Build a contextual prompt and call ChatOpenAI → answer + cited sources.

---

### 🔧 Configuration

All settings (API keys, database paths, OCR credentials, logging) live in `core/config.py` and can be overridden via environment variables or a `.env` file.

---

### 🚀 Quickstart

```bash
# Install dependencies
pip install -r requirements.txt  

# Ingest a folder of PDFs
rag.exe ingest ./data --chunk-size 1200 --chunk-overlap 200

# Ask a question
rag.exe query "What is retrieval-augmented generation?" -k 3 -m gpt-o4-mini

# List chunks for a document
rag.exe chunks myfile.pdf --top-k 5

# Wipe all stored vectors
rag.exe clear --force
```

This architecture keeps each concern isolated, making it easy to:

* Swap in new chunking strategies or embedding models
* Replace ChromaDB with another vector store
* Extend to additional file formats or vision/OCR back-ends


