import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from ..core.database import AsyncTemplatesSessionLocal
from ..core.models import SQLTemplate
from ..services.websocket_manager import websocket_manager
from .text2sql_service import Text2SQLService
from ..core.config import settings
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionResult:
    def __init__(self, template_id: int, data: Optional[Dict] = None, error: Optional[str] = None):
        self.timestamp = datetime.now()
        self.template_id = template_id
        self.template_info = None
        self.error = error  # Add error as a direct attribute
        
        # Format data to match text2sql/query response
        if data and not error:
            self.data = {
                "sql_query": data.get("sql_query", ""),
                "result": data.get("result", []),
                "answer": data.get("answer", ""),
            }
        else:
            self.data = {
                "sql_query": "",
                "result": [],
                "answer": "",
            }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "template_id": self.template_id,
            "template_info": self.template_info,
            "data": self.data,
            "error": self.error
        }

class SchedulerService:
    def __init__(self, text2sql_service: Text2SQLService):
        self.text2sql_service = text2sql_service
        self.running = False
        self.results: Dict[int, ExecutionResult] = {}
        self.templates = []  # Store loaded templates
        self.interval = 60  # Default interval in seconds
        self.max_results_age = 3600  # 1 hour in seconds
        self.results_cache: Dict[int, Dict[str, Any]] = {}
        self._scheduler_task = None
        logger.info("SchedulerService initialized")

    async def initialize(self):
        """Initialize the scheduler service."""
        logger.info("Initializing SchedulerService...")
        # Load templates and their refresh rates
        await self.load_templates()

    async def load_templates(self):
        """Load templates from database."""
        try:
            logger.info(f"Loading templates from database: {settings.TEMPLATES_DB_PATH}")
            async with AsyncTemplatesSessionLocal() as db:
                result = await db.execute(text("SELECT * FROM sql_templates"))
                self.templates = result.fetchall()  # Store all templates
                logger.info(f"Found {len(self.templates)} templates")
                
                for template in self.templates:
                    logger.info(f"Processing template {template.id}: {template.name}")
                    logger.info(f"Template details: refresh_rate={template.refresh_rate}, query={template.query}")
                    
                    if template.refresh_rate > 0:  # Only schedule templates with refresh rate
                        self.results[template.id] = ExecutionResult(template.id)
                        self.results[template.id].template_info = {
                            "name": template.name,
                            "description": template.description,
                            "refresh_rate": template.refresh_rate
                        }
                        logger.info(f"Added template {template.id} to scheduler")
                    else:
                        logger.info(f"Skipping template {template.id} (refresh_rate=0)")
                
                logger.info(f"Loaded {len(self.results)} templates with active refresh rates")
                logger.info(f"Active templates: {list(self.results.keys())}")
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            logger.exception("Full traceback:")
            raise

    async def start(self):
        """Start the scheduler service."""
        if self.running:
            logger.warning("SchedulerService is already running")
            return
            
        logger.info("Starting SchedulerService")
        self.running = True
        
        # Create the scheduler task
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Scheduler task created")
        
        # Execute initial templates
        try:
            templates_to_execute = []
            current_time = datetime.now()
            
            for template in self.templates:
                if template.refresh_rate <= 0:
                    continue
                    
                cached_result = self.results_cache.get(template.id)
                if not cached_result or \
                   (current_time - cached_result["timestamp"]).total_seconds() >= template.refresh_rate:
                    templates_to_execute.append(template)
            
            if templates_to_execute:
                logger.info(f"Executing {len(templates_to_execute)} templates")
                await self._execute_templates(templates_to_execute)
        except Exception as e:
            logger.error(f"Error in initial template execution: {str(e)}")
            logger.exception("Full traceback:")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        logger.info("Scheduler loop started")
        while self.running:
            try:
                # Load templates if not already loaded
                if not self.templates:
                    await self.load_templates()
                
                # Execute templates
                templates_to_execute = []
                current_time = datetime.now()
                
                for template in self.templates:
                    if template.refresh_rate <= 0:
                        continue
                        
                    cached_result = self.results_cache.get(template.id)
                    if not cached_result or \
                       (current_time - cached_result["timestamp"]).total_seconds() >= template.refresh_rate:
                        templates_to_execute.append(template)
                
                if templates_to_execute:
                    logger.info(f"Executing {len(templates_to_execute)} templates")
                    await self._execute_templates(templates_to_execute)
                
                # Wait for the next interval
                await asyncio.sleep(self.interval)
                
            except asyncio.CancelledError:
                logger.info("Scheduler loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                logger.exception("Full traceback:")
                await asyncio.sleep(5)  # Wait before retrying

    async def stop(self):
        """Stop the scheduler."""
        logger.info("Stopping scheduler...")
        self.running = False
        
        if self._scheduler_task:
            try:
                self._scheduler_task.cancel()
                await self._scheduler_task
            except asyncio.CancelledError:
                logger.info("Scheduler task cancelled")
            except Exception as e:
                logger.error(f"Error cancelling scheduler task: {str(e)}")
        
        # Cleanup text2sql service
        try:
            await self.text2sql_service.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up Text2SQL service: {str(e)}")
        
        logger.info("Scheduler stopped")

    async def execute_template(self, template_row) -> ExecutionResult:
        """Execute a single template and return the result."""
        try:
            # Access template attributes using SQLAlchemy's mapping
            template_id = template_row.id
            template_name = template_row.name
            template_description = template_row.description
            template_query = template_row.query
            template_refresh_rate = template_row.refresh_rate
            
            logger.info(f"Starting execution of template {template_id}: {template_name}")
            logger.info(f"Template query: {template_query}")
            
            # Execute the SQL query
            result = await self.text2sql_service.execute_raw_sql(template_query)
            logger.info(f"Raw SQL execution completed. Result: {result[:5] if result else []}")  # Log first 5 rows only
            
            # Create execution result with properly formatted data
            execution_result = ExecutionResult(
                template_id=template_id,
                data={
                    "sql_query": template_query,
                    "result": result,  # result is now directly a List[Dict]
                    "answer": "",  # Raw SQL execution doesn't provide an answer
                }
            )
            execution_result.template_info = {
                "name": template_name,
                "description": template_description,
                "refresh_rate": template_refresh_rate
            }
            
            # Update template's last_execution timestamp
            async with AsyncTemplatesSessionLocal() as db:
                await db.execute(
                    text("UPDATE sql_templates SET last_execution = :now WHERE id = :id"),
                    {"now": datetime.now(), "id": template_id}
                )
                await db.commit()
                logger.info(f"Updated last_execution timestamp for template {template_id}")
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing template {getattr(template_row, 'id', 'unknown')}: {str(e)}")
            logger.exception("Full traceback:")
            error_result = ExecutionResult(
                template_id=getattr(template_row, 'id', 0),
                error=str(e)
            )
            error_result.template_info = {
                "name": getattr(template_row, 'name', 'Unknown'),
                "description": getattr(template_row, 'description', None),
                "refresh_rate": getattr(template_row, 'refresh_rate', 0)
            }
            return error_result

    async def _execute_templates(self, templates):
        """Execute a list of templates and broadcast results."""
        for template in templates:
            try:
                result = await self.execute_template(template)
                
                broadcast_data = {
                    "type": "live_update",
                    "template_id": template.id,
                    "data": result.data,
                    "template_info": result.template_info,
                    "error": result.error if hasattr(result, 'error') else None
                }
                
                # Store result in memory cache
                self.results_cache[template.id] = {
                    "timestamp": datetime.now(),
                    "result": result
                }
                
                # Broadcast result via WebSocket
                await websocket_manager.broadcast(template.id, broadcast_data)
                logger.info(f"Broadcasted results for template {template.id}")
                
            except Exception as e:
                logger.error(f"Failed to execute template {template.id}: {str(e)}")
                logger.exception("Full traceback:")
                # Broadcast error
                error_data = {
                    "type": "live_update",
                    "template_id": template.id,
                    "error": str(e),
                    "template_info": {
                        "name": template.name,
                        "description": template.description,
                        "refresh_rate": template.refresh_rate
                    }
                }
                await websocket_manager.broadcast(template.id, error_data)

    async def _cleanup_old_results(self):
        """Remove results older than max_results_age."""
        current_time = datetime.now()
        for template_id, result in list(self.results.items()):
            if (current_time - result.timestamp).total_seconds() > self.max_results_age:
                del self.results[template_id]

    def get_result(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get the latest result for a template."""
        result = self.results.get(template_id)
        if result:
            return result.to_dict()
        return None

# Global instance
scheduler = None  # Will be initialized in main.py 