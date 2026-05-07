"""WebSocket 连接管理器。"""

from fastapi import WebSocket


class WSManager:
    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        if session_id not in self._connections:
            self._connections[session_id] = []
        self._connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str) -> None:
        if session_id in self._connections:
            self._connections[session_id] = [ws for ws in self._connections[session_id] if ws != websocket]
            if not self._connections[session_id]:
                del self._connections[session_id]

    async def send_event(self, session_id: str, event) -> None:
        """发送事件到指定会话的所有连接。"""
        if session_id in self._connections:
            dead = []
            for ws in self._connections[session_id]:
                try:
                    await ws.send_json(event.model_dump())
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.disconnect(ws, session_id)

    async def broadcast(self, event) -> None:
        """广播事件到所有会话。"""
        for session_id in list(self._connections.keys()):
            await self.send_event(session_id, event)


ws_manager = WSManager()
