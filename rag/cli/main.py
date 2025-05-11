"""Main CLI module for the RAG system."""

import os
from pathlib import Path
from typing import Optional, List
import uuid

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
            console.print(f"[blue]Found {len(documents)} documents to process[/blue]")

            task = progress.add_task("Chunking documents...", total=len(documents))
            chunks = []
            for i, doc in enumerate(documents, 1):
                doc_chunks = document_loader.chunk_document(doc, chunk_size, chunk_overlap)
                chunks.extend(doc_chunks)
                console.print(f"[blue]Document {i}/{len(documents)}: Created {len(doc_chunks)} chunks[/blue]")
                progress.advance(task)

            console.print(f"[blue]Total chunks created: {len(chunks)}[/blue]")
            console.print(f"[blue]Average chunks per document: {len(chunks)/len(documents):.1f}[/blue]")

            task = progress.add_task("Generating embeddings...", total=len(chunks))
            vectors = []
            for chunk in chunks:
                vector = embedding_model.embed_text(chunk.page_content)
                vectors.append(vector)
                progress.advance(task)

            task = progress.add_task("Storing vectors...", total=len(chunks))
            for chunk, vector in zip(chunks, vectors):
                doc_id = str(uuid.uuid4())
                store.store_vector(
                    id=doc_id,
                    vector=vector,
                    content=chunk.page_content,
                    metadata=chunk.metadata)
                
                progress.advance(task)

        console.print(f"[green]Successfully ingested {len(documents)} documents![/green]")
        console.print(f"[green]Total chunks processed: {len(chunks)}[/green]")
        console.print(f"[green]Average chunk size: {sum(len(c.page_content) for c in chunks)/len(chunks):.0f} characters[/green]")
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

@app.command()
def chunks(
    document_name: str = typer.Argument(..., help="Name of the document to show chunks for"),
    top_k: Optional[int] = typer.Option(None, "--top-k", "-k", help="Number of chunks to show (default: all chunks)")
):
    """Show chunks for a specific document."""
    try:
        # Initialize components
        store = ChromaStore()
        
        # Search for chunks from the specified document
        results = store.search_by_source(document_name, top_k=top_k)
        
        if not results:
            console.print(f"[yellow]No chunks found for document: {document_name}[/yellow]")
            return
        
        # Display chunks
        console.print(f"\n[bold]Chunks for document: {document_name}[/bold]")
        console.print(f"Found {len(results)} chunks\n")
        
        for i, result in enumerate(results, 1):
            # Create a panel for each chunk
            chunk_panel = Panel(
                f"[bold]Chunk {i}[/bold]\n\n{result['content']}\n\n"
                f"[dim]Page: {result['metadata'].get('page_number', 'N/A')}[/dim]",
                title=f"Chunk {i}",
                border_style="blue"
            )
            console.print(chunk_panel)
            console.print()  # Add spacing between chunks
            
    except Exception as e:
        console.print(f"[red]Error retrieving chunks: {str(e)}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 