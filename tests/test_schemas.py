"""测试 Pydantic Schema 校验和序列化。"""

import pytest
from pydantic import ValidationError


class TestUserCreate:
    def test_valid_user_create(self):
        from app.schemas.user import UserCreate

        data = UserCreate(username="zhangsan", email="zhangsan@example.com", password="securePass123")
        assert data.username == "zhangsan"
        assert data.email == "zhangsan@example.com"

    def test_username_too_short(self):
        from app.schemas.user import UserCreate

        with pytest.raises(ValidationError):
            UserCreate(username="ab", email="a@b.com", password="12345678")

    def test_username_too_long(self):
        from app.schemas.user import UserCreate

        with pytest.raises(ValidationError):
            UserCreate(username="a" * 101, email="a@b.com", password="12345678")

    def test_invalid_email(self):
        from app.schemas.user import UserCreate

        with pytest.raises(ValidationError):
            UserCreate(username="validname", email="not-an-email", password="12345678")

    def test_password_too_short(self):
        from app.schemas.user import UserCreate

        with pytest.raises(ValidationError):
            UserCreate(username="validname", email="a@b.com", password="short")


class TestUserLogin:
    def test_valid_user_login(self):
        from app.schemas.auth import UserLogin

        data = UserLogin(username="zhangsan", password="secret")
        assert data.username == "zhangsan"

    def test_empty_username(self):
        from app.schemas.auth import UserLogin

        with pytest.raises(ValidationError):
            UserLogin(username="", password="secret")


class TestTokenResponse:
    def test_token_response_defaults(self):
        from app.schemas.auth import TokenResponse

        t = TokenResponse(access_token="abc")
        assert t.token_type == "bearer"


class TestUserResponse:
    def test_from_attributes_config(self):
        from app.schemas.user import UserResponse

        assert UserResponse.model_config.get("from_attributes") is True


class TestRegisterResponse:
    def test_register_response_structure(self):
        from app.schemas.auth import RegisterResponse

        r = RegisterResponse(
            user={"id": "00000000-0000-0000-0000-000000000001", "username": "u", "email": "u@x.com",
                  "role": "user", "is_active": True, "created_at": "2026-01-01T00:00:00Z"},
            access_token="token",
        )
        assert r.access_token == "token"
        assert r.token_type == "bearer"
