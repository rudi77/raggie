from typing import List

from langchain_openai import OpenAIEmbeddings

class EmbeddingModel:
    """Handles text embedding operations."""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        return self.embeddings.embed_query(text)
        
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        return self.embed_query(text) 