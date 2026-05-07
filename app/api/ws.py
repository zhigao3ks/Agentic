"""WebSocket 流式问答端点。"""

import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.db.session import _get_session_factory
from app.services.streaming_agent import run_streaming_agent
from app.services.ws_manager import ws_manager

router = APIRouter()


@router.websocket("/api/chat/stream")
async def chat_stream(websocket: WebSocket):
    """WebSocket 流式问答端点。

    接收 JSON 消息：{"query": "...", "kb_id": "...", "session_id": "..."}
    推送事件：query_analyzed, retrieval_started, mcp_tool_call,
             mcp_tool_result, answer_delta, citation, done, error
    """
    session_id = str(uuid.uuid4())
    await ws_manager.connect(websocket, session_id)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"event": "error", "data": "Invalid JSON"})
                continue

            query = msg.get("query", "")
            kb_id = msg.get("kb_id", "")
            client_session_id = msg.get("session_id", session_id)

            if msg.get("action") == "cancel":
                await ws_manager.send_event(client_session_id,
                    type("Event", (), {"event": "done", "data": "cancelled", "model_dump": lambda: {"event": "done", "data": "cancelled"}})())
                continue

            if not query or not kb_id:
                await websocket.send_json({"event": "error", "data": "query and kb_id are required"})
                continue

            async with _get_session_factory()() as db:
                await run_streaming_agent(query, kb_id, client_session_id, db)

    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(websocket, session_id)
