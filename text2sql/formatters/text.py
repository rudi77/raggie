"""Text formatter for SQL query results."""
import logging
from typing import Any, Dict, List, Optional, Union

from ..core.exceptions import FormattingError
from .base import BaseFormatter

logger = logging.getLogger(__name__)


class TextFormatter(BaseFormatter):
    """Formatter for human-readable text output."""

    def __init__(self, max_width: int = 80, truncate: bool = True):
        """Initialize the text formatter.
        
        Args:
            max_width: Maximum width for text output.
            truncate: Whether to truncate long values.
        """
        self.max_width = max_width
        self.truncate = truncate

    async def format(self, result: Any) -> str:
        """Format the query result as readable text.
        
        Args:
            result: The query result to format.
            
        Returns:
            The formatted result as a string.
            
        Raises:
            FormattingError: If formatting fails.
        """
        try:
            if result is None:
                return "No results returned."
                
            if isinstance(result, list):
                return self._format_list(result)
            elif isinstance(result, dict):
                return self._format_dict(result)
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error formatting result: {str(e)}")
            raise FormattingError(f"Failed to format result: {str(e)}")

    async def format_error(self, error: Exception) -> str:
        """Format an error message as readable text.
        
        Args:
            error: The error to format.
            
        Returns:
            The formatted error message as a string.
        """
        return f"Error: {str(error)}"

    def _format_list(self, result_list: List[Any]) -> str:
        """Format a list of results.
        
        Args:
            result_list: The list of results to format.
            
        Returns:
            The formatted list as a string.
        """
        if not result_list:
            return "No results returned."
            
        # Check if all items are dictionaries with the same keys
        if all(isinstance(item, dict) for item in result_list):
            # Format as a table
            return self._format_table(result_list)
        else:
            # Format as a simple list
            return "\n".join([str(item) for item in result_list])

    def _format_dict(self, result_dict: Dict[str, Any]) -> str:
        """Format a dictionary result.
        
        Args:
            result_dict: The dictionary to format.
            
        Returns:
            The formatted dictionary as a string.
        """
        if not result_dict:
            return "No results returned."
            
        lines = []
        for key, value in result_dict.items():
            if self.truncate and isinstance(value, str) and len(value) > self.max_width:
                value = value[:self.max_width - 3] + "..."
            lines.append(f"{key}: {value}")
            
        return "\n".join(lines)

    def _format_table(self, rows: List[Dict[str, Any]]) -> str:
        """Format a list of dictionaries as a table.
        
        Args:
            rows: The rows to format as a table.
            
        Returns:
            The formatted table as a string.
        """
        if not rows:
            return "No results returned."
            
        # Get all unique keys
        keys = set()
        for row in rows:
            keys.update(row.keys())
        keys = sorted(list(keys))
        
        # Calculate column widths
        widths = {key: len(str(key)) for key in keys}
        for row in rows:
            for key in keys:
                value = str(row.get(key, ""))
                if self.truncate and len(value) > self.max_width:
                    value = value[:self.max_width - 3] + "..."
                widths[key] = max(widths[key], len(value))
        
        # Create header
        header = " | ".join(key.ljust(widths[key]) for key in keys)
        separator = "-+-".join("-" * widths[key] for key in keys)
        
        # Create rows
        formatted_rows = []
        for row in rows:
            formatted_row = " | ".join(
                str(row.get(key, "")).ljust(widths[key])[:widths[key]]
                for key in keys
            )
            formatted_rows.append(formatted_row)
        
        # Combine all parts
        return "\n".join([header, separator] + formatted_rows) 