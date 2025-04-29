from typing import Optional, Any
import asyncio
import json
import logging
from text2sql.agent.sql_agent import SQLAgent
from llama_index.llms.openai import OpenAI
from sqlalchemy.exc import SQLAlchemyError
from ..core.config import settings
from ..core.database import finance_engine

# Configure logging
logger = logging.getLogger(__name__)

class Text2SQLService:
    def __init__(self, db_path: str):
        """Initialize Text2SQL service with configuration."""
        self.db_path = db_path
        self.agent = None
        self.llm = None
        self._initialized = False

    async def initialize(self):
        """Initialize the service with OpenAI API key."""
        if self._initialized:
            return

        try:
            # Initialize OpenAI LLM with API key
            self.llm = OpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")
            
            # Initialize the SQL agent with our database and LLM
            logger.info(f"Initializing SQLAgent with database: {self.db_path}")
            self.agent = SQLAgent(database_url=f"sqlite:///{self.db_path}", llm=self.llm)
            
            self._initialized = True
            logger.info("Text2SQL service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Text2SQL service: {str(e)}")
            raise

    async def query(self, question: str) -> dict:
        """Execute a natural language query."""
        if not self._initialized:
            await self.initialize()

        try:
            # Use the agent's query method which returns a dictionary with sql_query, result, and answer
            result = await self.agent.query(question)
            
            logger.info(f"Question: {question}")
            logger.info(f"SQL Query: {result['sql_query']}")
            logger.info(f"Answer: {result['answer']}")
            
            # Format the result as JSON string
            formatted_result = json.dumps(result["result"], default=str)
            
            return {
                "sql": result["sql_query"],
                "result": result["result"],
                "answer": result["answer"],
                "formatted_result": formatted_result
            }
        except Exception as e:
            logger.error(f"Error in Text2SQL query: {str(e)}")
            raise

    async def execute_sql(self, sql_query: str) -> dict:
        """Execute a raw SQL query directly."""
        try:
            # Use direct database connection for SQL execution
            with finance_engine.connect() as connection:
                result = connection.execute(sql_query)
                rows = [dict(row) for row in result]
            
            logger.info(f"Executing SQL: {sql_query}")
            logger.info(f"Raw Result: {rows}")
            
            # Format the result as JSON string
            formatted_result = json.dumps(rows, default=str)
            
            return {
                "sql": sql_query,
                "result": rows,
                "formatted_result": formatted_result
            }
        except SQLAlchemyError as e:
            logger.error(f"SQL Error executing query: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"General error executing SQL: {str(e)}")
            raise

    async def explain(self, question: str) -> str:
        """Get SQL explanation for a question without executing it."""
        if not self._initialized:
            await self.initialize()

        try:
            # Use the agent's query method but only return the SQL part
            result = await self.agent.query(question)
            return result["sql_query"]
        except Exception as e:
            logger.error(f"Error in Text2SQL explain: {str(e)}")
            raise