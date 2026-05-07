"""测试 app/services/kb_service.py"""

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
async def user(s):
    from app.models.user import User
    u = User(username="kbowner", email="kbowner@x.com", password_hash="h")
    s.add(u)
    await s.flush()
    return u


@pytest_asyncio.fixture
async def other_user(s):
    from app.models.user import User
    u = User(username="other", email="other@x.com", password_hash="h")
    s.add(u)
    await s.flush()
    return u


@pytest.mark.asyncio
class TestCreateKB:
    async def test_create_kb_success(self, s, user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.services import kb_service

        data = KnowledgeBaseCreate(name="Test KB", description="desc", visibility="team")
        result = await kb_service.create_kb(s, user, data)

        assert result.name == "Test KB"
        assert result.visibility == "team"
        assert result.owner_id == user.id

    async def test_create_kb_default_visibility(self, s, user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.services import kb_service

        data = KnowledgeBaseCreate(name="Private KB")
        result = await kb_service.create_kb(s, user, data)
        assert result.visibility == "private"


@pytest.mark.asyncio
class TestListKBs:
    async def test_list_own_kbs(self, s, user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.services import kb_service

        data = KnowledgeBaseCreate(name="KB1", visibility="private")
        await kb_service.create_kb(s, user, data)

        results = await kb_service.list_kbs(s, user)
        assert len(results) == 1

    async def test_list_excludes_other_private(self, s, user, other_user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.services import kb_service

        await kb_service.create_kb(s, user, KnowledgeBaseCreate(name="My KB", visibility="private"))
        await kb_service.create_kb(s, other_user, KnowledgeBaseCreate(name="Other Private", visibility="private"))

        results = await kb_service.list_kbs(s, user)
        assert len(results) == 1
        assert results[0].name == "My KB"

    async def test_list_includes_other_public(self, s, user, other_user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.services import kb_service

        await kb_service.create_kb(s, user, KnowledgeBaseCreate(name="My KB", visibility="private"))
        await kb_service.create_kb(s, other_user, KnowledgeBaseCreate(name="Public KB", visibility="public"))

        results = await kb_service.list_kbs(s, user)
        assert len(results) == 2


@pytest.mark.asyncio
class TestGetKB:
    async def test_get_own_kb(self, s, user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.services import kb_service

        created = await kb_service.create_kb(s, user, KnowledgeBaseCreate(name="KB"))
        result = await kb_service.get_kb(s, created.id, user)
        assert result.name == "KB"

    async def test_get_kb_not_found(self, s, user):
        from app.core.exceptions import NotFoundException
        from app.services import kb_service

        with pytest.raises(NotFoundException):
            await kb_service.get_kb(s, uuid.uuid4(), user)

    async def test_get_kb_forbidden(self, s, user, other_user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.core.exceptions import ForbiddenException
        from app.services import kb_service

        created = await kb_service.create_kb(s, user, KnowledgeBaseCreate(name="Private", visibility="private"))
        with pytest.raises(ForbiddenException):
            await kb_service.get_kb(s, created.id, other_user)


@pytest.mark.asyncio
class TestUpdateKB:
    async def test_update_kb_success(self, s, user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate
        from app.services import kb_service

        created = await kb_service.create_kb(s, user, KnowledgeBaseCreate(name="Old"))
        result = await kb_service.update_kb(s, created.id, user, KnowledgeBaseUpdate(name="New"))
        assert result.name == "New"

    async def test_update_kb_forbidden(self, s, user, other_user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate
        from app.core.exceptions import ForbiddenException
        from app.services import kb_service

        created = await kb_service.create_kb(s, user, KnowledgeBaseCreate(name="KB"))
        with pytest.raises(ForbiddenException):
            await kb_service.update_kb(s, created.id, other_user, KnowledgeBaseUpdate(name="Hacked"))


@pytest.mark.asyncio
class TestDeleteKB:
    async def test_delete_kb_success(self, s, user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.services import kb_service
        from app.core.exceptions import NotFoundException

        created = await kb_service.create_kb(s, user, KnowledgeBaseCreate(name="To Delete"))
        await kb_service.delete_kb(s, created.id, user)

        with pytest.raises(NotFoundException):
            await kb_service.get_kb(s, created.id, user)

    async def test_delete_kb_forbidden(self, s, user, other_user):
        from app.schemas.knowledge_base import KnowledgeBaseCreate
        from app.core.exceptions import ForbiddenException
        from app.services import kb_service

        created = await kb_service.create_kb(s, user, KnowledgeBaseCreate(name="KB"))
        with pytest.raises(ForbiddenException):
            await kb_service.delete_kb(s, created.id, other_user)
