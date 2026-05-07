"""测试 app/services/document_pipeline.py"""

import os
import tempfile
import uuid

import pytest
import pytest_asyncio

from app.db.session import _get_session_factory, init_db


@pytest_asyncio.fixture
async def s():
    await init_db()
    async with _get_session_factory()() as session:
        async with session.begin():
            yield session


@pytest_asyncio.fixture
async def setup_data(s):
    from app.models.document import Document
    from app.models.knowledge_base import KnowledgeBase
    from app.models.user import User

    user = User(username="pipeuser", email="pipe@x.com", password_hash="h")
    s.add(user)
    await s.flush()

    kb = KnowledgeBase(name="Pipe KB", owner_id=user.id)
    s.add(kb)
    await s.flush()

    storage_dir = tempfile.mkdtemp()
    file_path = os.path.join(storage_dir, str(kb.id))
    os.makedirs(file_path, exist_ok=True)
    test_file = os.path.join(file_path, "test.txt")
    with open(test_file, "w") as f:
        f.write("这是测试文档的内容。\n\n这是第二段内容，用于验证流水线。")

    doc = Document(
        kb_id=kb.id,
        filename="test.txt",
        file_type="txt",
        file_path=os.path.join(str(kb.id), "test.txt"),
        file_size=100,
    )
    s.add(doc)
    await s.flush()

    return doc, storage_dir


@pytest.mark.asyncio
class TestDocumentPipeline:
    async def test_process_document_creates_chunks(self, s, setup_data, monkeypatch):
        doc, storage_dir = setup_data

        # Mock 向量存储使用临时目录
        chroma_tmp = tempfile.mkdtemp()
        from app.services.dependencies import set_embedding_service, set_vector_store
        from app.services.embedding.fake import FakeEmbeddingService
        from app.services.vector_store.chroma_store import ChromaVectorStore
        set_embedding_service(FakeEmbeddingService(dimension=128))
        set_vector_store(ChromaVectorStore(persist_dir=chroma_tmp))

        monkeypatch.setattr("app.core.config.settings.STORAGE_DIR", storage_dir)

        from app.services.document_pipeline import process_document
        await process_document(s, doc.id)

        assert doc.status.value == "ready"
        assert doc.chunk_count > 0

        # 验证 chunks 已保存
        from sqlalchemy import select
        from app.models.chunk import Chunk
        result = await s.execute(select(Chunk).where(Chunk.document_id == doc.id))
        chunks = result.scalars().all()
        assert len(chunks) == doc.chunk_count
        assert chunks[0].content
        assert chunks[0].embedding_id is not None  # 验证已向量化

        import shutil
        shutil.rmtree(chroma_tmp, ignore_errors=True)

    async def test_process_document_not_found(self, s):
        from app.services.document_pipeline import process_document
        await process_document(s, uuid.uuid4())
