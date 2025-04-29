from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

from backend.core.config import settings
from backend.core.database import templates_engine, Base
from backend.services.text2sql_service import Text2SQLService
from backend.services.scheduler_service import SchedulerService
from backend.services.websocket_manager import websocket_manager
from backend.api.routes import templates, websocket, text2sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(templates.router)  # Already has prefix in router definition
app.include_router(websocket.router)  # Already has prefix in router definition
app.include_router(text2sql.router)  # Already has prefix in router definition

# Initialize services
text2sql_service = Text2SQLService(db_path=settings.FINANCE_DB_PATH)
scheduler_service = SchedulerService(text2sql_service)

@app.on_event("startup")
async def startup_event():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=templates_engine)
    logger.info("Database tables created successfully")
    
    logger.info(f"Initializing Text2SQLService with finance database: {settings.FINANCE_DB_PATH}")
    await text2sql_service.initialize()
    
    logger.info("Initializing SchedulerService...")
    await scheduler_service.initialize()
    
    logger.info("Starting scheduler...")
    await scheduler_service.start()
    
    logger.info("Starting WebSocket health checks...")
    await websocket_manager.start_health_check()
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping scheduler...")
    await scheduler_service.stop()
    
    logger.info("Stopping WebSocket health checks...")
    await websocket_manager.stop_health_check()
    
    logger.info("Closing WebSocket connections...")
    await websocket_manager.close_all()
    
    logger.info("Application shutdown complete")

@app.get("/")
async def root():
    return {"message": "Raggie API is running"} 