from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...services.websocket_manager import websocket_manager
from ...services.scheduler_service import scheduler
from typing import Dict, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["websocket"]
)

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live updates"""
    try:
        # Connect with initial data from scheduler if available
        initial_data = scheduler.results if scheduler and hasattr(scheduler, 'results') else {}
        await websocket_manager.connect(websocket, initial_data)
        logger.info("WebSocket client connected and received initial data")
        
        while True:
            try:
                # Handle incoming messages
                raw_message = await websocket.receive_text()
                try:
                    message = json.loads(raw_message)
                    logger.debug(f"Received WebSocket message: {message}")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {raw_message}")
                    continue

                message_type = message.get("type")
                if message_type == "ping":
                    # Respond to ping with pong
                    await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
                    logger.debug("Responded to ping with pong")
                elif message_type == "pong":
                    # Client responded to our ping
                    logger.debug("Received pong from client")
                elif message_type == "get_results":
                    # Client requesting current results
                    logger.info("Client requested current results")
                    if scheduler and hasattr(scheduler, 'results'):
                        for template_id, result in scheduler.results.items():
                            await websocket_manager.broadcast(template_id, result)
                else:
                    logger.warning(f"Unknown message type: {message_type}")

            except WebSocketDisconnect:
                raise  # Re-raise to handle in outer try-except
            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
                # Don't disconnect on message handling errors
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket_manager.disconnect(websocket)
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass 