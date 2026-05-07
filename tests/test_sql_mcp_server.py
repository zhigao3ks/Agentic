"""测试 SQL Query MCP Server 工具。"""

import json
import os
import sqlite3
import tempfile

import pytest
import pytest_asyncio


@pytest.fixture
def test_db(monkeypatch):
    """创建临时 SQLite 数据库并插入测试数据，monkeypatch 模块 DB 路径。"""
    tmp = tempfile.mktemp(suffix=".db")
    conn = sqlite3.connect(tmp)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@x.com')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@x.com')")
    conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL)")
    conn.execute("INSERT INTO orders VALUES (1, 1, 99.9)")
    conn.commit()
    conn.close()

    monkeypatch.setattr("app.mcp_servers.sql_query.server.DEFAULT_DB_PATH", tmp)
    yield tmp
    os.unlink(tmp)


@pytest.mark.asyncio
class TestListTables:
    async def test_list_tables(self, test_db):
        from app.mcp_servers.sql_query.server import _list_tables

        result = await _list_tables()
        data = json.loads(result[0].text)
        table_names = [t["table_name"] for t in data["tables"]]
        assert "users" in table_names
        assert "orders" in table_names

    async def test_row_counts(self, test_db):
        from app.mcp_servers.sql_query.server import _list_tables

        result = await _list_tables()
        data = json.loads(result[0].text)
        for t in data["tables"]:
            if t["table_name"] == "users":
                assert t["row_count"] == 2


@pytest.mark.asyncio
class TestDescribeTable:
    async def test_describe_table(self, test_db):
        from app.mcp_servers.sql_query.server import _describe_table

        result = await _describe_table({"table_name": "users"})
        data = json.loads(result[0].text)
        assert data["table_name"] == "users"
        col_names = [c["name"] for c in data["columns"]]
        assert "id" in col_names
        assert "name" in col_names
        assert len(data["sample_rows"]) >= 1

    async def test_describe_nonexistent(self, test_db):
        from app.mcp_servers.sql_query.server import _describe_table

        result = await _describe_table({"table_name": "ghost"})
        data = json.loads(result[0].text)
        assert "error" in data

    async def test_invalid_table_name(self, test_db):
        from app.mcp_servers.sql_query.server import handle_call_tool

        result = await handle_call_tool("describe_table", {"table_name": "users; DROP TABLE users"})
        data = json.loads(result[0].text)
        assert "error" in data


@pytest.mark.asyncio
class TestExecuteSQL:
    async def test_select_all(self, test_db):
        from app.mcp_servers.sql_query.server import _execute_sql

        result = await _execute_sql({"sql_query": "SELECT * FROM users"})
        data = json.loads(result[0].text)
        assert data["row_count"] == 2
        assert data["columns"] == ["id", "name", "email"]

    async def test_select_with_condition(self, test_db):
        from app.mcp_servers.sql_query.server import _execute_sql

        result = await _execute_sql({"sql_query": "SELECT name FROM users WHERE id = 1"})
        data = json.loads(result[0].text)
        assert data["row_count"] == 1
        assert data["rows"][0][0] == "Alice"

    async def test_auto_limit(self, test_db):
        from app.mcp_servers.sql_query.server import _execute_sql

        result = await _execute_sql({"sql_query": "SELECT * FROM users", "limit": 1})
        data = json.loads(result[0].text)
        assert data["row_count"] == 1

    async def test_blocks_drop(self, test_db):
        from app.mcp_servers.sql_query.server import handle_call_tool

        result = await handle_call_tool("execute_readonly_sql", {"sql_query": "DROP TABLE users"})
        data = json.loads(result[0].text)
        assert "error" in data

    async def test_blocks_delete(self, test_db):
        from app.mcp_servers.sql_query.server import handle_call_tool

        result = await handle_call_tool("execute_readonly_sql", {"sql_query": "DELETE FROM users"})
        data = json.loads(result[0].text)
        assert "error" in data

    async def test_blocks_update(self, test_db):
        from app.mcp_servers.sql_query.server import handle_call_tool

        result = await handle_call_tool("execute_readonly_sql", {"sql_query": "UPDATE users SET name='X'"})
        data = json.loads(result[0].text)
        assert "error" in data

    async def test_blocks_insert(self, test_db):
        from app.mcp_servers.sql_query.server import handle_call_tool

        result = await handle_call_tool("execute_readonly_sql", {"sql_query": "INSERT INTO users VALUES (3, 'X', 'x@x.com')"})
        data = json.loads(result[0].text)
        assert "error" in data

    async def test_empty_sql(self, test_db):
        from app.mcp_servers.sql_query.server import handle_call_tool

        result = await handle_call_tool("execute_readonly_sql", {"sql_query": ""})
        data = json.loads(result[0].text)
        assert "error" in data


@pytest.mark.asyncio
class TestToolListing:
    async def test_list_tools_returns_three(self):
        from app.mcp_servers.sql_query.server import handle_list_tools

        tools = await handle_list_tools()
        assert len(tools) == 3
        tool_names = [t.name for t in tools]
        assert "list_tables" in tool_names
        assert "describe_table" in tool_names
        assert "execute_readonly_sql" in tool_names


@pytest.mark.asyncio
class TestDispatch:
    async def test_dispatch_to_list_tables(self, test_db):
        from app.mcp_servers.sql_query.server import handle_call_tool

        result = await handle_call_tool("list_tables", {})
        data = json.loads(result[0].text)
        assert "tables" in data

    async def test_dispatch_unknown_tool(self, test_db):
        from app.mcp_servers.sql_query.server import handle_call_tool

        result = await handle_call_tool("dangerous_tool", {})
        data = json.loads(result[0].text)
        assert "error" in data
