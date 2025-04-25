"""JSON formatter for SQL query results."""
import json
import logging
from typing import Any, Dict, List, Optional, Union

from ..core.exceptions import FormattingError
from .base import BaseFormatter

logger = logging.getLogger(__name__)


class JSONFormatter(BaseFormatter):
    """Formatter for JSON output."""

    def __init__(self, indent: int = 2, ensure_ascii: bool = False):
        """Initialize the JSON formatter.
        
        Args:
            indent: Number of spaces for indentation.
            ensure_ascii: Whether to ensure ASCII-only output.
        """
        self.indent = indent
        self.ensure_ascii = ensure_ascii

    async def format(self, result: Any) -> str:
        """Format the query result as JSON.
        
        Args:
            result: The query result to format.
            
        Returns:
            The formatted result as a JSON string.
            
        Raises:
            FormattingError: If formatting fails.
        """
        try:
            # Handle None and empty lists
            if result is None:
                return json.dumps(
                    {"result": None},
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii
                )
            elif result == []:
                return json.dumps(
                    {"result": []},
                    indent=self.indent,
                    ensure_ascii=self.ensure_ascii
                )
            
            # Convert result to a serializable format
            serializable_result = self._make_serializable(result)
            
            # Format as JSON
            return json.dumps(
                serializable_result,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii
            )
            
        except Exception as e:
            logger.error(f"Error formatting result as JSON: {str(e)}")
            raise FormattingError(f"Failed to format result as JSON: {str(e)}")

    async def format_error(self, error: Exception) -> str:
        """Format an error message as JSON.
        
        Args:
            error: The error to format.
            
        Returns:
            The formatted error message as a JSON string.
        """
        error_dict = {
            "error": str(error),
            "type": error.__class__.__name__
        }
        
        return json.dumps(
            error_dict,
            indent=self.indent,
            ensure_ascii=self.ensure_ascii
        )

    def _make_serializable(self, obj: Any) -> Any:
        """Convert an object to a JSON-serializable format.
        
        Args:
            obj: The object to convert.
            
        Returns:
            A JSON-serializable version of the object.
        """
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {str(k): self._make_serializable(v) for k, v in obj.items()}
        else:
            # Try to convert to a string representation
            return str(obj) 