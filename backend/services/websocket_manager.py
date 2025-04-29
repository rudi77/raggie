from fastapi import WebSocket
from typing import Dict, Set, Any
import json
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._health_check_task = None

    async def connect(self, websocket: WebSocket, initial_data: Dict[int, Any] = None):
        """Handle new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Send initial data if provided
        if initial_data:
            for template_id, data in initial_data.items():
                await self.broadcast(template_id, data)

    async def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        self.active_connections.remove(websocket)

    async def broadcast(self, template_id: int, data: dict):
        """Broadcast data to all connected clients"""
        message = {
            "template_id": template_id,
            "data": data
        }
        
        # Convert to JSON string
        json_message = json.dumps(message)
        
        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(json_message)
            except Exception:
                # Mark failed connections for removal
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections.remove(connection)

    async def start_health_check(self):
        """Start periodic health checks"""
        async def health_check():
            while True:
                disconnected = set()
                for connection in self.active_connections:
                    try:
                        await connection.send_json({"type": "ping"})
                    except Exception:
                        disconnected.add(connection)
                
                # Clean up disconnected clients
                for connection in disconnected:
                    self.active_connections.remove(connection)
                
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

# Global instance
websocket_manager = WebSocketManager() 