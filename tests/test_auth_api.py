"""测试 app/api/auth.py 端点。"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.db.session import init_db


@pytest_asyncio.fixture(autouse=True)
async def _init_tables():
    """API 测试前创建所有表。"""
    await init_db()
    yield


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.mark.asyncio
class TestRegisterAPI:
    async def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "username": "apiuser",
            "email": "apiuser@example.com",
            "password": "securePass123",
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "apiuser"

    async def test_register_missing_fields(self, client):
        response = client.post("/api/auth/register", json={"username": "x"})
        assert response.status_code == 422

    async def test_register_duplicate_username(self, client):
        payload = {"username": "dup", "email": "dup1@x.com", "password": "12345678"}
        client.post("/api/auth/register", json=payload)
        payload2 = {"username": "dup", "email": "dup2@x.com", "password": "87654321"}
        response = client.post("/api/auth/register", json=payload2)
        assert response.status_code == 409
        assert response.json()["error_code"] == "CONFLICT"


@pytest.mark.asyncio
class TestLoginAPI:
    @pytest_asyncio.fixture
    async def _registered(self, client):
        client.post("/api/auth/register", json={
            "username": "loginapi",
            "email": "loginapi@x.com",
            "password": "testPass123",
        })

    async def test_login_success(self, client, _registered):
        response = client.post("/api/auth/login", json={
            "username": "loginapi",
            "password": "testPass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_login_wrong_password(self, client, _registered):
        response = client.post("/api/auth/login", json={
            "username": "loginapi",
            "password": "wrong",
        })
        assert response.status_code == 401


@pytest.mark.asyncio
class TestMeAPI:
    async def test_me_with_valid_token(self, client):
        reg = client.post("/api/auth/register", json={
            "username": "meuser",
            "email": "me@x.com",
            "password": "mepass123",
        })
        token = reg.json()["access_token"]

        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "meuser"

    async def test_me_without_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code in (401, 403)  # HTTPBearer 取决于 Starlette 版本

    async def test_me_with_invalid_token(self, client):
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert response.status_code == 401
