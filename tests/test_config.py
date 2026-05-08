"""测试 app/core/config.py"""

from app.core.config import Settings


class TestSettings:
    def test_default_values(self):
        settings = Settings()
        assert settings.APP_NAME == "MCP-Agentic RAG Backend"
        assert settings.APP_VERSION == "0.1.0"
        assert settings.APP_ENV == "development"
        assert settings.APP_DEBUG is True

    def test_database_url_is_set(self):
        settings = Settings()
        # .env 存在时使用 SQLite，否则默认 PostgreSQL
        assert settings.DATABASE_URL and len(settings.DATABASE_URL) > 0

    def test_jwt_defaults(self):
        settings = Settings()
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 60

    def test_environment_override(self, monkeypatch):
        monkeypatch.setenv("APP_NAME", "Test App")
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
        settings = Settings()
        assert settings.APP_NAME == "Test App"
        assert settings.JWT_SECRET_KEY == "test-secret"

    def test_module_level_settings_instance(self):
        from app.core.config import settings
        assert settings.APP_NAME is not None
