"""MCP 管理 API 路由。"""

import time
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.mcp_client import permissions, tool_caller, tool_discovery
from app.mcp_client.call_logger import log_tool_call
from app.mcp_client.registry import registry
from app.models.user import User
from app.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/api/mcp", tags=["mcp"])


@router.get("/servers")
async def list_servers(user: User = Depends(get_current_user_dependency)):
    """列出已注册的 MCP Server。"""
    servers = registry.list_servers()
    return [
        {"name": s.name, "transport": s.transport, "endpoint": s.endpoint, "enabled": s.enabled}
        for s in servers
    ]


@router.get("/tools")
async def list_tools(user: User = Depends(get_current_user_dependency)):
    """列出所有可用 MCP 工具。"""
    tools = await tool_discovery.list_all_tools()
    return {"tools": tools}


@router.post("/tools/refresh")
async def refresh_tools(user: User = Depends(get_current_user_dependency)):
    """刷新工具列表（重新从 MCP Server 获取）。"""
    tools = []
    for info in registry.list_servers():
        if info.enabled:
            await registry.disconnect(info.name)
            discovered = await tool_discovery.discover_tools(info.name)
            for t in discovered:
                t["server_name"] = info.name
            tools.extend(discovered)
    return {"tools": tools}


@router.post("/tools/call")
async def call_tool_endpoint(
    body: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    """调用指定 MCP 工具（需认证和权限校验）。"""
    server_name = body.get("server", "")
    tool_name = body.get("tool", "")
    arguments = body.get("arguments", {})

    if not permissions.check_permission(tool_name, user):
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException(detail=f"Permission denied for tool: {tool_name}")

    start = time.monotonic()
    result = await tool_caller.call_tool(server_name, tool_name, arguments)
    latency_ms = int((time.monotonic() - start) * 1000)

    status = "error" if result.get("is_error") else "success"
    await log_tool_call(db, tool_name, arguments, result, status, latency_ms)

    return {"server": server_name, "tool": tool_name, "result": result, "latency_ms": latency_ms}
