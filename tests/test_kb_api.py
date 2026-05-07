"""测试 app/api/knowledge_base.py 端点。"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.db.session import init_db


@pytest_asyncio.fixture(autouse=True)
async def _init_tables():
    await init_db()
    yield


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def _register(client, username="kbuser", email="kbuser@x.com", password="testPass123"):
    return client.post("/api/auth/register", json={
        "username": username, "email": email, "password": password,
    })


def _token(client):
    return _register(client).json()["access_token"]


def _auth_header(client):
    return {"Authorization": f"Bearer {_token(client)}"}


@pytest.mark.asyncio
class TestCreateKBAPI:
    async def test_create_kb_success(self, client):
        resp = client.post("/api/kbs", json={"name": "My KB", "visibility": "team"},
                           headers=_auth_header(client))
        assert resp.status_code == 201
        assert resp.json()["name"] == "My KB"

    async def test_create_kb_no_auth(self, client):
        resp = client.post("/api/kbs", json={"name": "KB"})
        assert resp.status_code in (401, 403)

    async def test_create_kb_empty_name(self, client):
        resp = client.post("/api/kbs", json={"name": ""}, headers=_auth_header(client))
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestListKBsAPI:
    async def test_list_kbs(self, client):
        headers = _auth_header(client)
        client.post("/api/kbs", json={"name": "KB1"}, headers=headers)
        client.post("/api/kbs", json={"name": "KB2", "visibility": "public"}, headers=headers)

        resp = client.get("/api/kbs", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_list_kbs_no_auth(self, client):
        resp = client.get("/api/kbs")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestGetKBAPI:
    async def test_get_kb_by_id(self, client):
        headers = _auth_header(client)
        created = client.post("/api/kbs", json={"name": "Detail KB"}, headers=headers)
        kb_id = created.json()["id"]

        resp = client.get(f"/api/kbs/{kb_id}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Detail KB"

    async def test_get_kb_not_found(self, client):
        import uuid
        resp = client.get(f"/api/kbs/{uuid.uuid4()}", headers=_auth_header(client))
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestUpdateKBAPI:
    async def test_update_kb(self, client):
        headers = _auth_header(client)
        created = client.post("/api/kbs", json={"name": "Old"}, headers=headers)
        kb_id = created.json()["id"]

        resp = client.put(f"/api/kbs/{kb_id}", json={"name": "Updated"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated"


@pytest.mark.asyncio
class TestDeleteKBAPI:
    async def test_delete_kb(self, client):
        headers = _auth_header(client)
        created = client.post("/api/kbs", json={"name": "To Delete"}, headers=headers)
        kb_id = created.json()["id"]

        resp = client.delete(f"/api/kbs/{kb_id}", headers=headers)
        assert resp.status_code == 204

        # 确认已删除
        get_resp = client.get(f"/api/kbs/{kb_id}", headers=headers)
        assert get_resp.status_code == 404
