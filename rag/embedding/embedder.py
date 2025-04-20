from typing import Dict, Any
from ..core.interfaces import IEmbedder
from ..core.models import Vector
import uuid

class BaseEmbedder(IEmbedder):
    """Base class for embedding generators."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def embed(self, text: str, metadata: Dict[str, Any]) -> Vector:
        """Generate embeddings for text."""
        raise NotImplementedError("Subclasses must implement embed()")
    
    def _create_vector(self, values: list[float], metadata: Dict[str, Any]) -> Vector:
        """Create a new vector with metadata."""
        return Vector(
            id=str(uuid.uuid4()),
            values=values,
            metadata={
                **metadata,
                "model_name": self.model_name,
                "embedding_dim": len(values)
            }
        ) 