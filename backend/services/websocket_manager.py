from fastapi import WebSocket
from typing import Dict, Set, Any
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._health_check_task = None

    async def connect(self, websocket: WebSocket, initial_data: Dict[int, Any] = None):
        """Handle new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections.add(websocket)
            logger.info(f"New WebSocket connection accepted. Total connections: {len(self.active_connections)}")
            
            # Send initial data if provided
            if initial_data:
                for template_id, data in initial_data.items():
                    await self.broadcast(template_id, data)
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {str(e)}")
            try:
                await websocket.close()
            except Exception:
                pass
            raise

    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        try:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Remaining connections: {len(self.active_connections)}")
        except KeyError:
            logger.warning("Attempted to remove non-existent WebSocket connection")
        except Exception as e:
            logger.error(f"Error during WebSocket disconnection: {str(e)}")

    async def broadcast(self, template_id: int, data: dict):
        """Broadcast data to all connected clients"""
        try:
            # Format the message
            message = {
                "type": data.get("type", "template_result"),
                "template_id": template_id,
                "result": {
                    "data": data.get("data", {}),
                    "error": data.get("error"),
                    "timestamp": data.get("timestamp", datetime.now().isoformat())
                }
            }
            
            # Convert to JSON string
            json_message = json.dumps(message)
            logger.debug(f"Broadcasting message for template {template_id}: {json_message}")
            
            # Send to all connected clients
            disconnected = set()
            for connection in self.active_connections:
                try:
                    await connection.send_text(json_message)
                    logger.info(f"Message sent successfully to client")
                except Exception as e:
                    logger.error(f"Error sending message to client: {str(e)}")
                    # Mark failed connections for removal
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.active_connections.remove(connection)
                logger.info(f"Removed disconnected client. Remaining connections: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Error in broadcast: {str(e)}")

    async def start_health_check(self):
        """Start periodic health checks"""
        async def health_check():
            while True:
                logger.debug("Starting health check cycle")
                disconnected = set()
                for connection in self.active_connections:
                    try:
                        # Send ping message
                        await connection.send_json({"type": "ping"})
                        logger.debug("Sent ping to client")
                    except Exception as e:
                        logger.error(f"Error in health check for connection: {str(e)}")
                        disconnected.add(connection)
                
                # Clean up disconnected clients
                for connection in disconnected:
                    try:
                        self.active_connections.remove(connection)
                        logger.info(f"Removed unresponsive client. Remaining connections: {len(self.active_connections)}")
                    except Exception as e:
                        logger.error(f"Error removing connection: {str(e)}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
        
        self._health_check_task = asyncio.create_task(health_check())

    async def stop_health_check(self):
        """Stop health checks"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

    async def close_all(self):
        """Close all WebSocket connections"""
        logger.info(f"Closing all WebSocket connections. Current connections: {len(self.active_connections)}")
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.close()
                disconnected.add(connection)
                logger.info("Closed WebSocket connection")
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {str(e)}")
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)
        
        logger.info("All WebSocket connections closed")

# Global instance
websocket_manager = WebSocketManager() 