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
            
            # Test database connection
            async with AsyncFinanceSessionLocal() as session:
                result = await session.execute(text("SELECT 1"))
                row = result.fetchone()
                if row is None:
                    raise Exception("Database connection test failed")
                logger.info("Database connection verified successfully")
            
            self._initialized = True
            logger.info("Text2SQL service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Text2SQL service: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources."""
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
            # Decide how to present the result (markdown or @widgets/* directive)
            presentation = await self._choose_presentation(question, result.get("result"))
            
            return {
                "sql": result["sql_query"],
                "result": result["result"],
                "answer": result["answer"],
                "formatted_result": formatted_result,
                "presentation": presentation,
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

        async with AsyncFinanceSessionLocal() as session:
            try:
                # Start a new transaction
                async with session.begin():
                    result = await session.execute(text(sql_query))
                    if result.returns_rows:
                        # Convert results to list of dictionaries
                        keys = result.keys()
                        rows = [dict(zip(keys, row)) for row in result.fetchall()]
                        return rows
                    return []
            except Exception as e:
                logger.error(f"Error executing SQL query: {str(e)}")
                raise

    def _heuristic_presentation(self, rows):
        """Fallback decision on how to present data without an LLM call."""
        try:
            if not rows:
                return '@widgets/Text {"data":"Keine Daten gefunden."}'

            # Normalize to list of dicts
            if isinstance(rows, dict):
                rows = [rows]

            first = rows[0] if rows else {}
            if isinstance(first, dict) and len(first) == 1 and len(rows) == 1:
                value = list(first.values())[0]
                return f'@widgets/Number {{"data": {json.dumps(value, default=str)} }}'

            if not isinstance(first, dict) or not first:
                return '@widgets/Table'

            cols = list(first.keys())
            first_col = cols[0]
            first_val = first.get(first_col)

            def is_numeric(v):
                try:
                    float(str(v))
                    return True
                except Exception:
                    return False

            def looks_like_date(v):
                if not isinstance(v, str):
                    return False
                lv = v.lower()
                return any(k in lv for k in ["-", ":", "t", "z", "date", "datum", "monat", "month", "jahr", "year"])

            numeric_cols = [c for c in cols[1:] if is_numeric(first.get(c))]
            if looks_like_date(first_val) and numeric_cols:
                return f'@widgets/LineChart {{"data": {json.dumps(rows, default=str)} }}'

            if len(cols) == 2 and is_numeric(first.get(cols[1])):
                categories = len(rows)
                widget = "PieChart" if categories <= 6 else "BarChart"
                return f'@widgets/{widget} {{"data": {json.dumps(rows, default=str)} }}'

            return f'@widgets/Table {{"data": {json.dumps(rows, default=str)} }}'
        except Exception:
            return '@widgets/Table'

    async def _choose_presentation(self, question: str, rows):
        """Use LLM to choose a presentation, with heuristic fallback."""
        try:
            if rows is None:
                return '@widgets/Text {"data":"Keine Daten gefunden."}'

            prompt = f"""
Du bist ein Visualisierungsplaner. Analysiere die JSON-Daten und gib GENAU EINE Zeile als Antwort zurück:
- Entweder reines Markdown (kurze Erklärung),
- oder eine Widget-Direktive: @widgets/Table | @widgets/LineChart | @widgets/BarChart | @widgets/PieChart | @widgets/Text | @widgets/Number
- Wenn Du ein Widget nutzt, übergib Daten IMMER als JSON-Objekt mit Feld "data": @widgets/<Name> {{"data":[...]}}
- Verwende die vorhandenen Spaltennamen unverändert.
- Wähle:
  - LineChart: Zeitreihen (Datum/Zeit + numerische Spalten)
  - BarChart/PieChart: Kategorien + numerische Werte (Pie bei <=6 Kategorien)
  - Number: genau ein einzelner Wert
  - Table: sonst
- Keine zusätzlichen Erklärungen, nur die eine Zeile.

Frage: {question}
Daten (JSON): {json.dumps(rows, default=str)}
"""

            # Prefer async completion if available
            if hasattr(self.llm, "acomplete"):
                resp = await self.llm.acomplete(prompt)
            else:
                # Fallback to sync complete in a thread
                resp = await asyncio.to_thread(self.llm.complete, prompt)

            text = getattr(resp, "text", str(resp)).strip()
            return text or self._heuristic_presentation(rows)
        except Exception:
            return self._heuristic_presentation(rows)