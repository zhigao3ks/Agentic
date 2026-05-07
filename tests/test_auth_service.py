"""测试 app/services/auth_service.py"""

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
class TestRegister:
    async def test_register_creates_user_and_returns_token(self, s):
        from app.schemas.user import UserCreate
        from app.services import auth_service

        data = UserCreate(username="newuser", email="new@example.com", password="securePass123")
        result = await auth_service.register(s, data)

        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert result["user"].username == "newuser"
        assert result["user"].email == "new@example.com"

    async def test_register_hashes_password(self, s):
        from app.schemas.user import UserCreate
        from app.services import auth_service

        data = UserCreate(username="hashuser", email="hash@x.com", password="my-password")
        result = await auth_service.register(s, data)

        # 密码不应明文存储
        from app.models.user import User
        from sqlalchemy import select
        user = (await s.execute(select(User).where(User.id == result["user"].id))).scalars().first()
        assert user.password_hash != "my-password"

    async def test_register_duplicate_username(self, s):
        from app.core.exceptions import ConflictException
        from app.schemas.user import UserCreate
        from app.services import auth_service

        data1 = UserCreate(username="same", email="a@x.com", password="12345678")
        await auth_service.register(s, data1)

        data2 = UserCreate(username="same", email="b@x.com", password="87654321")
        with pytest.raises(ConflictException):
            await auth_service.register(s, data2)

    async def test_register_duplicate_email(self, s):
        from app.core.exceptions import ConflictException
        from app.schemas.user import UserCreate
        from app.services import auth_service

        data1 = UserCreate(username="user1", email="same@x.com", password="12345678")
        await auth_service.register(s, data1)

        data2 = UserCreate(username="user2", email="same@x.com", password="87654321")
        with pytest.raises(ConflictException):
            await auth_service.register(s, data2)


@pytest.mark.asyncio
class TestLogin:
    @pytest_asyncio.fixture
    async def registered_user(self, s):
        from app.schemas.user import UserCreate
        from app.services import auth_service

        data = UserCreate(username="loginuser", email="login@example.com", password="correct-password")
        return await auth_service.register(s, data)

    async def test_login_success(self, s, registered_user):
        from app.services import auth_service

        result = await auth_service.login(s, "loginuser", "correct-password")
        assert "access_token" in result
        assert result["token_type"] == "bearer"

    async def test_login_wrong_password(self, s, registered_user):
        from app.core.exceptions import UnauthorizedException
        from app.services import auth_service

        with pytest.raises(UnauthorizedException):
            await auth_service.login(s, "loginuser", "wrong-password")

    async def test_login_nonexistent_user(self, s, registered_user):
        from app.core.exceptions import UnauthorizedException
        from app.services import auth_service

        with pytest.raises(UnauthorizedException):
            await auth_service.login(s, "nonexistent", "any-password")


@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_get_current_user_success(self, s):
        from app.schemas.user import UserCreate
        from app.services import auth_service

        data = UserCreate(username="tokenuser", email="token@x.com", password="password123")
        result = await auth_service.register(s, data)
        token = result["access_token"]

        user = await auth_service.get_current_user(s, token)
        assert user.username == "tokenuser"

    async def test_get_current_user_invalid_token(self, s):
        from app.core.exceptions import UnauthorizedException
        from app.services import auth_service

        with pytest.raises(UnauthorizedException):
            await auth_service.get_current_user(s, "not-a-valid-token")

    async def test_get_current_user_user_not_found(self, s):
        import uuid
        from app.core.config import settings
        from app.core.security import create_access_token
        from app.core.exceptions import UnauthorizedException
        from app.services import auth_service

        token = create_access_token({"sub": str(uuid.uuid4()), "username": "ghost"})
        with pytest.raises(UnauthorizedException):
            await auth_service.get_current_user(s, token)
