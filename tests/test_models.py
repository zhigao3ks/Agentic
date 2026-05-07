"""测试所有数据库模型。"""

import pytest
import pytest_asyncio

from app.db.session import _get_session_factory, init_db


@pytest_asyncio.fixture
async def s():
    """提供独立的 AsyncSession，每个测试获得全新数据库。"""
    await init_db()
    async with _get_session_factory()() as session:
        yield session


@pytest.mark.asyncio
class TestUserModel:
    async def test_create_user(self, s):
        from app.models.user import User, UserRole

        user = User(username="testuser", email="test@example.com", password_hash="hashed", role=UserRole.USER)
        s.add(user)
        await s.flush()

        assert user.id is not None
        assert user.username == "testuser"
        assert user.role == UserRole.USER
        assert user.is_active is True

    async def test_user_unique_username(self, s):
        from app.models.user import User

        s.add(User(username="same", email="a@x.com", password_hash="h"))
        await s.flush()
        s.add(User(username="same", email="b@x.com", password_hash="h"))
        with pytest.raises(Exception):
            await s.flush()

    async def test_user_unique_email(self, s):
        from app.models.user import User

        s.add(User(username="a", email="same@x.com", password_hash="h"))
        await s.flush()
        s.add(User(username="b", email="same@x.com", password_hash="h"))
        with pytest.raises(Exception):
            await s.flush()

    async def test_user_default_role_is_user(self, s):
        from app.models.user import User, UserRole

        user = User(username="new", email="new@x.com", password_hash="h")
        assert user.role == UserRole.USER

    async def test_user_repr(self, s):
        from app.models.user import User

        user = User(username="test", email="t@x.com", password_hash="h")
        assert "test" in repr(user)


@pytest.mark.asyncio
class TestKnowledgeBaseModel:
    @pytest_asyncio.fixture
    async def user(self, s):
        from app.models.user import User

        u = User(username="kb_owner", email="kb@x.com", password_hash="h")
        s.add(u)
        await s.flush()
        return u

    async def test_create_knowledge_base(self, s, user):
        from app.models.knowledge_base import KnowledgeBase, Visibility

        kb = KnowledgeBase(name="Test KB", description="A test KB", owner_id=user.id, visibility=Visibility.TEAM)
        s.add(kb)
        await s.flush()

        assert kb.id is not None
        assert kb.name == "Test KB"
        assert kb.visibility == Visibility.TEAM

    async def test_kb_default_visibility_is_private(self, s, user):
        from app.models.knowledge_base import KnowledgeBase, Visibility

        kb = KnowledgeBase(name="KB", owner_id=user.id)
        assert kb.visibility == Visibility.PRIVATE

    async def test_kb_owner_relationship(self, s, user):
        from app.models.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(name="KB", owner_id=user.id)
        s.add(kb)
        await s.flush()
        await s.refresh(kb, ["owner"])
        assert kb.owner is not None
        assert kb.owner.username == "kb_owner"


@pytest.mark.asyncio
class TestDocumentModel:
    @pytest_asyncio.fixture
    async def kb(self, s):
        from app.models.knowledge_base import KnowledgeBase
        from app.models.user import User

        u = User(username="doc_owner", email="doc@x.com", password_hash="h")
        s.add(u)
        await s.flush()
        kb = KnowledgeBase(name="KB", owner_id=u.id)
        s.add(kb)
        await s.flush()
        return kb

    async def test_create_document(self, s, kb):
        from app.models.document import Document, DocumentStatus

        doc = Document(kb_id=kb.id, filename="test.pdf", file_type="pdf", file_path="/storage/test.pdf")
        s.add(doc)
        await s.flush()

        assert doc.status == DocumentStatus.UPLOADED
        assert doc.file_size == 0

    async def test_document_status_enum(self, s, kb):
        from app.models.document import Document, DocumentStatus

        doc = Document(kb_id=kb.id, filename="f.pdf", file_type="pdf", file_path="/p", status=DocumentStatus.READY)
        s.add(doc)
        await s.flush()
        assert doc.status == DocumentStatus.READY

    async def test_document_kb_relationship(self, s, kb):
        from app.models.document import Document

        doc = Document(kb_id=kb.id, filename="f.pdf", file_type="pdf", file_path="/p")
        s.add(doc)
        await s.flush()
        await s.refresh(doc, ["knowledge_base"])
        assert doc.knowledge_base is not None


