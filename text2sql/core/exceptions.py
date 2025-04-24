"""Custom exceptions for the Text2SQL component."""
from typing import Optional


class Text2SQLError(Exception):
    """Base exception for all Text2SQL errors."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class SchemaError(Text2SQLError):
    """Raised when there are issues with database schema operations."""
    pass


class ConnectionError(Text2SQLError):
    """Raised when database connection fails."""
    pass


class QueryGenerationError(Text2SQLError):
    """Raised when LLM fails to generate a valid SQL query."""
    pass


class QueryExecutionError(Text2SQLError):
    """Raised when SQL query execution fails."""
    pass


class ValidationError(Text2SQLError):
    """Raised when input validation fails."""
    pass


class ConfigurationError(Text2SQLError):
    """Raised when there are configuration issues."""
    pass


class FormattingError(Text2SQLError):
    """Raised when result formatting fails."""
    pass 