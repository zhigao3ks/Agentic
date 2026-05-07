"""MCP Tool 调用 —— 参数校验、超时控制、错误处理。"""

import asyncio

from app.core.exceptions import ValidationException
from app.mcp_client.registry import registry


async def call_tool(server_name: str, tool_name: str, arguments: dict, timeout: int | None = None) -> dict:
    """调用指定 MCP Server 上的工具。"""
    info = registry.get(server_name)
    if not info:
        raise ValidationException(detail=f"MCP Server not found: {server_name}")

    timeout = timeout or info.timeout_seconds

    session = await registry.connect(server_name)
    if not session:
        raise ValidationException(detail=f"Failed to connect to MCP Server: {server_name}")

    try:
        result = await asyncio.wait_for(
            session.call_tool(tool_name, arguments=arguments),
            timeout=timeout,
        )
        return {
            "content": [c.model_dump() if hasattr(c, "model_dump") else str(c) for c in result.content],
            "is_error": getattr(result, "isError", False),
        }
    except asyncio.TimeoutError:
        return {"content": [], "is_error": True, "error": f"Tool call timed out after {timeout}s"}
    except Exception as e:
        return {"content": [], "is_error": True, "error": str(e)}
