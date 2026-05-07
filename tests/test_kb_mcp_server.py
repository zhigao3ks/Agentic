"""测试 Knowledge Base MCP Server 工具。"""

import json
import tempfile

import pytest
import pytest_asyncio

from app.db.session import _get_session_factory, init_db


@pytest_asyncio.fixture
async def s():
    await init_db()
    async with _get_session_factory()() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def setup_kb(s):
    from app.models.chunk import Chunk
    from app.models.document import Document
    from app.models.knowledge_base import KnowledgeBase
    from app.models.user import User

    u = User(username="mcpkbuser", email="mcpkb@x.com", password_hash="h")
    s.add(u)
    await s.flush()

    kb = KnowledgeBase(name="MCP KB", owner_id=u.id)
    s.add(kb)
    await s.flush()

    doc = Document(kb_id=kb.id, filename="mcp_doc.txt", file_type="txt", file_path="/p", file_size=100)
    s.add(doc)
    await s.flush()

    for i, content in enumerate([
        "Python 是一种高级编程语言，广泛用于数据科学和 Web 开发。",
        "FastAPI 是一个现代 Python Web 框架，支持异步处理和自动 API 文档。",
        "MCP 是模型上下文协议，用于标准化 AI 模型与外部工具的交互。",
    ]):
        s.add(Chunk(document_id=doc.id, kb_id=kb.id, content=content, chunk_index=i))
    await s.flush()
    await s.commit()

    from app.services.dependencies import set_embedding_service, set_vector_store
    from app.services.embedding.fake import FakeEmbeddingService
    from app.services.indexing import index_chunks
    from app.services.vector_store.chroma_store import ChromaVectorStore

    tmp = tempfile.mkdtemp()
    store = ChromaVectorStore(persist_dir=tmp)
    emb = FakeEmbeddingService(dimension=128)
    set_embedding_service(emb)
    set_vector_store(store)

    await index_chunks(s, kb.id, emb, store)
    await s.commit()

    return kb, doc


@pytest.mark.asyncio
class TestSearchKnowledgeBase:
    async def test_search_returns_results(self, setup_kb):
        kb, _doc = setup_kb
        from app.mcp_servers.knowledge_base.server import _search

        result = await _search({"query": "Python 编程", "kb_id": str(kb.id), "top_k": 5})
        data = json.loads(result[0].text)
        assert data["total"] >= 1
        assert len(data["chunks"]) >= 1
        assert "content" in data["chunks"][0]

    async def test_search_invalid_kb_id(self):
        from app.mcp_servers.knowledge_base.server import _search

        result = await _search({"query": "test", "kb_id": "not-a-uuid"})
        data = json.loads(result[0].text)
        assert "error" in data

    async def test_search_empty_kb(self):
        import uuid
        from app.mcp_servers.knowledge_base.server import _search

        result = await _search({"query": "nothing", "kb_id": str(uuid.uuid4())})
        data = json.loads(result[0].text)
        assert data["total"] == 0


@pytest.mark.asyncio
class TestGetDocumentDetail:
    async def test_get_document_detail(self, setup_kb):
        _kb, doc = setup_kb
        from app.mcp_servers.knowledge_base.server import _document_detail

        result = await _document_detail({"document_id": str(doc.id)})
        data = json.loads(result[0].text)
        assert data["filename"] == "mcp_doc.txt"
        assert data["file_type"] == "txt"

    async def test_get_document_not_found(self, setup_kb):
        import uuid
        from app.mcp_servers.knowledge_base.server import _document_detail

        result = await _document_detail({"document_id": str(uuid.uuid4())})
        data = json.loads(result[0].text)
        assert "error" in data


@pytest.mark.asyncio
class TestGetChunkContext:
    async def test_get_chunk_context(self, setup_kb):
        from sqlalchemy import select
        from app.models.chunk import Chunk

        async with _get_session_factory()() as session:
            db_result = await session.execute(select(Chunk).limit(1))
            chunk = db_result.scalars().first()

        from app.mcp_servers.knowledge_base.server import _chunk_context

        result = await _chunk_context({"chunk_id": str(chunk.id)})
        data = json.loads(result[0].text)
        assert len(data["chunks"]) >= 1
        assert any(c["is_target"] for c in data["chunks"])

    async def test_get_chunk_context_invalid_id(self, setup_kb):
        import uuid
        from app.mcp_servers.knowledge_base.server import _chunk_context

        result = await _chunk_context({"chunk_id": str(uuid.uuid4())})
        data = json.loads(result[0].text)
        assert "error" in data


@pytest.mark.asyncio
class TestToolListing:
    async def test_list_tools_returns_three(self):
        from app.mcp_servers.knowledge_base.server import handle_list_tools

        tools = await handle_list_tools()
        assert len(tools) == 3
        tool_names = [t.name for t in tools]
        assert "search_knowledge_base" in tool_names
        assert "get_document_detail" in tool_names
        assert "get_chunk_context" in tool_names


@pytest.mark.asyncio
class TestToolDispatch:
    async def test_handle_call_tool_dispatches(self, setup_kb):
        kb, _doc = setup_kb
        from app.mcp_servers.knowledge_base.server import handle_call_tool

        result = await handle_call_tool("search_knowledge_base", {"query": "Python", "kb_id": str(kb.id)})
        data = json.loads(result[0].text)
        assert data["total"] >= 0

    async def test_handle_call_tool_unknown(self):
        from app.mcp_servers.knowledge_base.server import handle_call_tool

        result = await handle_call_tool("unknown_tool", {})
        data = json.loads(result[0].text)
        assert "error" in data
