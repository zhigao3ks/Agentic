"""测试 Agent API 端点。"""

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


def _register(client):
    resp = client.post("/api/auth/register", json={
        "username": "agentapi", "email": "agentapi@x.com", "password": "testPass123",
    })
    return resp.json()["access_token"]


def _create_kb(client, token):
    resp = client.post("/api/kbs", json={"name": "Agent KB", "visibility": "team"},
                       headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


@pytest.mark.asyncio
class TestAgentAPI:
    async def test_agent_chat_returns_answer(self, client):
        token = _register(client)
        kb_id = _create_kb(client, token)
        headers = {"Authorization": f"Bearer {token}"}

        # 上传文档建立索引
        from io import BytesIO
        client.post(
            f"/api/kbs/{kb_id}/documents/upload",
            files={"file": ("doc.txt", BytesIO(b"Python is a programming language."), "text/plain")},
            headers=headers,
        )

        resp = client.post("/api/agent/chat", json={
            "query": "什么是 Python？", "kb_id": kb_id,
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "answer" in data
        assert "agent_run_id" in data
        assert "verification" in data

    async def test_agent_chat_no_auth(self, client):
        resp = client.post("/api/agent/chat", json={"query": "test", "kb_id": "dummy"})
        assert resp.status_code in (401, 403)
