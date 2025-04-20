from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import Document, Chunk, Vector, Prompt, Response, FinalAnswer

class IParser(ABC):
    """Interface for document parsers."""
    
    @abstractmethod
    def parse(self, content: str, metadata: Dict[str, Any]) -> Document:
        """Parse content into a Document object."""
        pass

class IChunker(ABC):
    """Interface for text chunking strategies."""
    
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        """Split a document into chunks."""
        pass

class IVectorStore(ABC):
    """Interface for vector storage implementations."""
    
    @abstractmethod
    def store(self, vector: Vector) -> None:
        """Store a vector in the database."""
        pass
    
    @abstractmethod
    def search(self, query_vector: Vector, limit: int = 5) -> List[Vector]:
        """Search for similar vectors."""
        pass

class IRetriever(ABC):
    """Interface for document retrieval."""
    
    @abstractmethod
    def retrieve(self, query: str, limit: int = 5) -> List[Chunk]:
        """Retrieve relevant chunks for a query."""
        pass

class IPromptBuilder(ABC):
    """Interface for prompt construction."""
    
    @abstractmethod
    def build(self, query: str, context: List[Chunk]) -> Prompt:
        """Build a prompt from query and context."""
        pass

class ILLMClient(ABC):
    """Interface for LLM interactions."""
    
    @abstractmethod
    def generate(self, prompt: Prompt) -> Response:
        """Generate a response from the LLM."""
        pass

class IPostProcessor(ABC):
    """Interface for response post-processing."""
    
    @abstractmethod
    def process(self, response: Response) -> FinalAnswer:
        """Process and format the LLM response."""
        pass

class IDocumentLoader(ABC):
    """Interface for document loading implementations."""
    
    @abstractmethod
    def load(self, path: str) -> List[Document]:
        """Load documents from a path."""
        pass

class IEmbedder(ABC):
    """Interface for embedding implementations."""
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Embed a text into a vector."""
        pass 