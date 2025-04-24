"""Base formatter for SQL query results."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ..core.exceptions import FormattingError


class BaseFormatter(ABC):
    """Base class for all result formatters."""

    @abstractmethod
    async def format(self, result: Any) -> str:
        """Format the query result.
        
        Args:
            result: The query result to format.
            
        Returns:
            The formatted result as a string.
            
        Raises:
            FormattingError: If formatting fails.
        """
        pass

    @abstractmethod
    async def format_error(self, error: Exception) -> str:
        """Format an error message.
        
        Args:
            error: The error to format.
            
        Returns:
            The formatted error message as a string.
        """
        pass 