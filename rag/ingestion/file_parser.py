from typing import Dict, Any, Type
from ..core.interfaces import IParser
from ..core.models import Document
from datetime import datetime
import os

class BaseFileParser(IParser):
    """Base class for file parsers."""
    
    def __init__(self, supported_extensions: list[str]):
        self.supported_extensions = supported_extensions
    
    def can_parse(self, file_path: str) -> bool:
        """Check if the file can be parsed by this parser."""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self.supported_extensions
    
    def parse(self, content: str, metadata: Dict[str, Any]) -> Document:
        """Parse content into a Document object."""
        raise NotImplementedError("Subclasses must implement parse()")

class ParserRegistry:
    """Registry for file parsers."""
    
    def __init__(self):
        self._parsers: Dict[str, Type[BaseFileParser]] = {}
    
    def register(self, parser: Type[BaseFileParser]) -> None:
        """Register a new parser."""
        for ext in parser.supported_extensions:
            self._parsers[ext.lower()] = parser
    
    def get_parser(self, file_path: str) -> BaseFileParser:
        """Get the appropriate parser for a file."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self._parsers:
            raise ValueError(f"No parser registered for extension: {ext}")
        
        return self._parsers[ext]() 