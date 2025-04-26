# agents/tools.py

from smolagents import Tool
import json
from text2sql.agent.sql_agent import SQLAgent
from llama_index.llms.openai import OpenAI

class Text2SQLTool(Tool):
    def __init__(self, db_path: str, openai_api_key: str):
        """Initialize Text2SQL service with configuration."""
        # Initialize OpenAI LLM with API key
        self.llm = OpenAI(api_key=openai_api_key, model="gpt-4o-mini")
        
        # Initialize the SQL agent with our database and LLM
        self.agent = SQLAgent(database_url=f"sqlite:///{db_path}", llm=self.llm)

    async def query(self, question: str) -> dict:
        """Execute a natural language query."""
        try:
            # Use the agent's query method which returns a dictionary with sql_query, result, and answer
            result = await self.agent.query(question)
            
            print("\nQuestion:", question)
            print("\nSQL Query:", result["sql_query"])
            print("\nAnswer:", result["answer"])
            print("\nRaw Result:", result["result"])
            
            # Format the result as JSON string
            formatted_result = json.dumps(result["result"], default=str)
            
            return {
                "sql": result["sql_query"],
                "result": result["result"],
                "answer": result["answer"],
                "formatted_result": formatted_result
            }
        except Exception as e:
            # Log the error and re-raise
            print(f"Error in Text2SQL query: {str(e)}")
            raise

    async def explain(self, question: str) -> str:
        """Get SQL explanation for a question without executing it."""
        # For now, we'll just return the SQL query without executing it
        try:
            # Use the agent's query method but only return the SQL part
            result = await self.agent.query(question)
            return result["sql_query"]
        except Exception as e:
            # Log the error and re-raise
            print(f"Error in Text2SQL explain: {str(e)}")
            raise