@pytest.mark.asyncio
class TestChunkModel:
    @pytest_asyncio.fixture
    async def doc(self, s):
        from app.models.document import Document
        from app.models.knowledge_base import KnowledgeBase
        from app.models.user import User

        u = User(username="ch_owner", email="ch@x.com", password_hash="h")
        s.add(u)
        await s.flush()
        kb = KnowledgeBase(name="KB", owner_id=u.id)
        s.add(kb)
        await s.flush()
        doc = Document(kb_id=kb.id, filename="f.pdf", file_type="pdf", file_path="/p")
        s.add(doc)
        await s.flush()
        return doc

    async def test_create_chunk(self, s, doc):
        from app.models.chunk import Chunk

        chunk = Chunk(document_id=doc.id, kb_id=doc.kb_id, content="Test content",
                       page=1, section_title="Intro", chunk_index=0)
        s.add(chunk)
        await s.flush()

        assert chunk.content == "Test content"
        assert chunk.page == 1
        assert chunk.chunk_metadata == {}

    async def test_chunk_metadata_json(self, s, doc):
        from app.models.chunk import Chunk

        chunk = Chunk(document_id=doc.id, kb_id=doc.kb_id, content="C",
                       chunk_metadata={"key": "value", "tokens": 128})
        s.add(chunk)
        await s.flush()
        assert chunk.chunk_metadata == {"key": "value", "tokens": 128}


@pytest.mark.asyncio
class TestChatModels:
    @pytest_asyncio.fixture
    async def user(self, s):
        from app.models.user import User

        u = User(username="chat_user", email="chat@x.com", password_hash="h")
        s.add(u)
        await s.flush()
        return u

    async def test_create_chat_session(self, s, user):
        from app.models.chat import ChatSession

        cs = ChatSession(user_id=user.id, title="Test Session")
        s.add(cs)
        await s.flush()
        assert cs.title == "Test Session"

    async def test_create_chat_message(self, s, user):
        from app.models.chat import ChatMessage, ChatSession, MessageRole

        cs = ChatSession(user_id=user.id, title="S")
        s.add(cs)
        await s.flush()

        msg = ChatMessage(session_id=cs.id, role=MessageRole.USER, content="Hello")
        s.add(msg)
        await s.flush()

        assert msg.role == MessageRole.USER
        assert msg.citations == []

    async def test_citations_json(self, s, user):
        from app.models.chat import ChatMessage, ChatSession, MessageRole

        cs = ChatSession(user_id=user.id, title="S")
        s.add(cs)
        await s.flush()

        citations = [{"doc_id": "d1", "score": 0.95}]
        msg = ChatMessage(session_id=cs.id, role=MessageRole.ASSISTANT, content="A", citations=citations)
        s.add(msg)
        await s.flush()
        assert msg.citations == citations


@pytest.mark.asyncio
class TestAgentRunModel:
    async def test_create_agent_run(self, s):
        from app.models.agent_run import AgentRun, AgentRunStatus

        run = AgentRun(user_query="What is RAG?", status=AgentRunStatus.COMPLETED, latency_ms=1500)
        s.add(run)
        await s.flush()

        assert run.status == AgentRunStatus.COMPLETED
        assert run.latency_ms == 1500
        assert run.steps == []

    async def test_agent_run_default_status(self, s):
        from app.models.agent_run import AgentRun, AgentRunStatus

        run = AgentRun(user_query="Q")
        assert run.status == AgentRunStatus.PENDING


@pytest.mark.asyncio
class TestMCPModels:
    async def test_create_mcp_server(self, s):
        from app.models.mcp import MCPServer, MCPTransport

        server = MCPServer(name="test-server", transport=MCPTransport.STDIO, endpoint="python -m test")
        s.add(server)
        await s.flush()

        assert server.enabled is True
        assert server.timeout_seconds == 30

    async def test_create_mcp_tool(self, s):
        from app.models.mcp import MCPPermissionLevel, MCPServer, MCPTool

        server = MCPServer(name="srv", endpoint="e")
        s.add(server)
        await s.flush()

        tool = MCPTool(server_id=server.id, name="search", description="Search tool",
                        input_schema={"type": "object"}, permission_level=MCPPermissionLevel.PUBLIC)
        s.add(tool)
        await s.flush()

        assert tool.permission_level == MCPPermissionLevel.PUBLIC
        assert tool.input_schema == {"type": "object"}

    async def test_create_mcp_tool_call(self, s):
        from app.models.mcp import MCPToolCall, MCPToolCallStatus

        call = MCPToolCall(tool_name="search", tool_input={"q": "test"},
                            tool_output={"results": []}, status=MCPToolCallStatus.SUCCESS, latency_ms=100)
        s.add(call)
        await s.flush()

        assert call.status == MCPToolCallStatus.SUCCESS
        assert call.latency_ms == 100

    async def test_mcp_tool_call_default_status(self, s):
        from app.models.mcp import MCPToolCall, MCPToolCallStatus

        call = MCPToolCall(tool_name="test")
        assert call.status == MCPToolCallStatus.PENDING

    async def test_mcp_server_unique_name(self, s):
        from app.models.mcp import MCPServer

        s.add(MCPServer(name="unique", endpoint="a"))
        await s.flush()
        s.add(MCPServer(name="unique", endpoint="b"))
        with pytest.raises(Exception):
            await s.flush()
