"""测试 app/api/document.py 端点。"""

import tempfile
from io import BytesIO

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


def _register_and_get_token(client):
    resp = client.post("/api/auth/register", json={
        "username": "docadmin", "email": "docadmin@x.com", "password": "testPass123",
    })
    return resp.json()["access_token"]


def _create_kb(client, token):
    resp = client.post("/api/kbs", json={"name": "Doc KB", "visibility": "team"},
                       headers={"Authorization": f"Bearer {token}"})
    return resp.json()["id"]


def _make_file(content=b"hello world", filename="test.txt"):
    return {"file": (filename, BytesIO(content), "text/plain")}


@pytest.mark.asyncio
class TestUploadAPI:
    async def test_upload_txt_success(self, client):
        token = _register_and_get_token(client)
        kb_id = _create_kb(client, token)

        resp = client.post(
            f"/api/kbs/{kb_id}/documents/upload",
            files=_make_file(b"hello world", "readme.txt"),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["filename"] == "readme.txt"
        assert data["file_type"] == "txt"
        assert data["status"] == "ready"  # 流水线同步处理后状态为 ready

    async def test_upload_no_auth(self, client):
        token = _register_and_get_token(client)
        kb_id = _create_kb(client, token)

        resp = client.post(f"/api/kbs/{kb_id}/documents/upload", files=_make_file())
        assert resp.status_code in (401, 403)

    async def test_upload_invalid_file_type(self, client):
        token = _register_and_get_token(client)
        kb_id = _create_kb(client, token)

        resp = client.post(
            f"/api/kbs/{kb_id}/documents/upload",
            files={"file": ("bad.exe", BytesIO(b"x"), "application/octet-stream")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestListDocsAPI:
    async def test_list_documents(self, client):
        token = _register_and_get_token(client)
        kb_id = _create_kb(client, token)
        headers = {"Authorization": f"Bearer {token}"}

        client.post(f"/api/kbs/{kb_id}/documents/upload", files=_make_file(b"a", "a.txt"), headers=headers)
        client.post(f"/api/kbs/{kb_id}/documents/upload", files=_make_file(b"b", "b.txt"), headers=headers)

        resp = client.get(f"/api/kbs/{kb_id}/documents", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2


@pytest.mark.asyncio
class TestGetDocAPI:
    async def test_get_document(self, client):
        token = _register_and_get_token(client)
        kb_id = _create_kb(client, token)
        headers = {"Authorization": f"Bearer {token}"}

        upload_resp = client.post(f"/api/kbs/{kb_id}/documents/upload",
                                  files=_make_file(b"content", "doc.txt"), headers=headers)
        doc_id = upload_resp.json()["id"]

        resp = client.get(f"/api/documents/{doc_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["filename"] == "doc.txt"

    async def test_get_document_not_found(self, client):
        import uuid
        token = _register_and_get_token(client)
        resp = client.get(f"/api/documents/{uuid.uuid4()}",
                          headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestDeleteDocAPI:
    async def test_delete_document(self, client):
        token = _register_and_get_token(client)
        kb_id = _create_kb(client, token)
        headers = {"Authorization": f"Bearer {token}"}

        upload_resp = client.post(f"/api/kbs/{kb_id}/documents/upload",
                                  files=_make_file(b"x", "delme.txt"), headers=headers)
        doc_id = upload_resp.json()["id"]

        resp = client.delete(f"/api/documents/{doc_id}", headers=headers)
        assert resp.status_code == 204

        get_resp = client.get(f"/api/documents/{doc_id}", headers=headers)
        assert get_resp.status_code == 404
