"""SQL agent implementation using LlamaIndex's NLSQLTableQueryEngine."""
import logging
from typing import Any, Dict, Optional

from llama_index.indices.struct_store import NLSQLTableQueryEngine
from llama_index.indices.struct_store.sql import SQLDatabase
from llama_index.llms import OpenAI

from ..core.config import LLMConfig
from ..core.exceptions import QueryGenerationError
from ..core.interfaces import QueryEngine
from ..core.schema import DatabaseSchema

logger = logging.getLogger(__name__)


class SQLAgent(QueryEngine):
    """Agent for converting natural language to SQL queries using LlamaIndex."""

    def __init__(self, llm_config: LLMConfig):
        """Initialize the SQL agent with LLM configuration."""
        self.llm_config = llm_config
        self.llm = self._initialize_llm()
        self.query_engine = None

    def _initialize_llm(self) -> OpenAI:
        """Initialize the LLM with the provided configuration."""
        try:
            return OpenAI(
                model=self.llm_config.model_name,
                temperature=self.llm_config.temperature,
                max_tokens=self.llm_config.max_tokens,
                api_key=self.llm_config.api_key,
                request_timeout=self.llm_config.timeout,
                **self.llm_config.additional_params
            )
        except Exception as e:
            raise QueryGenerationError(f"Failed to initialize LLM: {str(e)}")

    def _initialize_query_engine(self, sql_database: SQLDatabase) -> None:
        """Initialize the LlamaIndex query engine with the SQL database."""
        try:
            self.query_engine = NLSQLTableQueryEngine(
                sql_database=sql_database,
                llm=self.llm,
                verbose=True
            )
        except Exception as e:
            raise QueryGenerationError(f"Failed to initialize query engine: {str(e)}")

    async def generate_sql(self,
                         natural_query: str,
                         schema: DatabaseSchema,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """Convert natural language query to SQL using LlamaIndex."""
        try:
            if not self.query_engine:
                raise QueryGenerationError("Query engine not initialized. Call initialize_query_engine first.")

            # Generate SQL using LlamaIndex's query engine
            response = await self.query_engine.aquery(natural_query)
            
            # Extract the SQL query from the response
            # LlamaIndex's response includes both the SQL and the result
            # We want to return just the SQL part
            sql_query = response.metadata.get("sql_query", "")
            if not sql_query:
                raise QueryGenerationError("No SQL query generated")
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            raise QueryGenerationError(f"Failed to generate SQL: {str(e)}")

    async def validate_sql(self, sql_query: str, schema: DatabaseSchema) -> bool:
        """Validate if the SQL query is valid for the given schema."""
        try:
            if not self.query_engine:
                return False

            # Let LlamaIndex's SQLDatabase handle the validation
            # It will raise an exception if the SQL is invalid
            await self.query_engine.sql_database.run_sql(sql_query)
            return True
            
        except Exception as e:
            logger.error(f"Error validating SQL: {str(e)}")
            return False
