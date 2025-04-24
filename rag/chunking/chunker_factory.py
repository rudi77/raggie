from typing import Dict, Type, Optional
from .chunker import BaseChunker
from .token_chunker import TokenChunker
from .recursive_character_chunker import RecursiveCharacterChunker
from .markdown_chunker import MarkdownChunker
from .html_chunker import HTMLChunker

class ChunkerFactory:
    """Factory for creating chunkers based on document type."""
    
    # Registry of chunkers by name
    _chunkers: Dict[str, Type[BaseChunker]] = {
        "token": TokenChunker,
        "recursive": RecursiveCharacterChunker,
        "markdown": MarkdownChunker,
        "html": HTMLChunker
    }
    
    @classmethod
    def get_chunker(cls, chunker_type: str, **kwargs) -> BaseChunker:
        """
        Get a chunker instance based on the specified type.
        
        Args:
            chunker_type: Type of chunker to create
            **kwargs: Additional arguments to pass to the chunker constructor
            
        Returns:
            An instance of the requested chunker
            
        Raises:
            ValueError: If the chunker type is not supported
        """
        if chunker_type not in cls._chunkers:
            raise ValueError(f"Unsupported chunker type: {chunker_type}. "
                            f"Supported types: {', '.join(cls._chunkers.keys())}")
        
        chunker_class = cls._chunkers[chunker_type]
        return chunker_class(**kwargs)
    
    @classmethod
    def get_chunker_for_file(cls, file_path: str, **kwargs) -> BaseChunker:
        """
        Get an appropriate chunker based on the file extension.
        
        Args:
            file_path: Path to the file
            **kwargs: Additional arguments to pass to the chunker constructor
            
        Returns:
            An instance of the appropriate chunker
        """
        # Extract file extension
        extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
        
        # Map extensions to chunker types
        extension_map = {
            'md': 'markdown',
            'markdown': 'markdown',
            'html': 'html',
            'htm': 'html',
            'txt': 'recursive',
            'pdf': 'recursive',
            'doc': 'recursive',
            'docx': 'recursive'
        }
        
        # Get the appropriate chunker type
        chunker_type = extension_map.get(extension, 'recursive')
        
        # Create and return the chunker
        return cls.get_chunker(chunker_type, **kwargs)
    
    @classmethod
    def register_chunker(cls, name: str, chunker_class: Type[BaseChunker]) -> None:
        """
        Register a new chunker type.
        
        Args:
            name: Name of the chunker type
            chunker_class: Class of the chunker
        """
        cls._chunkers[name] = chunker_class 