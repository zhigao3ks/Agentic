"""MCP Tool 发现 —— 获取 Server 暴露的工具列表和参数 schema。"""

from app.mcp_client.registry import registry


async def discover_tools(server_name: str) -> list[dict]:
    """连接 MCP Server 并获取工具列表。"""
    try:
        session = await registry.connect(server_name)
        if not session:
            return []

        result = await session.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in result.tools
        ]
    except Exception:
        return []


async def list_all_tools() -> list[dict]:
    """列出所有已注册 Server 的工具。"""
    all_tools = []
    for info in registry.list_servers():
        if info.enabled:
            tools = await discover_tools(info.name)
            for t in tools:
                t["server_name"] = info.name
            all_tools.extend(tools)
    return all_tools
