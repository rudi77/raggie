import asyncio
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..core.database import SessionLocal
from ..core.models import SQLTemplate
from .text2sql_service import Text2SQLService

class SchedulerService:
    def __init__(self, text2sql_service: Text2SQLService):
        self.results: Dict[int, Any] = {}  # template_id -> latest result
        self.running = False
        self._task = None
        self.text2sql = text2sql_service

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

    def get_result(self, template_id: int) -> Any:
        """Get the latest result for a template"""
        return self.results.get(template_id)

    async def execute_template(self, template: SQLTemplate) -> dict:
        """Execute a single template and return the result"""
        try:
            # Execute the stored SQL query directly
            result = await self.text2sql.execute_sql(template.query)
            
            return {
                'data': result,
                'timestamp': datetime.now(),
                'error': None
            }
        except Exception as e:
            return {
                'data': None,
                'timestamp': datetime.now(),
                'error': str(e)
            }

    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                # Get all templates
                db = SessionLocal()
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
                            
                            # TODO: Broadcast result to WebSocket clients
                            
                    except Exception as e:
                        print(f"Error executing template {template.id}: {str(e)}")
                        
                db.close()
                
            except Exception as e:
                print(f"Scheduler error: {str(e)}")
            
            # Sleep for a short interval before next check
            await asyncio.sleep(1)

# Note: Don't create the global instance here anymore since we need the text2sql service 