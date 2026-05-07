"""SQL Query MCP Server —— 提供 3 个工具：list_tables、describe_table、execute_readonly_sql。

安全要求：
- 只允许 SELECT 查询
- 禁止 DROP/DELETE/UPDATE/INSERT/ALTER/TRUNCATE 等危险操作
- 限制返回行数（默认 100，最大 1000）
- 查询超时（默认 5 秒）
- 参数化查询，禁止拼接未校验的用户输入

启动方式：python -m app.mcp_servers.sql_query.server
"""

import asyncio
import json
import os
import re
import sqlite3

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("sql-query-mcp")

DEFAULT_DB_PATH = os.environ.get("SQL_QUERY_DB_PATH", "storage/agentic_rag.db")
MAX_ROWS = 1000
DEFAULT_ROWS = 100
QUERY_TIMEOUT = 5

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
    "CREATE", "REPLACE", "GRANT", "REVOKE",
]


def _validate_sql(sql: str) -> None:
    """校验 SQL 语句安全性：只允许 SELECT，禁止危险关键字。"""
    stripped = sql.strip().upper()
    if not stripped.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")

    # 检查禁止关键字（用词边界匹配防止误判）
    for kw in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{kw}\b", stripped):
            raise ValueError(f"Forbidden SQL keyword: {kw}")


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DEFAULT_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_tables",
            description="列出数据库中所有表名及行数估算",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="describe_table",
            description="获取指定表的列名、类型、是否可空等 schema 信息",
            inputSchema={
                "type": "object",
                "properties": {"table_name": {"type": "string", "description": "表名"}},
                "required": ["table_name"],
            },
        ),
        Tool(
            name="execute_readonly_sql",
            description="安全执行只读 SQL 查询（仅允许 SELECT）",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {"type": "string", "description": "SQL SELECT 查询语句"},
                    "limit": {"type": "integer", "description": "返回行数上限", "default": 100},
                },
                "required": ["sql_query"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "list_tables":
            return await _list_tables()
        elif name == "describe_table":
            return await _describe_table(arguments)
        elif name == "execute_readonly_sql":
            return await _execute_sql(arguments)
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False))]
    except ValueError as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, ensure_ascii=False))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Query failed: {str(e)}"}, ensure_ascii=False))]


async def _list_tables() -> list[TextContent]:
    loop = asyncio.get_running_loop()
    conn = await loop.run_in_executor(None, _get_connection)
    try:
        cursor = await loop.run_in_executor(None, conn.execute,
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = await loop.run_in_executor(None, cursor.fetchall)

        result = []
        for row in tables:
            table_name = row["name"]
            cnt_cursor = await loop.run_in_executor(None, conn.execute, f"SELECT COUNT(*) FROM [{table_name}]")
            row_count = await loop.run_in_executor(None, cnt_cursor.fetchone)
            result.append({"table_name": table_name, "row_count": row_count[0] if row_count else 0})

        return [TextContent(type="text", text=json.dumps({"tables": result}, ensure_ascii=False))]
    finally:
        await loop.run_in_executor(None, conn.close)


async def _describe_table(args: dict) -> list[TextContent]:
    table_name = args.get("table_name", "")

    # 校验表名安全：只允许字母、数字、下划线
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
        raise ValueError(f"Invalid table name: {table_name}")

    loop = asyncio.get_running_loop()
    conn = await loop.run_in_executor(None, _get_connection)
    try:
        cursor = await loop.run_in_executor(None, conn.execute, f"PRAGMA table_info([{table_name}])")
        columns = await loop.run_in_executor(None, cursor.fetchall)

        if not columns:
            return [TextContent(type="text", text=json.dumps({"error": f"Table not found: {table_name}"}, ensure_ascii=False))]

        result = []
        for col in columns:
            result.append({
                "name": col["name"],
                "type": col["type"],
                "notnull": bool(col["notnull"]),
                "pk": bool(col["pk"]),
            })

        # 获取示例数据（前 3 行）
        sample_cursor = await loop.run_in_executor(None, conn.execute, f"SELECT * FROM [{table_name}] LIMIT 3")
        samples = await loop.run_in_executor(None, sample_cursor.fetchall)
        sample_rows = [[str(v) for v in row] for row in samples]

        return [TextContent(type="text", text=json.dumps({
            "table_name": table_name,
            "columns": result,
            "sample_rows": sample_rows,
        }, ensure_ascii=False))]
    finally:
        await loop.run_in_executor(None, conn.close)


async def _execute_sql(args: dict) -> list[TextContent]:
    sql = args.get("sql_query", "").strip()
    limit = min(int(args.get("limit", DEFAULT_ROWS)), MAX_ROWS)

    if not sql:
        raise ValueError("SQL query is required")

    _validate_sql(sql)

    # 自动添加 LIMIT（如果查询中没有）
    if "LIMIT" not in sql.upper():
        sql = f"{sql.rstrip(';')} LIMIT {limit}"

    loop = asyncio.get_running_loop()
    conn = await loop.run_in_executor(None, _get_connection)
    try:
        cursor = await asyncio.wait_for(
            loop.run_in_executor(None, conn.execute, sql),
            timeout=QUERY_TIMEOUT,
        )
        rows = await loop.run_in_executor(None, cursor.fetchall)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []

        return [TextContent(type="text", text=json.dumps({
            "columns": columns,
            "rows": [[str(v) for v in row] for row in rows],
            "row_count": len(rows),
        }, ensure_ascii=False))]
    except asyncio.TimeoutError:
        return [TextContent(type="text", text=json.dumps({"error": f"Query timed out after {QUERY_TIMEOUT}s"}, ensure_ascii=False))]
    finally:
        await loop.run_in_executor(None, conn.close)


def main():
    """启动 SQL Query MCP Server（stdio 模式）。"""
    async def _run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    main()
