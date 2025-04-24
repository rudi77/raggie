from typing import Dict, Type, Optional
from .chunker import BaseChunker
from .token_chunker import TokenChunker
from .recursive_character_chunker import RecursiveCharacterChunker
from .markdown_chunker import MarkdownChunker
from .html_chunker import HTMLChunker
from .page_wise_chunker import PageWiseChunker

class ChunkerFactory:
    """Factory for creating chunkers based on document type."""
    
    # Registry of chunkers by name
    _chunkers: Dict[str, Type[BaseChunker]] = {
        "token": TokenChunker,
        "recursive": RecursiveCharacterChunker,
        "markdown": MarkdownChunker,
        "html": HTMLChunker,
        "page": PageWiseChunker
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
            'md': 'page',  # Use page-wise chunker for Markdown
            'markdown': 'page',  # Use page-wise chunker for Markdown
            'html': 'html',
            'htm': 'html',
            'pdf': 'page',  # Use page-wise chunker for PDFs
            'txt': 'recursive',
            'doc': 'recursive',
            'docx': 'recursive'
        }
        
        # Get the appropriate chunker type
        chunker_type = extension_map.get(extension, 'recursive')
        
        # Set file-type specific configurations
        if chunker_type == 'page':
            if extension in ['md', 'markdown']:
                # For Markdown, use a smaller min_page_size since sections tend to be smaller
                kwargs.setdefault('min_page_size', 50)
            else:  # PDF
                # For PDFs, use a larger min_page_size since pages tend to be larger
                kwargs.setdefault('min_page_size', 200)
            
            # Remove chunk_size and chunk_overlap for PageWiseChunker as it doesn't use them
            kwargs.pop('chunk_size', None)
            kwargs.pop('chunk_overlap', None)
        
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