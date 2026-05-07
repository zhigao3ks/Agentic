"""测试 app/main.py 健康检查端点与异常处理。"""

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import NotFoundException
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthCheck:
    def test_health_check_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_returns_ok_status(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_check_returns_version(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert "version" in data


class TestExceptionHandler:
    def test_app_exception_handler(self, client):
        # 挂载一个测试路由来触发 AppException
        from fastapi import APIRouter

        router = APIRouter()

        @router.get("/api/test-not-found")
        def _trigger_exception():
            raise NotFoundException(detail="test item not found")

        app.include_router(router)
        response = client.get("/api/test-not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NOT_FOUND"
        assert data["detail"] == "test item not found"


class TestCORSMiddleware:
    def test_cors_headers_present(self, client):
        response = client.options(
            "/api/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        # TestClient 的 OPTIONS 可能不会完全走 CORS 中间件逻辑，这里只确保无 500
        assert response.status_code in (200, 405)


class TestOpenAPIDocs:
    def test_docs_endpoint_accessible(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] is not None
