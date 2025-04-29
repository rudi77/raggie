from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

from backend.core.config import settings
from backend.core.database import templates_engine, Base, create_tables
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
    allow_headers=["*"]
)

# Include routers
app.include_router(templates.router)  # Already has prefix in router definition
app.include_router(websocket.router)  # Already has prefix in router definition
app.include_router(text2sql.router)  # Already has prefix in router definition

# Initialize services
text2sql_service = Text2SQLService(settings.FINANCE_DB_PATH)
scheduler = None

@app.on_event("startup")
async def startup_event():
    """Initialize services and database on startup."""
    global scheduler
    
    try:
        logger.info("Creating database tables...")
        await create_tables()
        logger.info("Database tables created successfully")
        
        # Initialize Text2SQLService
        logger.info(f"Initializing Text2SQLService with finance database: {settings.FINANCE_DB_PATH}")
        await text2sql_service.initialize()
        
        # Initialize and start SchedulerService
        logger.info("Initializing SchedulerService...")
        scheduler = SchedulerService(text2sql_service)
        await scheduler.initialize()
        
        logger.info("Starting SchedulerService...")
        await scheduler.start()
        
        # Start WebSocket health checks
        logger.info("Starting WebSocket health checks...")
        await websocket_manager.start_health_check()
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global scheduler
    
    try:
        # Stop scheduler first to prevent new queries
        if scheduler:
            logger.info("Stopping SchedulerService...")
            await scheduler.stop()
            scheduler = None
        
        # Stop WebSocket health checks
        logger.info("Stopping WebSocket health checks...")
        await websocket_manager.stop_health_check()
        
        # Close all WebSocket connections
        logger.info("Closing all WebSocket connections...")
        await websocket_manager.close_all()
        
        # Cleanup text2sql service
        logger.info("Cleaning up Text2SQL service...")
        await text2sql_service.cleanup()
        
        logger.info("Shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
        logger.exception("Shutdown error details:")
        raise

@app.get("/")
async def root():
    return {"message": "Raggie API is running"} 