"""测试 WebSocket 端点。"""

import json
import tempfile

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.db.session import init_db


@pytest_asyncio.fixture(autouse=True)
async def _setup():
    await init_db()
    from app.services.dependencies import set_embedding_service, set_vector_store
    from app.services.embedding.fake import FakeEmbeddingService
    from app.services.vector_store.chroma_store import ChromaVectorStore
    tmp = tempfile.mkdtemp()
    set_embedding_service(FakeEmbeddingService(dimension=128))
    set_vector_store(ChromaVectorStore(persist_dir=tmp))
    yield
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.mark.asyncio
class TestWebSocketStream:
    async def test_ws_stream_events(self, client):
        """通过 TestClient 的 WebSocket 测试流式事件。"""
        with client.websocket_connect("/api/chat/stream") as ws:
            ws.send_text(json.dumps({
                "query": "什么是 Python？",
                "kb_id": "dummy-kb-id",
            }))

            events = []
            try:
                while True:
                    data = ws.receive_json()
                    events.append(data["event"])
                    if data["event"] == "done" or data["event"] == "error":
                        break
            except Exception:
                pass

            assert len(events) >= 2  # 至少 received query_analyzed + done/error
            assert "query_analyzed" in events

    async def test_ws_invalid_json(self, client):
        with client.websocket_connect("/api/chat/stream") as ws:
            ws.send_text("not json")
            data = ws.receive_json()
            assert data["event"] == "error"

    async def test_ws_missing_query(self, client):
        with client.websocket_connect("/api/chat/stream") as ws:
            ws.send_text(json.dumps({"kb_id": "x"}))
            data = ws.receive_json()
            assert data["event"] == "error"
