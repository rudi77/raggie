"""Base implementations of core interfaces."""
from typing import Any, Dict, List, Optional
import time
import logging
from abc import ABC, abstractmethod

from .interfaces import (
    DatabaseSchema, QueryResult, SchemaLoader, DatabaseConnector,
    QueryEngine, SQLExecutor, ResultFormatter
)
from .exceptions import (
    SchemaError, ConnectionError, QueryGenerationError,
    QueryExecutionError, FormattingError
)

logger = logging.getLogger(__name__)


class BaseSchemaLoader(SchemaLoader, ABC):
    """Base implementation of SchemaLoader protocol."""
    
    def __init__(self) -> None:
        self._cached_schema: Optional[DatabaseSchema] = None
        self._last_refresh: float = 0
        self._cache_ttl: int = 3600  # 1 hour default

    @abstractmethod
    async def _fetch_schema(self, connection_string: str) -> DatabaseSchema:
        """Actual implementation of schema fetching logic."""
        pass

    async def load_schema(self, connection_string: str) -> DatabaseSchema:
        """Load the database schema from the given connection."""
        try:
            schema = await self._fetch_schema(connection_string)
            self._cached_schema = schema
            self._last_refresh = time.time()
            return schema
        except Exception as e:
            raise SchemaError(f"Failed to load schema: {str(e)}")

    async def refresh_schema(self) -> DatabaseSchema:
        """Refresh the current schema."""
        if not self._cached_schema:
            raise SchemaError("No schema loaded to refresh")
        return await self.load_schema(self._connection_string)


class BaseDatabaseConnector(DatabaseConnector, ABC):
    """Base implementation of DatabaseConnector protocol."""

    def __init__(self) -> None:
        self._connection = None
        self._schema_loader: Optional[SchemaLoader] = None
        self._connection_string: Optional[str] = None

    @abstractmethod
    async def _establish_connection(self, connection_string: str) -> Any:
        """Actual implementation of connection establishment."""
        pass

    @abstractmethod
    async def _close_connection(self) -> None:
        """Actual implementation of connection closing."""
        pass

    async def connect(self, connection_string: str) -> None:
        """Establish a database connection."""
        try:
            self._connection = await self._establish_connection(connection_string)
            self._connection_string = connection_string
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {str(e)}")

    async def disconnect(self) -> None:
        """Close the database connection."""
        if self._connection:
            try:
                await self._close_connection()
                self._connection = None
            except Exception as e:
                raise ConnectionError(f"Failed to disconnect: {str(e)}")

    async def is_connected(self) -> bool:
        """Check if the database connection is active."""
        return self._connection is not None

    async def get_schema(self) -> DatabaseSchema:
        """Get the current database schema."""
        if not self._schema_loader:
            raise SchemaError("No schema loader configured")
        return await self._schema_loader.load_schema(self._connection_string)


class BaseQueryEngine(QueryEngine):
    """Base implementation of QueryEngine protocol."""

    async def generate_sql(self,
                         natural_query: str,
                         schema: DatabaseSchema,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """Convert natural language query to SQL."""
        try:
            # Subclasses should implement the actual LLM-based conversion
            raise NotImplementedError("Subclasses must implement generate_sql")
        except Exception as e:
            raise QueryGenerationError(f"Failed to generate SQL: {str(e)}")

    async def validate_sql(self, sql_query: str, schema: DatabaseSchema) -> bool:
        """Validate if the SQL query is valid for the given schema."""
        try:
            # Subclasses should implement actual validation logic
            raise NotImplementedError("Subclasses must implement validate_sql")
        except Exception as e:
            raise QueryGenerationError(f"Failed to validate SQL: {str(e)}")


class BaseSQLExecutor(SQLExecutor):
    """Base implementation of SQLExecutor protocol."""

    def __init__(self, connector: DatabaseConnector):
        self._connector = connector

    async def execute_query(self, sql_query: str) -> QueryResult:
        """Execute a SQL query and return the results."""
        try:
            start_time = time.time()
            # Subclasses should implement actual query execution
            raise NotImplementedError("Subclasses must implement execute_query")
        except Exception as e:
            raise QueryExecutionError(f"Failed to execute query: {str(e)}")

    async def execute_batch(self, queries: List[str]) -> List[QueryResult]:
        """Execute multiple SQL queries in a batch."""
        results = []
        for query in queries:
            try:
                result = await self.execute_query(query)
                results.append(result)
            except QueryExecutionError as e:
                logger.error(f"Failed to execute query in batch: {str(e)}")
                results.append(QueryResult(
                    columns=[],
                    rows=[],
                    affected_rows=0,
                    execution_time=0,
                    query=query
                ))
        return results


class BaseResultFormatter(ResultFormatter):
    """Base implementation of ResultFormatter protocol."""

    def format_result(self,
                     result: QueryResult,
                     format_type: str = "text",
                     **kwargs: Any) -> str:
        """Format the query result in the specified format."""
        try:
            if format_type not in self.get_supported_formats():
                raise FormattingError(f"Unsupported format type: {format_type}")
            # Subclasses should implement actual formatting logic
            raise NotImplementedError("Subclasses must implement format_result")
        except Exception as e:
            raise FormattingError(f"Failed to format result: {str(e)}")

    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats."""
        return ["text", "json", "csv"]  # Base supported formats 