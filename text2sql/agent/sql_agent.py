"""SQL agent implementation using LlamaIndex."""
from pathlib import Path
from typing import Dict, Optional, Any
from sqlalchemy import inspect

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
                return {"answer": response,
                        "sql_query": response.metadata.get("sql_query", ""),
                        "result": response.metadata.get("result", None)
                        }
            else:
                response = await self.query_engine.aquery(question)
                return {
                    "answer": str(response),
                    "sql_query": response.metadata.get("sql_query", ""),
                    "result": response.metadata.get("result", None)
                }
        except Exception as e:
            raise QueryGenerationError(f"Failed to generate or execute query: {str(e)}")

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
