"""Markdown formatter module."""
from typing import Any, Optional

from .base import BaseFormatter


class MarkdownFormatter(BaseFormatter):
    """Formatter that outputs results as markdown."""
    
    def format(self, result: Any) -> str:
        """Format a result as markdown.
        
        Args:
            result: The result to format
            
        Returns:
            str: The formatted result as markdown
        """
        if result is None:
            return "## No Results\n\nNo results found."
            
        if isinstance(result, (list, tuple)):
            if not result:
                return "## No Results\n\nNo results found."
            return self._format_list(result)
            
        if isinstance(result, dict):
            return self._format_dict(result)
            
        return f"## Result\n\n{str(result)}"
        
    def format_error(self, error: Exception) -> str:
        """Format an error as markdown.
        
        Args:
            error: The error to format
            
        Returns:
            str: The formatted error as markdown
        """
        return f"## Error\n\n{str(error)}"
        
    def _format_list(self, items: list) -> str:
        """Format a list as markdown.
        
        Args:
            items: The list to format
            
        Returns:
            str: The formatted list as markdown
        """
        if not items:
            return "## No Results\n\nNo results found."
            
        if isinstance(items[0], dict):
            # Format as table
            headers = list(items[0].keys())
            header_row = "| " + " | ".join(headers) + " |"
            separator = "| " + " | ".join(["---"] * len(headers)) + " |"
            rows = []
            for item in items:
                row = "| " + " | ".join(str(item.get(h, "")) for h in headers) + " |"
                rows.append(row)
            return "## Results\n\n" + "\n".join([header_row, separator] + rows)
            
        # Format as bullet points
        return "## Results\n\n" + "\n".join(f"- {item}" for item in items)
        
    def _format_dict(self, data: dict) -> str:
        """Format a dictionary as markdown.
        
        Args:
            data: The dictionary to format
            
        Returns:
            str: The formatted dictionary as markdown
        """
        return "## Result\n\n" + "\n".join(f"**{k}**: {v}" for k, v in data.items()) 