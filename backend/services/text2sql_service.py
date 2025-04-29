from typing import Optional, Any, Dict, List
import asyncio
import json
import logging
from text2sql.agent.sql_agent import SQLAgent
from llama_index.llms.openai import OpenAI
from sqlalchemy.exc import SQLAlchemyError
from ..core.config import settings
from ..core.database import finance_engine, AsyncFinanceSessionLocal
from sqlalchemy import text
import aiosqlite
from sqlalchemy.ext.asyncio import AsyncSession

# Configure logging
logger = logging.getLogger(__name__)

class Text2SQLService:
    def __init__(self, db_path: str):
        """Initialize Text2SQL service with configuration."""
        self.db_path = db_path
        self.agent = None
        self.llm = None
        self.engine = finance_engine
        self._initialized = False
        self._session: Optional[AsyncSession] = None

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
            
            # Create a session
            self._session = AsyncFinanceSessionLocal()
            
            # Verify database connection
            async with self._session as session:
                result = await session.execute(text("SELECT 1"))
                row = result.fetchone()
                if row is None:
                    raise Exception("Database connection test failed")
                logger.info("Database connection verified successfully")
            
            self._initialized = True
            logger.info("Text2SQL service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Text2SQL service: {str(e)}")
            if self._session:
                await self._session.close()
                self._session = None
            raise

    async def cleanup(self):
        """Cleanup resources."""
        if self._session:
            await self._session.close()
            self._session = None
        self._initialized = False

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
        """Execute a raw SQL query."""
        if not self._initialized:
            await self.initialize()

        try:
            logger.info(f"Executing SQL query: {sql_query}")
            logger.info(f"Using database: {self.db_path}")
            
            # Execute the query using the correct method name
            result = await self.agent.execute_raw_sql(sql_query)
            
            logger.debug(f"Query execution result: {result}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error executing query: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
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

    async def execute_raw_sql(self, sql_query: str) -> List[Dict]:
        """Execute a raw SQL query and return results as a list of dictionaries."""
        if not self._initialized:
            await self.initialize()

        try:
            async with self._session as session:
                result = await session.execute(text(sql_query))
                if result.returns_rows:
                    # Convert results to list of dictionaries
                    keys = result.keys()
                    rows = [dict(zip(keys, row)) for row in result.fetchall()]
                    await session.commit()
                    return rows
                else:
                    await session.commit()
                    return []
        except Exception as e:
            logger.error(f"Error executing SQL query: {str(e)}")
            if 'session' in locals():
                await session.rollback()
            raise