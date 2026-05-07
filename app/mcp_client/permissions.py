"""MCP 权限控制 —— 工具白名单和权限级别校验。"""

from app.models.user import User, UserRole

# tool → 所需最低权限级别
_PERMISSION_MAP: dict[str, str] = {
    "search_knowledge_base": "public",
    "get_document_detail": "user",
    "get_chunk_context": "user",
    "list_tables": "public",
    "describe_table": "user",
    "execute_readonly_sql": "admin",
    "list_files": "user",
    "read_file": "user",
}

# 允许调用的工具白名单
_TOOL_WHITELIST: set[str] = {
    "search_knowledge_base", "get_document_detail", "get_chunk_context",
    "list_tables", "describe_table", "execute_readonly_sql",
    "list_files", "read_file",
}

ROLE_HIERARCHY = {"public": 0, "user": 1, "admin": 2}


def check_permission(tool_name: str, user: User) -> bool:
    """检查用户是否有权调用指定工具。"""
    if tool_name not in _TOOL_WHITELIST:
        return False

    required = _PERMISSION_MAP.get(tool_name, "admin")
    required_level = ROLE_HIERARCHY.get(required, 2)

    user_role = user.role.value if hasattr(user.role, "value") else str(user.role)
    user_level = ROLE_HIERARCHY.get(user_role, 0)

    return user_level >= required_level


def register_tool_permission(tool_name: str, permission_level: str) -> None:
    """注册工具权限（用于 MCP Server 动态注册）。"""
    _PERMISSION_MAP[tool_name] = permission_level
    _TOOL_WHITELIST.add(tool_name)
