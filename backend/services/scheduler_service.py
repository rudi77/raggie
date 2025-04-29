import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..core.models import SQLTemplate
from .text2sql_service import Text2SQLService
from .websocket_manager import websocket_manager

class ExecutionResult:
    def __init__(self, data: Optional[dict] = None, error: Optional[str] = None):
        self.timestamp = datetime.now()
        self.data = data
        self.error = error
        self.template_id: Optional[int] = None
        self.template_info: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'error': self.error,
            'template_info': self.template_info
        }

class SchedulerService:
    def __init__(self, text2sql_service: Text2SQLService, check_interval: int = 1):
        self.results: Dict[int, ExecutionResult] = {}
        self.running = False
        self._task = None
        self.text2sql = text2sql_service
        self.check_interval = check_interval  # seconds
        self._cleanup_threshold = timedelta(hours=1)  # Keep results for 1 hour

    async def start(self):
        """Start the scheduler service"""
        if self.running:
            return
        
        self.running = True
        self._task = asyncio.create_task(self._run_scheduler())

    async def stop(self):
        """Stop the scheduler service"""
        self.running = False
        if self._task:
            await self._task

    def get_result(self, template_id: int) -> Optional[dict]:
        """Get the latest result for a template"""
        result = self.results.get(template_id)
        return result.to_dict() if result else None

    def _cleanup_old_results(self):
        """Remove results older than cleanup threshold"""
        now = datetime.now()
        to_remove = []
        for template_id, result in self.results.items():
            age = now - result.timestamp
            if age > self._cleanup_threshold:
                to_remove.append(template_id)
        
        for template_id in to_remove:
            del self.results[template_id]

    async def execute_template(self, template: SQLTemplate) -> ExecutionResult:
        """Execute a single template and return the result"""
        result = ExecutionResult()
        result.template_id = template.id
        result.template_info = {
            'source_question': template.source_question,
            'widget_type': template.widget_type.value,
            'refresh_rate': template.refresh_rate
        }
        
        try:
            # Execute the stored SQL query directly
            sql_result = await self.text2sql.execute_sql(template.query)
            result.data = sql_result
        except Exception as e:
            result.error = str(e)
        
        return result

    async def _run_scheduler(self):
        """Main scheduler loop"""
        db = SessionLocal()  # Create a single session for the loop
        try:
            while self.running:
                try:
                    # Refresh the session
                    db.rollback()
                    
                    # Get all templates
                    templates = db.query(SQLTemplate).all()
                    
                    # Execute each template
                    for template in templates:
                        try:
                            now = datetime.now()
                            
                            # Check if it's time to execute this template
                            if (template.last_execution is None or 
                                (now - template.last_execution).total_seconds() >= template.refresh_rate):
                                
                                # Execute the query
                                result = await self.execute_template(template)
                                self.results[template.id] = result
                                
                                # Update last_execution in database
                                template.last_execution = now
                                db.add(template)
                                db.commit()
                                
                                # Broadcast result to WebSocket clients
                                await websocket_manager.broadcast(template.id, result.to_dict())
                                
                        except Exception as e:
                            print(f"Error executing template {template.id}: {str(e)}")
                            db.rollback()  # Rollback on error
                    
                    # Cleanup old results periodically
                    self._cleanup_old_results()
                    
                except Exception as e:
                    print(f"Scheduler error: {str(e)}")
                    db.rollback()
                
                # Sleep for the configured interval
                await asyncio.sleep(self.check_interval)
        finally:
            db.close()  # Ensure the session is closed

# Note: Don't create the global instance here anymore since we need the text2sql service 