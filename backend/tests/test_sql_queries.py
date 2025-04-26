from fastapi.testclient import TestClient
from backend.main import app
import pytest

client = TestClient(app)

def test_tables_endpoint():
    response = client.get("/api/sql/tables")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all("name" in table and "columns" in table for table in data)

def test_execute_valid_query():
    query = {
        "query": "SELECT * FROM bookings",
        "parameters": {}
    }
    response = client.post("/api/sql/execute", json=query)
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "data" in data
    assert "query" in data
    assert isinstance(data["data"], list)

def test_execute_invalid_query():
    query = {
        "query": "INVALID SQL QUERY",
        "parameters": {}
    }
    response = client.post("/api/sql/execute", json=query)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data 