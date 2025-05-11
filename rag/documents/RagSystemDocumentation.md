## RAG System Documentation

This document provides an in-depth overview of the RAG (Retrieval-Augmented Generation) system, including its architecture, modules, key classes, and usage patterns. The system is organized into several packages: `core`, `chunking`, `ingestion`, `embedding`, `store`, `llm`, and `cli`.

---

### Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)

   * `core.models`
   * `core.interfaces`
   * `core.config`
3. [Document Ingestion](#document-ingestion)

   * `ingestion.file_parser`
   * `ingestion.markdown_parser`
   * `ingestion.ocr`
   * `ingestion.document_loader`
   * `ingestion.advanced_pdf_loader`
4. [Chunking Strategies](#chunking-strategies)

   * `chunking.BaseChunker`
   * `chunking.TokenChunker`
   * `chunking.RecursiveCharacterChunker`
   * `chunking.MarkdownChunker`
   * `chunking.HTMLChunker`
   * `chunking.PageWiseChunker`
   * `chunking.ChunkerFactory`
5. [Embedding Generation](#embedding-generation)

   * `embedding.BaseEmbedder`
   * `embedding.TextEmbedder`
   * `embedding.EmbeddingModel`
6. [Vector Store](#vector-store)

   * `store.BaseVectorStore`
   * `store.ChromaStore`
7. [LLM Client and Vision](#llm-client-and-vision)

   * `llm.llm_client.LLMClient`
   * `llm.vision_model.VisionModel`
8. [Command-Line Interface (CLI)](#command-line-interface-cli)

   * `cli.main`
9. [Configuration and Settings](#configuration-and-settings)
10. [Usage Examples](#usage-examples)

---

## Overview

The RAG system integrates document ingestion, chunking, embedding, storage, and retrieval to answer user queries with context-driven responses from large language models (LLMs). Key steps:

1. **Ingestion**: Load documents of various formats (PDF, Markdown, text) and parse content.
2. **Chunking**: Split large documents into manageable chunks for indexing.
3. **Embedding**: Convert text chunks into vector embeddings.
4. **Storage**: Store and index embeddings in a vector database (ChromaDB).
5. **Retrieval & Generation**: Given a query, embed it, retrieve similar chunks, and generate an answer using an LLM.

---

## Core Components

### core.models

Defines data classes used across the system:

* **Document**: Represents a source document with `id`, `content`, `metadata`, timestamps, and `source`.
* **Chunk**: Represents a text chunk with `id`, `document_id`, `content`, and `metadata`.
* **Vector**: Holds embedding vectors and metadata.
* **Prompt**, **Response**, **FinalAnswer**: Facilitate prompt construction and LLM responses.

### core.interfaces

Abstract interfaces defining contracts for:

* Parsers (`IParser`), Chunkers (`IChunker`), Vector Stores (`IVectorStore`), Retrievers, Prompt Builders, LLM Clients, Post-Processors, Document Loaders, Embedders, OCR Processors.

### core.config

Application configuration via Pydantic `BaseSettings`:

* `openai_api_key`, paths for ChromaDB and SQL database, logging settings, Azure OCR credentials.

---

## Document Ingestion

### ingestion.file\_parser

* **BaseFileParser**: Abstract base for file parsers; enforces `supported_extensions`.
* **ParserRegistry**: Registers and retrieves parsers by file extension.

### ingestion.markdown\_parser

* **MarkdownParser**: Converts Markdown to HTML (using `markdown` library), wraps into `core.models.Document`.

### ingestion.ocr

* **AzureOCRProcessor**: Uses Azure Document Intelligence to extract text from images/PDFs with retry logic and logging. Implements `IOCRProcessor`.

### ingestion.document\_loader

* **DocumentLoader**: Orchestrates loading of files:

  * Maps suffix to loader (PyPDFLoader, TextLoader, UnstructuredMarkdownLoader, or `AdvancedPDFLoader`).
  * `_load_single_file`: Returns LangChain Documents.
  * `chunk_document`: Uses `ChunkerFactory` to choose chunker, converts to `RagDocument`, and back to LangChain `Document` chunks.

### ingestion.advanced\_pdf\_loader

* **AdvancedPDFLoader**: Extends `BasePDFLoader` to extract text, tables (as Markdown), and images (base64 + descriptions via vision model).
* **Methods**: `_process_image`, `_process_table`, `lazy_load` yields page-wise Documents.

---

## Chunking Strategies

### chunking.BaseChunker

Abstract base for chunkers, handling `chunk_size` and `chunk_overlap`, and `_create_chunk` helper.

### chunking.TokenChunker

Splits by character count (approximate tokens) respecting word boundaries and overlap.

### chunking.RecursiveCharacterChunker

Uses LangChain's `RecursiveCharacterTextSplitter` with customizable separators and overlap.

* Tracks which separator created each chunk.

### chunking.MarkdownChunker

Uses LangChain's `MarkdownHeaderTextSplitter` to split at Markdown headers (`h1`, `h2`, etc.).

### chunking.HTMLChunker

Uses LangChain's `HTMLHeaderTextSplitter` to split at HTML header tags.

### chunking.PageWiseChunker

Splits by page boundaries based on metadata or common page markers (`\f`, `---`, etc.).

* Merges small pages below `min_page_size`.

### chunking.ChunkerFactory

* Maintains registry mapping names to chunker classes.
* `get_chunker`: Instantiate by type.
* `get_chunker_for_file`: Chooses chunker based on file extension, adjusts kwargs (`min_page_size`, removes unused parameters).
* `register_chunker`: Extendable.

---

## Embedding Generation

### embedding.BaseEmbedder

Abstract base for embedders, storing `model_name` and `_create_vector` helper.

### embedding.TextEmbedder

Wraps `sentence-transformers` to embed text into vectors.

### embedding.EmbeddingModel

Wraps LangChain's `OpenAIEmbeddings` for document/query embedding convenience.

---

## Vector Store

### store.BaseVectorStore

Defines `store(vector)` and `search(query_vector)` abstractly; includes cosine similarity helper.

### store.ChromaStore

Implements persistence with ChromaDB:

* `store_vectors`, `store_vector` for upsert/add.
* `search_vectors`, `search` for similarity queries.
* `search_by_source` to filter by document source.
* `clear` and `close` methods.

---

## LLM Client and Vision

### llm.llm\_client.LLMClient

* Initializes OpenAI chat models (`gpt-3.5-turbo` fallback).
* Holds a prompt template, formats context and question, invokes model via LangChain.
* `generate_answer` returns `{answer, sources}`.

### llm.vision\_model.VisionModel

* Wraps OpenAI's GPT-4 Vision via litellm to describe images.
* Converts PIL Images to base64, crafts system/user messages, calls `completion`, and parses output.
* `create_vision_model` helper.

---

## Command-Line Interface (CLI)

### cli.main

Defines Typer-based CLI with commands:

* `ingest`: Ingest path, chunk size/overlap. Loads documents, chunks, embeds, stores vectors.
* `query`: Query text, top K, model. Retrieves top chunks and generates answer.
* `clear`: Clears Chroma collection.
* `chunks`: Shows stored chunks for a document.

Uses Rich for console output, progress bars, and panels.

---

## Configuration and Settings

Controlled by `rag.core.config.Settings`:

* Environment variables via `.env`.
* Paths for ChromaDB, SQL DB.
* Azure OCR credentials.
* Logging level.

---

## Usage Examples

```powershell
# Ingest documents
rag.exe ingest ./data/**/*.pdf --chunk-size 1200 --chunk-overlap 300

# Query the knowledge base
rag.exe query "What is retrieval-augmented generation?" -k 3 -m gpt-o4-mini

# List chunks for a document
rag.exe chunks my_document.pdf --top-k 5

# Clear all stored vectors
rag.exe clear --force
```

