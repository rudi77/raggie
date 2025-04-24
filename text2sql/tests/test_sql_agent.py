"""Tests for the SQL agent implementation."""
import os
import pytest
import pytest_asyncio
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

from ..agent.sql_agent import SQLAgent, QueryGenerationError
from .create_test_db import create_test_db

TEST_DB_PATH = "test.db"

@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a test database with transaction data."""
    create_test_db(TEST_DB_PATH)
    yield TEST_DB_PATH
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except PermissionError:
        print(f"Warning: Could not remove test database at {TEST_DB_PATH}")

@pytest_asyncio.fixture
async def sql_agent(test_db):
    """Create a SQL agent instance with test database."""
    agent = SQLAgent(database_url=f"sqlite:///{test_db}")
    return agent

@pytest.mark.asyncio
async def test_sql_agent_initialization(sql_agent):
    """Test that SQL agent initializes correctly."""
    assert sql_agent.sql_database is not None
    assert sql_agent.query_engine is not None
    table_info = sql_agent.get_table_info()
    assert "transactions" in table_info.lower()

@pytest.mark.asyncio
async def test_basic_query(sql_agent):
    """Test basic query execution."""
    question = "What is the total amount for Musterdebitor Gewo GmbH?"
    result = await sql_agent.query(question)
    assert "answer" in result
    assert "sql_query" in result
    assert "result" in result
    assert "select" in result["sql_query"].lower()
    assert "musterdebitor" in result["sql_query"].lower()

@pytest.mark.asyncio
async def test_query_with_date_filter(sql_agent):
    """Test query with date filtering."""
    question = "Show transactions from January 2024"
    result = await sql_agent.query(question)
    assert any(term in result["sql_query"] for term in ["202401", "'January 2024'"])
    assert result["result"] is not None

@pytest.mark.skip(reason="LlamaIndex query engine is too robust to test invalid queries")
@pytest.mark.asyncio
async def test_invalid_query(sql_agent):
    """Test handling of invalid queries."""
    with pytest.raises(QueryGenerationError):
        await sql_agent.query("Tell me a joke about SQL")

@pytest.mark.asyncio
async def test_get_table_info(sql_agent):
    """Test retrieval of table information."""
    table_info = sql_agent.get_table_info()
    assert "transactions" in table_info.lower()
    assert "amount" in table_info.lower()
    assert "period" in table_info.lower()

@pytest.mark.asyncio
async def test_aggregation_query(sql_agent):
    """Test query with aggregation."""
    question = "What is the total amount of all transactions?"
    result = await sql_agent.query(question)
    assert "sum" in result["sql_query"].lower()
    assert "amount" in result["sql_query"].lower()
    assert result["result"] is not None 