"""测试对话 API 端点。"""

import tempfile

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.db.session import init_db


@pytest_asyncio.fixture(autouse=True)
async def _setup():
    await init_db()
    # 设置 embedding 和 vector store
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


def _register_and_get_token(client):
    resp = client.post("/api/auth/register", json={
        "username": "chatuser", "email": "chat@x.com", "password": "testPass123",
    })
    return resp.json()["access_token"]


def _create_kb(client, token):
    resp = client.post("/api/kbs", json={"name": "Chat KB", "visibility": "team"},
                       headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


@pytest.mark.asyncio
class TestChatAPI:
    async def test_chat_returns_answer(self, client):
        token = _register_and_get_token(client)
        kb_id = _create_kb(client, token)
        headers = {"Authorization": f"Bearer {token}"}

        # 先上传文档以建索引
        from io import BytesIO
        client.post(
            f"/api/kbs/{kb_id}/documents/upload",
            files={"file": ("doc.txt", BytesIO(b"FastAPI is a Python framework."), "text/plain")},
            headers=headers,
        )

        resp = client.post("/api/chat", json={
            "query": "什么是 FastAPI？", "kb_id": kb_id,
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "session_id" in data

    async def test_chat_no_auth(self, client):
        resp = client.post("/api/chat", json={"query": "test", "kb_id": "dummy"})
        assert resp.status_code in (401, 403)

    async def test_get_session(self, client):
        token = _register_and_get_token(client)
        kb_id = _create_kb(client, token)
        headers = {"Authorization": f"Bearer {token}"}

        chat_resp = client.post("/api/chat", json={
            "query": "What is FastAPI?", "kb_id": kb_id,
        }, headers=headers)
        session_id = chat_resp.json()["session_id"]

        resp = client.get(f"/api/chat/sessions/{session_id}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["messages"]) >= 1
