"""CSV formatter for SQL query results."""
import csv
import io
import logging
from typing import Any, Dict, List, Optional, Union

from ..core.exceptions import FormattingError
from .base import BaseFormatter

logger = logging.getLogger(__name__)


class CSVFormatter(BaseFormatter):
    """Formatter for CSV output."""

    def __init__(self, delimiter: str = ",", quotechar: str = '"', 
                 quoting: int = csv.QUOTE_MINIMAL, lineterminator: str = "\n"):
        """Initialize the CSV formatter.
        
        Args:
            delimiter: Field delimiter.
            quotechar: Character used for quoting fields.
            quoting: Quoting mode (csv.QUOTE_* constants).
            lineterminator: Line terminator.
        """
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.quoting = quoting
        self.lineterminator = lineterminator

    async def format(self, result: Any) -> str:
        """Format the query result as CSV.
        
        Args:
            result: The query result to format.
            
        Returns:
            The formatted result as a CSV string.
            
        Raises:
            FormattingError: If formatting fails.
        """
        try:
            if result is None:
                return ""
                
            # Convert to a list of dictionaries if needed
            rows = self._prepare_rows(result)
            if not rows:
                return ""
                
            # Write to a string buffer
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                fieldnames=rows[0].keys(),
                delimiter=self.delimiter,
                quotechar=self.quotechar,
                quoting=self.quoting,
                lineterminator=self.lineterminator
            )
            
            # Write header and rows
            writer.writeheader()
            writer.writerows(rows)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error formatting result as CSV: {str(e)}")
            raise FormattingError(f"Failed to format result as CSV: {str(e)}")

    async def format_error(self, error: Exception) -> str:
        """Format an error message as CSV.
        
        Args:
            error: The error to format.
            
        Returns:
            The formatted error message as a CSV string.
        """
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            quoting=self.quoting,
            lineterminator=self.lineterminator
        )
        
        writer.writerow(["error", "message", "type"])
        writer.writerow([True, str(error), error.__class__.__name__])
        
        return output.getvalue()

    def _prepare_rows(self, result: Any) -> List[Dict[str, Any]]:
        """Prepare rows for CSV formatting.
        
        Args:
            result: The result to prepare.
            
        Returns:
            A list of dictionaries representing rows.
        """
        if isinstance(result, dict):
            # Single row
            return [result]
        elif isinstance(result, list):
            if not result:
                return []
            elif all(isinstance(item, dict) for item in result):
                # List of dictionaries
                return result
            else:
                # List of non-dictionary items
                return [{"value": item} for item in result]
        else:
            # Single value
            return [{"value": result}] 