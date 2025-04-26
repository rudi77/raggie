from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/sql", tags=["sql"])

class SQLQuery(BaseModel):
    query: str
    parameters: Optional[dict] = None

class QueryResult(BaseModel):
    timestamp: str
    data: List[dict]
    query: str

@router.post("/execute", response_model=QueryResult)
async def execute_sql_query(query: SQLQuery):
    try:
        # TODO: Integrate with Text2SQL agent
        # For now, return mock data
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": [
                {"id": 1, "revenue": 15000, "month": "Januar"},
                {"id": 2, "revenue": 17500, "month": "Februar"},
                {"id": 3, "revenue": 21000, "month": "März"},
            ],
            "query": query.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables")
async def get_available_tables():
    """Return list of available tables in the database"""
    return {
        "tables": [
            {
                "name": "bookings",
                "columns": ["id", "date", "description", "category", "amount"]
            },
            {
                "name": "revenue",
                "columns": ["id", "month", "revenue", "year"]
            }
        ]
    } 