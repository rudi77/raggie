from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from .api.routes import text2sql, query
from .core.database import create_tables

app = FastAPI(
    title="cxo API",
    description="Backend API for cxo",
    version="0.1.0"
)

# Create database tables on startup
create_tables()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Text2SQL routes
app.include_router(text2sql.router)
app.include_router(query.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 