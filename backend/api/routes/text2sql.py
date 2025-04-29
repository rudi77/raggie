# backend/api/routes/text2sql.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
from ...core.database import get_finance_db
from ...services.text2sql_service import Text2SQLService
from ...core.config import settings

router = APIRouter(
    prefix="/text2sql",
    tags=["text2sql"]
)

# Initialize Text2SQL service
text2sql_service = Text2SQLService(db_path=settings.FINANCE_DB_PATH)

# Initialize the service
@router.on_event("startup")
async def startup_event():
    await text2sql_service.initialize()

class QueryRequest(BaseModel):
    question: str

class SQLRequest(BaseModel):
    sql: str

@router.post("/query")
async def query(request: QueryRequest) -> Dict[str, Any]:
    """Convert natural language question to SQL and execute it."""
    try:
        result = await text2sql_service.query(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_sql(request: SQLRequest) -> Dict[str, Any]:
    """Execute a raw SQL query."""
    try:
        result = await text2sql_service.execute_sql(request.sql)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain")
async def explain(request: QueryRequest) -> str:
    """Get SQL explanation for a question without executing it."""
    try:
        sql = await text2sql_service.explain(request.question)
        return sql
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))