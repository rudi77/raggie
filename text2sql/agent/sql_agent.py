"""SQL agent implementation using LlamaIndex."""
from pathlib import Path
from typing import Dict, Optional, Any, List
from sqlalchemy import inspect, create_engine, text

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.llms.openai import OpenAI

from ..core.exceptions import QueryGenerationError

class SQLAgent:
    """SQL agent that uses LlamaIndex's NLSQLTableQueryEngine for natural language queries."""
    
    def __init__(
        self,
        database_url: str,
        llm: Optional[Any] = None,
    ):
        """Initialize the SQL agent.
        
        Args:
            database_url: URL to the database (e.g. sqlite:///path/to/db.sqlite)
            llm: Optional language model to use. If not provided, uses OpenAI.
        """
        self.llm = llm or OpenAI()
        self.sql_database = SQLDatabase.from_uri(database_url)
        self.query_engine = NLSQLTableQueryEngine(
            sql_database=self.sql_database,
            llm=self.llm,
            tables=self.sql_database.get_usable_table_names()
        )
        self.retriever = NLSQLRetriever(
            sql_database=self.sql_database,
            llm=self.llm,
            tables=self.sql_database.get_usable_table_names()
        )
        
        self.engine = create_engine(self.database_url, future=True)


    async def query(self, question: str, retriever: bool = True) -> Dict[str, Any]:
        """Execute a natural language query against the database.
        
        Args:
            question: Natural language question about the data
            
        Returns:
            Dictionary containing the answer, SQL query, and raw result
            
        Raises:
            QueryGenerationError: If query generation or execution fails
        """
        try:
            if retriever:
                print(f'__________retriever___________ : {question}\n{self.retriever._text_to_sql_prompt}')
                response = await self.retriever.aretrieve(question)
                print(response)
                
                # Handle the case where response is a list
                if isinstance(response, list) and len(response) > 0:
                    # Extract data from the first item in the list
                    first_item = response[0]
                    if hasattr(first_item, 'metadata'):
                        return {
                            "answer": str(first_item),
                            "sql_query": first_item.metadata.get("sql_query", ""),
                            "result": first_item.metadata.get("result", None)
                        }
                    else:
                        # If it's a list but doesn't have metadata, just return the raw response
                        return {
                            "answer": str(response),
                            "sql_query": "",
                            "result": response
                        }
                else:
                    # If response is not a list or is empty, handle as before
                    return {
                        "answer": str(response),
                        "sql_query": response.metadata.get("sql_query", "") if hasattr(response, 'metadata') else "",
                        "result": response.metadata.get("result", None) if hasattr(response, 'metadata') else None
                    }
            else:
                response = await self.query_engine.aquery(question)
                return {
                    "answer": str(response),
                    "sql_query": response.metadata.get("sql_query", "") if hasattr(response, 'metadata') else "",
                    "result": response.metadata.get("result", None) if hasattr(response, 'metadata') else None
                }
        except Exception as e:
            raise QueryGenerationError(f"Failed to generate or execute query: {str(e)}")

    async def execute_raw_sql(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute a raw SQL query using SQLAlchemy, bypassing LlamaIndex entirely.
        Returns a dict with the rows.
        """
        try:

            # Run in thread‐pool so you don’t block the event loop
            from starlette.concurrency import run_in_threadpool

            def _run():
                with self.engine.connect() as conn:
                    result = conn.execute(text(sql_query))
                    # turn each Row into a dict
                    return [dict(row) for row in result]

            rows = await run_in_threadpool(_run)
            return {"result": rows}

        except Exception as e:
            raise QueryGenerationError(f"Failed to execute SQL query: {e}")

    def get_table_info(self) -> str:
        """Get information about available tables in the database.
        
        Returns:
            String containing table schema information
        """
        inspector = inspect(self.sql_database._engine)
        table_info = []
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            table_info.append(f"\nTable: {table_name}")
            for col in columns:
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                table_info.append(f"  {col['name']} {col['type']} {nullable}")
        
        return "\n".join(table_info)
