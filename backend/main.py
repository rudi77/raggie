from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from api.sql_queries import router as sql_router

app = FastAPI(
    title="iGecko API",
    description="Backend API for iGecko KI-Buchhaltungsassistent",
    version="0.1.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    content: str

class BookingEntry(BaseModel):
    date: str
    description: str
    category: str
    amount: float

@app.get("/")
async def root():
    return {"status": "API is running"}

@app.post("/api/query", response_model=List[BookingEntry])
async def process_query(message: Message):
    # Mock response for now
    return [
        BookingEntry(
            date="2024-03-15",
            description="Office supplies",
            category="Expenses",
            amount=150.50
        ),
        BookingEntry(
            date="2024-03-16",
            description="Client payment",
            category="Income",
            amount=2500.00
        )
    ]

# Include SQL routes
app.include_router(sql_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 