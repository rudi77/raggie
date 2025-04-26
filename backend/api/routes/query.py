# backend/api/routes/query.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Any
from pydantic import BaseModel

from ...agents import create_manager_agent

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql: str
    result: Any

@router.post('/query', response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    manager_agent = Depends(create_manager_agent)
):
    try:
        result = await manager_agent.execute(request.question)
        return QueryResponse(sql=result["sql"], result=result["result"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

