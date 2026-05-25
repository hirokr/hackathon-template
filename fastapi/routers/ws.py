# routers/ws.py — WebSocket endpoints
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from core.deps import get_current_user
from models.user import User

router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        self.active[user_id] = websocket

    def disconnect(self, user_id: str) -> None:
        self.active.pop(user_id, None)

    async def send_personal(self, user_id: str, message: str) -> None:
        socket = self.active.get(user_id)
        if socket:
            await socket.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user: User = Depends(get_current_user)):
    await manager.connect(websocket, current_user.id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal(current_user.id, data)
    except WebSocketDisconnect:
        manager.disconnect(current_user.id)
