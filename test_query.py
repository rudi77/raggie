"""Simple script to test the SQL agent with our test database."""
import asyncio
import os
from text2sql.agent.sql_agent import SQLAgent
from llama_index.llms.openai import OpenAI

from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

endpoint = "http://127.0.0.1:6006/v1/traces"
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))
# Optionally, you can also print the spans to the console.
tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)


async def main():
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        return

    # Initialize OpenAI LLM with API key
    llm = OpenAI(api_key=api_key, model="gpt-4o-mini")
    
    # Initialize the SQL agent with our test database and LLM
    agent = SQLAgent(database_url="sqlite:///test.db", llm=llm)
    
    # Try a summary query
    question = "Gib mir für 'Musterdebitor Gewo GmbH' die Umsätze pro Periode aus"  # "Show me the total amount of transactions per period for Musterdebitor Gewo GmbH"
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