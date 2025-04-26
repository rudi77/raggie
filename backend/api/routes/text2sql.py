# backend/api/routes/text2sql.py

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Any
from pydantic import BaseModel
import logging
from ..dependencies import get_text2sql_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/text2sql", tags=["text2sql"])

class QueryRequest(BaseModel):
    question: str

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
        logger.info(f"Processing query request: {request}")
        result = await text2sql_service.query(request.question)
        logger.info(f"Query result: {result}")

        return result

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/explain")
async def explain_query(
    request: QueryRequest,
    text2sql_service = Depends(get_text2sql_service)
):
    try:
        logger.info(f"Processing explain request: {request}")
        sql = await text2sql_service.explain(request.question)
        logger.info(f"Explain result: {sql}")
        return {"sql": sql}
    except Exception as e:
        logger.error(f"Error processing explain: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))