"""测试 MCP API 端点。"""

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


def _register(client):
    resp = client.post("/api/auth/register", json={
        "username": "mcpuser", "email": "mcp@x.com", "password": "testPass123",
    })
    return resp.json()["access_token"]


def _register_admin(client):
    from app.models.user import User, UserRole
    resp = client.post("/api/auth/register", json={
        "username": "adminuser", "email": "admin@x.com", "password": "testPass123",
    })
    return resp.json()["access_token"]


@pytest.mark.asyncio
class TestMCPServersAPI:
    async def test_list_servers(self, client):
        token = _register(client)
        from app.mcp_client.registry import registry
        registry.register("test-mcp", "stdio", "python test")

        resp = client.get("/api/mcp/servers", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        servers = resp.json()
        assert len(servers) >= 1

    async def test_list_servers_no_auth(self, client):
        resp = client.get("/api/mcp/servers")
        assert resp.status_code in (401, 403)


@pytest.mark.asyncio
class TestMCPToolsAPI:
    async def test_list_tools(self, client):
        token = _register(client)
        resp = client.get("/api/mcp/tools", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert "tools" in resp.json()

    async def test_call_tool_permission_denied(self, client):
        token = _register(client)
        resp = client.post("/api/mcp/tools/call", json={
            "server": "test", "tool": "execute_readonly_sql", "arguments": {"sql": "SELECT 1"},
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in (403, 422)

    async def test_call_tool_unknown_server(self, client):
        token = _register_admin(client)
        resp = client.post("/api/mcp/tools/call", json={
            "server": "nonexistent", "tool": "search_knowledge_base", "arguments": {},
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422
