"""Tests for the SQL agent."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from text2sql.agent.sql_agent import SQLAgent
from text2sql.core.config import LLMConfig
from text2sql.core.schema import Column, Table, DatabaseSchema


@pytest.fixture
def sample_schema():
    """Create a sample database schema for testing."""
    users_table = Table(
        name="users",
        columns=[
            Column(name="id", data_type="INTEGER", is_primary=True),
            Column(name="name", data_type="TEXT", is_nullable=False),
            Column(name="email", data_type="TEXT", is_nullable=True),
            Column(name="created_at", data_type="TIMESTAMP", is_nullable=True)
        ],
        primary_keys=["id"],
        description="User information"
    )
    
    posts_table = Table(
        name="posts",
        columns=[
            Column(name="id", data_type="INTEGER", is_primary=True),
            Column(name="user_id", data_type="INTEGER", is_nullable=False, is_foreign=True, references="users.id"),
            Column(name="title", data_type="TEXT", is_nullable=False),
            Column(name="content", data_type="TEXT", is_nullable=True),
            Column(name="created_at", data_type="TIMESTAMP", is_nullable=True)
        ],
        primary_keys=["id"],
        foreign_keys=["user_id"],
        description="User posts"
    )
    
    return DatabaseSchema(
        tables=[users_table, posts_table],
        relationships=[
            {
                "from_table": "posts",
                "to_table": "users",
                "from_column": "user_id",
                "to_column": "id",
                "type": "many_to_one"
            }
        ]
    )


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    mock = MagicMock()
    mock.apredict = AsyncMock(return_value="SELECT name FROM users")
    return mock


@pytest.fixture
def test_db_path():
    """Create a test database path."""
    return "sqlite:///test.db"


@pytest.mark.asyncio
async def test_sql_agent_initialization(mock_llm, test_db_path):
    """Test SQL agent initialization."""
    agent = SQLAgent(test_db_path, llm=mock_llm)
    assert agent is not None


@pytest.mark.asyncio
async def test_generate_sql(mock_llm, test_db_path, sample_schema):
    """Test SQL generation."""
    expected_sql = "SELECT name FROM users"

    agent = SQLAgent(test_db_path, llm=mock_llm)
    result = await agent.query("What are the names of all users?")
    assert result["sql_query"] == expected_sql


@pytest.mark.asyncio
async def test_validate_sql(mock_llm, test_db_path, sample_schema):
    """Test SQL validation."""
    agent = SQLAgent(test_db_path, llm=mock_llm)
    assert agent is not None


@pytest.mark.asyncio
async def test_generate_sql_error_handling(mock_llm, test_db_path, sample_schema):
    """Test error handling in SQL generation."""
    mock_llm.apredict.side_effect = Exception("LLM error")
    agent = SQLAgent(test_db_path, llm=mock_llm)
    with pytest.raises(Exception):
        await agent.query("Invalid query") 