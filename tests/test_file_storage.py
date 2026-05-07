"""测试 app/services/file_storage.py"""

import os
from io import BytesIO

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.core.exceptions import ValidationException


@pytest.fixture(autouse=True)
def _temp_storage(monkeypatch, tmp_path):
    """使用临时目录作为存储目录。"""
    monkeypatch.setattr("app.core.config.settings.STORAGE_DIR", str(tmp_path))
    yield


def _make_file(filename, content=b"hello world", mime="text/plain"):
    headers = {"content-type": mime} if mime else {}
    return UploadFile(filename=filename, file=BytesIO(content), headers=Headers(headers))


@pytest.mark.asyncio
class TestFileStorageAsync:
    async def test_save_and_retrieve(self):
        from app.services import file_storage

        path = await file_storage.save_file(_make_file("test.txt"), "kb1")
        abs_path = file_storage.get_file_path(path)

        assert os.path.exists(abs_path)
        with open(abs_path) as f:
            assert f.read() == "hello world"

    async def test_save_preserves_extension(self):
        from app.services import file_storage

        path = await file_storage.save_file(_make_file("doc.pdf", mime="application/pdf"), "kb2")
        assert path.endswith(".pdf")
        assert "kb2" in path

    async def test_empty_file_raises(self):
        from app.services import file_storage

        with pytest.raises(ValidationException, match="Empty"):
            await file_storage.save_file(_make_file("empty.txt", b""), "kb1")

    async def test_delete_file(self):
        from app.services import file_storage

        path = await file_storage.save_file(_make_file("del.txt"), "kb1")
        abs_path = file_storage.get_file_path(path)
        assert os.path.exists(abs_path)

        file_storage.delete_file(path)
        assert not os.path.exists(abs_path)


class TestFileStorageSync:
    def test_path_traversal_blocked(self):
        from app.services import file_storage

        with pytest.raises(ValidationException, match="Path traversal"):
            file_storage.get_file_path("../etc/passwd")
