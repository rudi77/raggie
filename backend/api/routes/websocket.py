from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...services.websocket_manager import websocket_manager
from ...services.scheduler_service import scheduler
from typing import Dict, Any
import json

router = APIRouter()

@router.websocket("/api/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live updates"""
    try:
        # Connect with initial data from scheduler
        await websocket_manager.connect(websocket, scheduler.results)
        
        while True:
            try:
                # Handle incoming messages
                raw_message = await websocket.receive_text()
                try:
                    message = json.loads(raw_message)
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {raw_message}")
                    continue

                message_type = message.get("type")
                if message_type == "pong":
                    continue
                elif message_type == "get_results":
                    # Client requesting current results
                    for template_id, result in scheduler.results.items():
                        await websocket_manager.broadcast(template_id, result)
                else:
                    print(f"Unknown message type: {message_type}")

            except WebSocketDisconnect:
                raise  # Re-raise to handle in outer try-except
            except Exception as e:
                print(f"Error handling message: {str(e)}")
                # Don't disconnect on message handling errors
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket_manager.disconnect(websocket)
        try:
            await websocket.close()
        except Exception:
            pass 