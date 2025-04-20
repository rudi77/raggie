"""Main CLI module for the RAG system."""

import os
from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from langchain.schema import Document

from rag.core.config import Settings
from rag.ingestion.document_loader import DocumentLoader
from rag.store.chroma_store import ChromaStore
from rag.embedding.embeddings import EmbeddingModel
from rag.llm.llm_client import LLMClient

app = typer.Typer(help="RAG System CLI")
console = Console()

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to document or directory to ingest"),
    chunk_size: int = typer.Option(1000, "--chunk-size", "-c", help="Size of text chunks"),
    chunk_overlap: int = typer.Option(200, "--chunk-overlap", "-o", help="Overlap between chunks")
):
    """Ingest documents into the RAG system."""
    try:
        # Initialize components
        store = ChromaStore()
        embedding_model = EmbeddingModel()
        document_loader = DocumentLoader()

        # Load and process documents
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading documents...", total=None)
            documents = document_loader.load_documents(path)
            progress.update(task, completed=True)

            task = progress.add_task("Chunking documents...", total=len(documents))
            chunks = []
            for doc in documents:
                doc_chunks = document_loader.chunk_document(doc, chunk_size, chunk_overlap)
                chunks.extend(doc_chunks)
                progress.advance(task)

            task = progress.add_task("Generating embeddings...", total=len(chunks))
            vectors = []
            for chunk in chunks:
                vector = embedding_model.embed_text(chunk.page_content)
                vectors.append(vector)
                progress.advance(task)

            task = progress.add_task("Storing vectors...", total=len(chunks))
            for chunk, vector in zip(chunks, vectors):
                doc_id = f"{chunk.metadata.get('source', 'unknown')}_{len(vectors)}"
                store.store_vector(doc_id, vector, chunk.page_content, chunk.metadata)
                progress.advance(task)

        console.print(f"[green]Successfully ingested {len(documents)} documents![/green]")
    except Exception as e:
        console.print(f"[red]Error during ingestion: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def query(
    text: str = typer.Argument(..., help="Query text"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of results to return"),
    model: str = typer.Option("gpt-4o-mini", "--model", "-m", help="LLM model to use")
):
    """Query the RAG system."""
    try:
        # Initialize components
        store = ChromaStore()
        embedding_model = EmbeddingModel()
        llm_client = LLMClient(model_name=model)

        # Convert query to vector
        query_vector = embedding_model.embed_text(text)

        # Search for similar vectors
        results = store.search_vectors(query_vector, top_k=top_k)

        if not results:
            console.print("[yellow]No relevant documents found.[/yellow]")
            return

        # Convert results to Langchain Documents
        context_docs = []
        for result in results:
            doc = Document(
                page_content=result["content"],
                metadata=result["metadata"]
            )
            context_docs.append(doc)

        # Generate answer using LLM
        response = llm_client.generate_answer(text, context_docs)

        # Display results
        console.print("\n[bold]Answer:[/bold]")
        console.print(Markdown(response["answer"]))
        
        console.print("\n[bold]Sources:[/bold]")
        for source in response["sources"]:
            console.print(f"- {source}")

    except Exception as e:
        console.print(f"[red]Error during query: {str(e)}[/red]")
        raise typer.Exit(1)

@app.command()
def clear(
    force: bool = typer.Option(False, "--force", "-f", help="Force deletion without confirmation"),
):
    """Clear all documents from the RAG system."""
    settings = get_settings()
    
    if not force:
        confirm = typer.confirm("Are you sure you want to clear all documents? This cannot be undone.")
        if not confirm:
            console.print("Operation cancelled.")
            raise typer.Exit()
    
    try:
        store = ChromaStore(settings.chroma_db_path)
        store.clear()
        console.print(Panel("✅ All documents cleared successfully!", style="green"))
    except Exception as e:
        console.print(Panel(f"❌ Error: {str(e)}", style="red"))
        raise typer.Exit(1)
    finally:
        store.close()

if __name__ == "__main__":
    app() 