"""Core interfaces for the Text2SQL component."""
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from pydantic import BaseModel


class DatabaseSchema(BaseModel):
    """Represents a database schema with tables and their relationships."""
    tables: Dict[str, "TableSchema"]
    relationships: List["SchemaRelationship"]

class TableSchema(BaseModel):
    """Represents a database table schema."""
    name: str
    columns: Dict[str, "ColumnSchema"]
    primary_key: List[str]
    description: Optional[str] = None

class ColumnSchema(BaseModel):
    """Represents a database column schema."""
    name: str
    data_type: str
    is_nullable: bool
    description: Optional[str] = None
    foreign_key: Optional["ForeignKeyReference"] = None

class ForeignKeyReference(BaseModel):
    """Represents a foreign key reference."""
    table: str
    column: str

class SchemaRelationship(BaseModel):
    """Represents a relationship between tables."""
    from_table: str
    to_table: str
    type: str  # one_to_one, one_to_many, many_to_many
    through_table: Optional[str] = None  # For many_to_many relationships

class QueryResult(BaseModel):
    """Represents the result of a SQL query execution."""
    columns: List[str]
    rows: List[List[Any]]
    affected_rows: Optional[int] = None
    execution_time: float
    query: str

@runtime_checkable
class SchemaLoader(Protocol):
    """Protocol for loading database schemas."""
    async def load_schema(self, connection_string: str) -> DatabaseSchema:
        """Load the database schema from the given connection."""
        ...

    async def refresh_schema(self) -> DatabaseSchema:
        """Refresh the current schema."""
        ...

@runtime_checkable
class DatabaseConnector(Protocol):
    """Protocol for database connections and operations."""
    async def connect(self, connection_string: str) -> None:
        """Establish a database connection."""
        ...

    async def disconnect(self) -> None:
        """Close the database connection."""
        ...

    async def is_connected(self) -> bool:
        """Check if the database connection is active."""
        ...

    async def get_schema(self) -> DatabaseSchema:
        """Get the current database schema."""
        ...

@runtime_checkable
class QueryEngine(Protocol):
    """Protocol for natural language to SQL conversion."""
    async def generate_sql(self, 
                         natural_query: str, 
                         schema: DatabaseSchema,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """Convert natural language query to SQL."""
        ...

    async def validate_sql(self, sql_query: str, schema: DatabaseSchema) -> bool:
        """Validate if the SQL query is valid for the given schema."""
        ...

@runtime_checkable
class SQLExecutor(Protocol):
    """Protocol for SQL query execution."""
    async def execute_query(self, sql_query: str) -> QueryResult:
        """Execute a SQL query and return the results."""
        ...

    async def execute_batch(self, queries: List[str]) -> List[QueryResult]:
        """Execute multiple SQL queries in a batch."""
        ...

@runtime_checkable
class ResultFormatter(Protocol):
    """Protocol for formatting query results."""
    def format_result(self, 
                     result: QueryResult,
                     format_type: str = "text",
                     **kwargs: Any) -> str:
        """Format the query result in the specified format."""
        ...

    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats."""
        ... 