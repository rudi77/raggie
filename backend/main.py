from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from .api.routes import text2sql, query, templates, websocket
from .core.database import create_tables
from .services.scheduler_service import SchedulerService
from .services.text2sql_service import Text2SQLService
from .core.config import settings

app = FastAPI(
    title="cxo API",
    description="Backend API for cxo",
    version="0.1.0"
)

# Create database tables on startup
create_tables()

# Initialize services
text2sql_service = Text2SQLService(
    db_path=settings.DATABASE_URL.replace("sqlite:///", ""),
    openai_api_key=settings.OPENAI_API_KEY
)
scheduler = SchedulerService(text2sql_service)

@app.on_event("startup")
async def startup_event():
    """Start the scheduler on app startup"""
    await scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler on app shutdown"""
    await scheduler.stop()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(text2sql.router)
app.include_router(query.router)
app.include_router(templates.router)
app.include_router(websocket.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 