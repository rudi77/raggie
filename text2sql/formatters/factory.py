"""Factory for creating formatters."""
from typing import Dict, Optional, Type

from ..core.exceptions import FormattingError
from .base import BaseFormatter
from .csv import CSVFormatter
from .json import JSONFormatter
from .text import TextFormatter


class FormatterFactory:
    """Factory for creating formatters."""

    # Registry of available formatters
    _formatters: Dict[str, Type[BaseFormatter]] = {
        "text": TextFormatter,
        "json": JSONFormatter,
        "csv": CSVFormatter
    }

    @classmethod
    def create(cls, format_type: str, **kwargs) -> BaseFormatter:
        """Create a formatter of the specified type.
        
        Args:
            format_type: The type of formatter to create.
            **kwargs: Additional arguments to pass to the formatter constructor.
            
        Returns:
            A formatter instance.
            
        Raises:
            FormattingError: If the formatter type is not supported.
        """
        formatter_class = cls._formatters.get(format_type.lower())
        if not formatter_class:
            raise FormattingError(f"Unsupported formatter type: {format_type}")
            
        return formatter_class(**kwargs)

    @classmethod
    def register(cls, name: str, formatter_class: Type[BaseFormatter]) -> None:
        """Register a new formatter type.
        
        Args:
            name: The name of the formatter type.
            formatter_class: The formatter class to register.
        """
        cls._formatters[name.lower()] = formatter_class

    @classmethod
    def get_available_formats(cls) -> list:
        """Get a list of available formatter types.
        
        Returns:
            A list of formatter type names.
        """
        return list(cls._formatters.keys()) 