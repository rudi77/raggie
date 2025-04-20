from typing import Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from .embedder import BaseEmbedder
from ..core.models import Vector

class TextEmbedder(BaseEmbedder):
    """Text embedding generator using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(model_name)
        self.model = SentenceTransformer(model_name)
    
    def embed(self, text: str, metadata: Dict[str, Any]) -> Vector:
        """Generate embeddings for text using sentence-transformers."""
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Convert to list for storage
        embedding_list = embedding.tolist()
        
        # Create vector with metadata
        return self._create_vector(
            values=embedding_list,
            metadata={
                **metadata,
                "text_length": len(text),
                "embedding_type": "text"
            }
        ) 