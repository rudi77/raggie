from typing import List, Dict, Any
from ..core.interfaces import IVectorStore
from ..core.models import Vector
import numpy as np

class BaseVectorStore(IVectorStore):
    """Base class for vector storage implementations."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
    
    def store(self, vector: Vector) -> None:
        """Store a vector in the database."""
        raise NotImplementedError("Subclasses must implement store()")
    
    def search(self, query_vector: Vector, limit: int = 5) -> List[Vector]:
        """Search for similar vectors."""
        raise NotImplementedError("Subclasses must implement search()")
    
    def _calculate_similarity(self, vec1: Vector, vec2: Vector) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1.values)
        v2 = np.array(vec2.values)
        
        # Normalize vectors
        v1_norm = v1 / np.linalg.norm(v1)
        v2_norm = v2 / np.linalg.norm(v2)
        
        # Calculate cosine similarity
        return float(np.dot(v1_norm, v2_norm)) 