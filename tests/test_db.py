"""测试 app/db/session.py 和 app/db/base.py"""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class TestDatabaseSession:
    @pytest.mark.asyncio
    async def test_get_db_returns_async_session(self):
        from app.db.session import get_db

        gen = get_db()
        session = await anext(gen)
        assert isinstance(session, AsyncSession)

    @pytest.mark.asyncio
    async def test_session_can_execute_query(self):
        from app.db.session import get_db

        gen = get_db()
        session = await anext(gen)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        from app.db.session import _get_engine, init_db

        await init_db()

        async with _get_engine().connect() as conn:
            tables = await conn.run_sync(lambda c: list(c.dialect.get_table_names(c)))
        assert "users" in tables
        assert "knowledge_bases" in tables
        assert "documents" in tables
        assert "chunks" in tables
        assert "chat_sessions" in tables
        assert "chat_messages" in tables
        assert "agent_runs" in tables
        assert "mcp_servers" in tables
        assert "mcp_tools" in tables
        assert "mcp_tool_calls" in tables
