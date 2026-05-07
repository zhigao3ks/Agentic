"""测试 MCP 权限控制。"""

import pytest

from app.mcp_client.permissions import check_permission, register_tool_permission


class TestMCPPermissions:
    def test_public_tool_accessible_by_user(self):
        from app.models.user import User, UserRole
        user = User(username="u", email="u@x.com", password_hash="h", role=UserRole.USER)
        assert check_permission("search_knowledge_base", user) is True

    def test_admin_tool_denied_for_user(self):
        from app.models.user import User, UserRole
        user = User(username="u", email="u@x.com", password_hash="h", role=UserRole.USER)
        assert check_permission("execute_readonly_sql", user) is False

    def test_admin_tool_allowed_for_admin(self):
        from app.models.user import User, UserRole
        user = User(username="a", email="a@x.com", password_hash="h", role=UserRole.ADMIN)
        assert check_permission("execute_readonly_sql", user) is True

    def test_unknown_tool_denied(self):
        from app.models.user import User, UserRole
        user = User(username="u", email="u@x.com", password_hash="h", role=UserRole.ADMIN)
        assert check_permission("dangerous_tool", user) is False

    def test_register_tool_permission(self):
        register_tool_permission("new_tool", "public")
        from app.models.user import User, UserRole
        user = User(username="u", email="u@x.com", password_hash="h", role=UserRole.USER)
        assert check_permission("new_tool", user) is True
