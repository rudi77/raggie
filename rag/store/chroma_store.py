from typing import List, Dict, Any, Optional
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from .vector_store import BaseVectorStore
from ..core.models import Vector

class ChromaStore(BaseVectorStore):
    """ChromaDB-based vector storage implementation."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        super().__init__("rag_documents")
        
        # Set default persist directory if none provided
        if persist_directory is None:
            # Use a default directory in the current working directory
            persist_directory = os.path.join(os.getcwd(), "data", "chroma")
            # Ensure directory exists
            os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=persist_directory,
                is_persistent=True,
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection("rag_documents")
    
    def store(self, vectors: List[List[float]], ids: List[str], metadatas: List[Dict[str, Any]] = None) -> None:
        """Store vectors in ChromaDB."""
        # Use upsert=True to update existing vectors with the same ID
        self.collection.upsert(
            embeddings=vectors,
            ids=ids,
            metadatas=metadatas
        )
    
    def search(self, query_vector: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors in ChromaDB."""
        # Perform similarity search
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            include=["embeddings", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "embedding": results.get("embeddings", [[]])[0][i] if results.get("embeddings") else None,
                    "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else None,
                    "distance": results.get("distances", [[]])[0][i] if results.get("distances") else None
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def close(self):
        """Close the ChromaDB client."""
        # ChromaDB doesn't have a direct cleanup method
        # We can just set references to None to allow garbage collection
        if hasattr(self, "collection"):
            self.collection = None
        if hasattr(self, "client"):
            self.client = None

    def store_vectors(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
        documents: List[str],
    ) -> None:
        """Store vectors in the collection."""
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def store_vector(
        self,
        id: str,
        vector: List[float],
        content: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Store a single vector in the collection."""
        self.collection.add(
            ids=[id],
            embeddings=[vector],
            metadatas=[metadata],
            documents=[content],
        )

    def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "content": results.get("documents", [[]])[0][i] if results.get("documents") else "",
                    "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                    "distance": results.get("distances", [[]])[0][i] if results.get("distances") else None
                }
                formatted_results.append(result)
        
        return formatted_results

    def clear(self) -> None:
        """Clear all vectors from the collection."""
        self.collection.delete() 