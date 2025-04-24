"""Simple script to test the SQL agent with our test database."""
import asyncio
import os
from text2sql.agent.sql_agent import SQLAgent
from llama_index.llms.openai import OpenAI

async def main():
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return

    # Initialize OpenAI LLM with API key
    llm = OpenAI(api_key=api_key)
    
    # Initialize the SQL agent with our test database and LLM
    agent = SQLAgent(database_url="sqlite:///test.db", llm=llm)
    
    # Try a summary query
    question = "Show me the total amount of transactions per period for Musterdebitor Gewo GmbH"
    try:
        result = await agent.query(question)
        print("\nQuestion:", question)
        print("\nSQL Query:", result["sql_query"])
        print("\nAnswer:", result["answer"])
        print("\nRaw Result:", result["result"])
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 