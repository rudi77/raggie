"""SQLite implementations of database interfaces."""
import sqlite3
import aiosqlite
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from .base import BaseDatabaseConnector, BaseSchemaLoader, BaseSQLExecutor
from .interfaces import DatabaseSchema, QueryResult
from .schema import Column, Table
from .exceptions import SchemaError, ConnectionError, QueryExecutionError


class SQLiteSchemaLoader(BaseSchemaLoader):
    """Schema loader implementation for SQLite databases."""

    async def _fetch_schema(self, connection_string: str) -> DatabaseSchema:
        """Fetch schema from SQLite database."""
        path = self._parse_connection_string(connection_string)
        tables = []
        
        async with aiosqlite.connect(path) as conn:
            # Get all tables
            async with conn.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """
            ) as cursor:
                table_names = await cursor.fetchall()

            for (table_name,) in table_names:
                # Get table info
                async with conn.execute(f"PRAGMA table_info({table_name})") as cursor:
                    columns_info = await cursor.fetchall()
                
                # Get foreign keys
                async with conn.execute(f"PRAGMA foreign_key_list({table_name})") as cursor:
                    fk_info = await cursor.fetchall()

                # Process columns
                columns = []
                primary_keys = []
                foreign_keys = []
                
                # Create a mapping of foreign keys
                fk_map: Dict[str, Tuple[str, str]] = {
                    row[3]: (row[2], row[4])  # from_col: (table, to_col)
                    for row in fk_info
                }

                for col in columns_info:
                    # col: (cid, name, type, notnull, dflt_value, pk)
                    is_primary = bool(col[5])
                    col_name = col[1]
                    
                    if is_primary:
                        primary_keys.append(col_name)
                    
                    if col_name in fk_map:
                        foreign_keys.append(col_name)
                        ref_table, ref_col = fk_map[col_name]
                        references = f"{ref_table}.{ref_col}"
                    else:
                        references = None

                    columns.append(Column(
                        name=col_name,
                        data_type=col[2],
                        is_nullable=not bool(col[3]),
                        is_primary=is_primary,
                        is_foreign=col_name in fk_map,
                        references=references
                    ))

                # Get table description from sqlite_master
                async with conn.execute(
                    """
                    SELECT sql FROM sqlite_master 
                    WHERE type='table' AND name=?
                    """, (table_name,)
                ) as cursor:
                    create_sql = (await cursor.fetchone())[0]

                tables.append(Table(
                    name=table_name,
                    columns=columns,
                    primary_keys=primary_keys,
                    foreign_keys=foreign_keys,
                    description=create_sql
                ))

        # Build relationships
        relationships = []
        for table in tables:
            for column in table.columns:
                if column.references:
                    ref_table, ref_col = column.references.split('.')
                    relationships.append({
                        'from_table': table.name,
                        'to_table': ref_table,
                        'from_column': column.name,
                        'to_column': ref_col,
                        'type': 'many_to_one'  # SQLite only supports this type
                    })

        return DatabaseSchema(
            tables=tables,
            relationships=relationships
        )

    def _parse_connection_string(self, connection_string: str) -> str:
        """Parse SQLite connection string to get database path."""
        if connection_string.startswith('sqlite:///'):
            return urlparse(connection_string).path
        return connection_string


class SQLiteConnector(BaseDatabaseConnector):
    """Database connector implementation for SQLite."""

    def __init__(self) -> None:
        super().__init__()
        self._schema_loader = SQLiteSchemaLoader()

    async def _establish_connection(self, connection_string: str) -> aiosqlite.Connection:
        """Establish SQLite connection."""
        try:
            path = self._schema_loader._parse_connection_string(connection_string)
            conn = await aiosqlite.connect(path)
            await conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQLite database: {str(e)}")

    async def _close_connection(self) -> None:
        """Close SQLite connection."""
        if self._connection:
            await self._connection.close()


class SQLiteExecutor(BaseSQLExecutor):
    """SQL executor implementation for SQLite."""

    async def execute_query(self, sql_query: str) -> QueryResult:
        """Execute a SQL query on SQLite database."""
        if not isinstance(self._connector, SQLiteConnector):
            raise QueryExecutionError("SQLiteExecutor requires SQLiteConnector")

        if not self._connector.is_connected():
            raise ConnectionError("Database connection is not established")

        try:
            start_time = time.time()
            conn = self._connector._connection
            
            async with conn.execute(sql_query) as cursor:
                # For SELECT queries
                if sql_query.strip().upper().startswith('SELECT'):
                    rows = await cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    affected_rows = len(rows)
                else:
                    # For INSERT, UPDATE, DELETE queries
                    rows = []
                    columns = []
                    affected_rows = cursor.rowcount

                execution_time = time.time() - start_time

                return QueryResult(
                    columns=columns,
                    rows=rows,
                    affected_rows=affected_rows,
                    execution_time=execution_time,
                    query=sql_query
                )

        except Exception as e:
            raise QueryExecutionError(f"Failed to execute query: {str(e)}") 