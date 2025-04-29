from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...services.websocket_manager import websocket_manager
from ...services.scheduler_service import scheduler

router = APIRouter()

@router.websocket("/api/live")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live updates"""
    # Connect with initial data from scheduler
    await websocket_manager.connect(websocket, scheduler.results)
    
    try:
        while True:
            # Handle incoming messages (including pong responses)
            message = await websocket.receive_json()
            if message.get("type") == "pong":
                continue
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket_manager.disconnect(websocket) 