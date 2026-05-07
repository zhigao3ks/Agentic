"""Pytest 共享 fixtures。"""

import os

import pytest

from app.core.config import settings

_TEST_DB_PATH = "storage/test.db"


@pytest.fixture(autouse=True)
def _override_db_url(monkeypatch):
    """所有测试默认使用 SQLite 文件数据库，测试结束后清理。"""
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite+aiosqlite:///{_TEST_DB_PATH}")
    from app.db.session import _reset_engine

    _reset_engine()
    yield
    _reset_engine()
    if os.path.exists(_TEST_DB_PATH):
        os.remove(_TEST_DB_PATH)
