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
        self.data = data
        self.error = error
        self.template_id = template_id
        self.template_info = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "error": self.error,
            "template_id": self.template_id,
            "template_info": self.template_info
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
            with TemplatesSessionLocal() as db:
                templates = db.query(SQLTemplate).all()
                for template in templates:
                    if template.refresh_rate > 0:  # Only schedule templates with refresh rate
                        self.results[template.id] = ExecutionResult(template.id)
                        self.results[template.id].template_info = {
                            "name": template.name,
                            "description": template.description,
                            "refresh_rate": template.refresh_rate
                        }
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            raise

    async def start(self):
        """Start the scheduler."""
        if not self.running:
            self.running = True
            asyncio.create_task(self._scheduler_loop())
            logger.info("Scheduler started")

    async def stop(self):
        """Stop the scheduler."""
        self.running = False
        logger.info("Scheduler stopped")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                await self._execute_templates()
                await self._cleanup_old_results()
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    async def _execute_templates(self):
        """Execute all templates that need to be refreshed."""
        for template_id, result in self.results.items():
            try:
                with TemplatesSessionLocal() as db:
                    template = db.query(SQLTemplate).filter(SQLTemplate.id == template_id).first()
                    if template and template.refresh_rate > 0:
                        # Check if it's time to refresh
                        if not result.timestamp or \
                           (datetime.now() - result.timestamp).total_seconds() >= template.refresh_rate:
                            # Execute the template
                            new_result = await self.execute_template(template)
                            self.results[template_id] = new_result
                            
                            # Broadcast the result
                            await websocket_manager.broadcast({
                                "type": "template_result",
                                "template_id": template_id,
                                "result": new_result.to_dict()
                            })
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
            # Execute the SQL query
            result = await self.text2sql_service.execute_sql(template.query)
            
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