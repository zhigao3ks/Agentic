"""MCP 调用日志 —— 记录工具调用到数据库。"""

import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mcp import MCPToolCall, MCPToolCallStatus


async def log_tool_call(
    db: AsyncSession,
    tool_name: str,
    tool_input: dict,
    tool_output: dict,
    status: str,
    latency_ms: int,
    session_id: uuid.UUID | None = None,
) -> MCPToolCall:
    """记录一次 MCP 工具调用。"""
    call = MCPToolCall(
        session_id=session_id,
        tool_name=tool_name,
        tool_input=tool_input,
        tool_output=tool_output,
        status=MCPToolCallStatus(status) if status in ("pending", "success", "error", "timeout") else MCPToolCallStatus.ERROR,
        latency_ms=latency_ms,
    )
    db.add(call)
    await db.flush()
    return call
