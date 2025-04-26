# backend/api/routes/text2sql.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Any
from pydantic import BaseModel
from ..dependencies import get_text2sql_service

router = APIRouter(prefix="/text2sql", tags=["text2sql"])

class QueryRequest(BaseModel):
    question: str
    output_format: Optional[str] = None

class QueryResponse(BaseModel):
    sql: str
    result: Any
    formatted_result: str

@router.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    text2sql_service = Depends(get_text2sql_service)
):
    try:
        result = text2sql_service.query(
            request.question,
            request.output_format
        )
        return {
            "sql": result.sql,
            "result": result.result,
            "formatted_result": result.formatted_result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/explain")
async def explain_query(
    request: QueryRequest,
    text2sql_service = Depends(get_text2sql_service)
):
    try:
        sql = text2sql_service.explain(request.question)
        return {"sql": sql}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))