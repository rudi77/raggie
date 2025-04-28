# backend/api/routes/query.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Any
from pydantic import BaseModel
from smolagents import CodeAgent
from ..dependencies import get_manager_agent

router = APIRouter(tags=["query"])

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    sql: str
    result: Any

@router.post('/query', response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    manager_agent: CodeAgent = Depends(get_manager_agent)
):
    try:
        result = await manager_agent.run(request.question)
        return QueryResponse(sql=result["sql"], result=result["result"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

