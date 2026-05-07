"""测试 app/core/security.py"""

from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    def test_hash_password_returns_string(self):
        hashed = hash_password("my-password")
        assert isinstance(hashed, str)
        assert hashed != "my-password"

    def test_hash_password_is_deterministic_for_verify(self):
        hashed = hash_password("my-password")
        assert verify_password("my-password", hashed) is True

    def test_verify_password_rejects_wrong_password(self):
        hashed = hash_password("correct-password")
        assert verify_password("wrong-password", hashed) is False

    def test_hash_password_generates_different_salts(self):
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2


class TestJWTToken:
    def test_create_access_token_returns_string(self):
        token = create_access_token({"sub": "user-1"})
        assert isinstance(token, str)

    def test_verify_token_returns_payload(self):
        token = create_access_token({"sub": "user-1"})
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user-1"

    def test_verify_token_returns_none_for_invalid_token(self):
        payload = verify_token("not-a-valid-jwt")
        assert payload is None

    def test_verify_token_returns_none_for_empty_string(self):
        payload = verify_token("")
        assert payload is None

    def test_token_includes_expiry(self):
        token = create_access_token({"sub": "user-1"}, expires_delta=timedelta(minutes=30))
        payload = verify_token(token)
        assert payload is not None
        assert "exp" in payload

    def test_expired_token_returns_none(self):
        token = create_access_token({"sub": "user-1"}, expires_delta=timedelta(seconds=-1))
        payload = verify_token(token)
        assert payload is None
