"""Tests for SQLite implementations."""
import os
import pytest
import aiosqlite
from text2sql.core.sqlite import SQLiteConnector, SQLiteExecutor


@pytest.fixture
async def test_db_path(tmp_path):
    """Create a test database with sample tables."""
    db_path = tmp_path / "test.db"
    
    async with aiosqlite.connect(db_path) as conn:
        # Create test tables
        await conn.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await conn.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Insert sample data
        await conn.execute("""
            INSERT INTO users (name, email) VALUES
            ('Alice', 'alice@example.com'),
            ('Bob', 'bob@example.com')
        """)
        
        await conn.execute("""
            INSERT INTO posts (user_id, title, content) VALUES
            (1, 'First Post', 'Hello World'),
            (1, 'Second Post', 'More content'),
            (2, 'Bob''s Post', 'My first post')
        """)
        
        await conn.commit()
    
    return str(db_path)


@pytest.mark.asyncio
async def test_sqlite_connector(test_db_path):
    """Test SQLite connector functionality."""
    connector = SQLiteConnector()
    db_url = f"sqlite:///{test_db_path}"

    # Test connection
    await connector.connect(db_url)
    assert connector._connection is not None

    # Test schema loading
    schema = await connector.load_schema()
    assert len(schema.tables) == 2
    assert any(t.name == "users" for t in schema.tables)
    assert any(t.name == "posts" for t in schema.tables)

    # Test closing connection
    await connector.close()
    assert connector._connection is None


@pytest.mark.asyncio
async def test_sqlite_executor(test_db_path):
    """Test SQLite executor functionality."""
    connector = SQLiteConnector()
    db_url = f"sqlite:///{test_db_path}"
    await connector.connect(db_url)
    
    executor = SQLiteExecutor(connector)
    
    # Test simple query
    result = await executor.execute_query("SELECT name FROM users")
    assert len(result.rows) == 2
    assert result.rows[0][0] in ["Alice", "Bob"]
    
    # Test query with parameters
    result = await executor.execute_query(
        "SELECT title FROM posts WHERE user_id = ?",
        parameters=(1,)
    )
    assert len(result.rows) == 2
    assert result.rows[0][0] in ["First Post", "Second Post"]
    
    await connector.close()


@pytest.mark.asyncio
async def test_error_handling(test_db_path):
    """Test error handling in SQLite implementations."""
    connector = SQLiteConnector()
    db_url = f"sqlite:///{test_db_path}"
    
    # Test invalid connection string
    with pytest.raises(Exception):
        await connector.connect("invalid:///path")
    
    # Test connection to non-existent database
    with pytest.raises(Exception):
        await connector.connect("sqlite:///nonexistent.db")
    
    # Test valid connection
    await connector.connect(db_url)
    
    # Test invalid query
    executor = SQLiteExecutor(connector)
    with pytest.raises(Exception):
        await executor.execute_query("SELECT * FROM nonexistent_table")
    
    await connector.close() 