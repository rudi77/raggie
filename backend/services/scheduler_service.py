import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from ..core.database import TemplatesSessionLocal
from ..core.models import SQLTemplate
from ..services.websocket_manager import websocket_manager
from .text2sql_service import Text2SQLService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExecutionResult:
    def __init__(self, template_id: int, data: Optional[Dict] = None, error: Optional[str] = None):
        self.timestamp = datetime.now()
        self.template_id = template_id
        self.template_info = None
        
        # Format data to match text2sql/query response
        if data:
            self.data = {
                "sql_query": data.get("sql_query", ""),
                "result": data.get("result", []),
                "answer": data.get("answer", ""),
                "error": error
            }
        else:
            self.data = {
                "sql_query": "",
                "result": [],
                "answer": "",
                "error": error
            }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "template_id": self.template_id,
            "template_info": self.template_info,
            "data": self.data
        }

class SchedulerService:
    def __init__(self, text2sql_service: Text2SQLService):
        self.text2sql_service = text2sql_service
        self.running = False
        self.results: Dict[int, ExecutionResult] = {}
        self.interval = 60  # Default interval in seconds
        self.max_results_age = 3600  # 1 hour in seconds
        logger.info("SchedulerService initialized")

    async def initialize(self):
        """Initialize the scheduler service."""
        logger.info("Initializing SchedulerService...")
        # Load templates and their refresh rates
        await self.load_templates()

    async def load_templates(self):
        """Load templates from database."""
        try:
            logger.info("Loading templates from database")
            with TemplatesSessionLocal() as db:
                templates = db.query(SQLTemplate).all()
                logger.info(f"Found {len(templates)} templates")
                
                for template in templates:
                    logger.info(f"Processing template {template.id}: {template.name} (refresh_rate: {template.refresh_rate})")
                    if template.refresh_rate > 0:  # Only schedule templates with refresh rate
                        self.results[template.id] = ExecutionResult(template.id)
                        self.results[template.id].template_info = {
                            "name": template.name,
                            "description": template.description,
                            "refresh_rate": template.refresh_rate
                        }
                        logger.info(f"Added template {template.id} to scheduler")
                
                logger.info(f"Loaded {len(self.results)} templates with active refresh rates")
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            raise

    async def start(self):
        """Start the scheduler."""
        if not self.running:
            self.running = True
            logger.info("Starting scheduler and executing initial template cycle")
            
            # Execute templates immediately
            try:
                await self._execute_templates()
            except Exception as e:
                logger.error(f"Error during initial template execution: {str(e)}")
            
            # Start the scheduler loop
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())
            logger.info("Scheduler loop started")

    async def stop(self):
        """Stop the scheduler."""
        self.running = False
        if hasattr(self, '_scheduler_task'):
            try:
                self._scheduler_task.cancel()
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        logger.info("Scheduler loop started")
        while self.running:
            try:
                logger.info("Starting scheduler cycle")
                await self._execute_templates()
                await self._cleanup_old_results()
                logger.info(f"Scheduler cycle complete, sleeping for {self.interval} seconds")
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _execute_templates(self):
        """Execute all templates that need to be refreshed."""
        logger.info("Starting template execution cycle")
        for template_id, result in self.results.items():
            try:
                with TemplatesSessionLocal() as db:
                    template = db.query(SQLTemplate).filter(SQLTemplate.id == template_id).first()
                    if template and template.refresh_rate > 0:
                        # Check if it's time to refresh
                        if not result.timestamp or \
                           (datetime.now() - result.timestamp).total_seconds() >= template.refresh_rate:
                            logger.info(f"Executing template {template_id}: {template.name}")
                            logger.info(f"SQL Query: {template.query}")
                            
                            # Execute the template
                            new_result = await self.execute_template(template)
                            self.results[template_id] = new_result
                            
                            # Format and broadcast the result
                            broadcast_data = {
                                "type": "template_result",
                                "template_id": template_id,
                                "result": {
                                    "data": new_result.data,
                                    "error": new_result.data.get("error"),
                                    "timestamp": new_result.timestamp.isoformat()
                                }
                            }
                            logger.info(f"Broadcasting result for template {template_id}: {broadcast_data}")
                            await websocket_manager.broadcast(template_id, broadcast_data)
            except Exception as e:
                logger.error(f"Error executing template {template_id}: {str(e)}")
                self.results[template_id] = ExecutionResult(
                    template_id,
                    error=str(e)
                )

    async def _cleanup_old_results(self):
        """Remove results older than max_results_age."""
        current_time = datetime.now()
        for template_id, result in list(self.results.items()):
            if (current_time - result.timestamp).total_seconds() > self.max_results_age:
                del self.results[template_id]

    async def execute_template(self, template: SQLTemplate) -> ExecutionResult:
        """Execute a single template and return the result."""
        try:
            logger.info(f"Executing SQL for template {template.id}: {template.name}")
            # Execute the SQL query
            result = await self.text2sql_service.execute_sql(template.query)
            logger.info(f"SQL execution result: {result}")
            
            # Create execution result
            execution_result = ExecutionResult(template.id, data=result)
            execution_result.template_info = {
                "name": template.name,
                "description": template.description,
                "refresh_rate": template.refresh_rate
            }
            
            return execution_result
        except Exception as e:
            logger.error(f"Error executing template {template.id}: {str(e)}")
            return ExecutionResult(template.id, error=str(e))

    def get_result(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get the latest result for a template."""
        result = self.results.get(template_id)
        if result:
            return result.to_dict()
        return None

# Global instance
scheduler = None  # Will be initialized in main.py 