from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
import socket
import signal
import asyncio
import sys
import os

from backend.core.config import settings
from backend.core.database import templates_engine, Base, create_tables
from backend.services.text2sql_service import Text2SQLService
from backend.services.scheduler_service import SchedulerService
from backend.services.websocket_manager import websocket_manager
from backend.api.routes import templates, websocket, text2sql

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log network information
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
logger.info(f"Server hostname: {hostname}")
logger.info(f"Server local IP: {local_ip}")

# Try to create a test socket to verify port availability
def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except socket.error as e:
        logger.error(f"Port {port} is not available: {str(e)}")
        return False
    finally:
        sock.close()

# Check if port 9000 is available
if not check_port(9000):
    logger.warning("Port 9000 is not available, trying port 9001")
    if not check_port(9001):
        logger.error("Neither port 9000 nor 9001 is available")
        sys.exit(1)

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
startup_completed = False

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    logger.info("Received shutdown signal, initiating graceful shutdown...")
    # Only handle signals in the main process
    if os.getpid() == os.getppid():
        # Create a new event loop for the shutdown process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(shutdown_event())
        finally:
            loop.close()
        sys.exit(0)

# Register signal handlers only in the main process
if os.getpid() == os.getppid():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

@app.on_event("startup")
async def startup_event():
    """Initialize services and database on startup."""
    global scheduler, startup_completed
    
    try:
        logger.info("Starting application startup sequence...")
        
        # Step 1: Create database tables
        logger.info("Step 1: Creating database tables...")
        await create_tables()
        logger.info("Database tables created successfully")
        
        # Step 2: Initialize Text2SQLService
        logger.info("Step 2: Initializing Text2SQLService...")
        logger.info(f"Using finance database: {settings.FINANCE_DB_PATH}")
        await text2sql_service.initialize()
        logger.info("Text2SQLService initialized successfully")
        
        # Step 3: Initialize SchedulerService
        logger.info("Step 3: Initializing SchedulerService...")
        scheduler = SchedulerService(text2sql_service)
        await scheduler.initialize()
        logger.info("SchedulerService initialized successfully")
        
        # Step 4: Start SchedulerService
        logger.info("Step 4: Starting SchedulerService...")
        await scheduler.start()
        logger.info("SchedulerService started successfully")
        
        # Step 5: Start WebSocket health checks
        logger.info("Step 5: Starting WebSocket health checks...")
        await websocket_manager.start_health_check()
        logger.info("WebSocket health checks started successfully")
        
        logger.info("Application startup completed successfully")
        startup_completed = True
        return True
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        logger.exception("Startup error details:")
        startup_completed = False
        return False

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
    if not startup_completed:
        raise HTTPException(status_code=503, detail="Service is still starting up")
    logger.debug("Root endpoint accessed")
    return {"message": "Raggie API is running"}

@app.get("/health")
async def health_check():
    if not startup_completed:
        raise HTTPException(status_code=503, detail="Service is still starting up")
    return {"status": "healthy"} 