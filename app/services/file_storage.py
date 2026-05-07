"""文件存储服务。"""

import os
import uuid

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationException


def _resolve_path(relative_path: str) -> str:
    """将相对路径转为绝对路径，并校验路径穿越。"""
    base = os.path.realpath(settings.STORAGE_DIR)
    target = os.path.realpath(os.path.join(base, relative_path))
    if not target.startswith(base + os.sep) and target != base:
        raise ValidationException(detail="Path traversal not allowed")
    return target


async def save_file(file: UploadFile, kb_id: str) -> str:
    """保存上传文件到 storage/{kb_id}/{uuid}_{filename}，返回相对路径。"""
    safe_name = f"{uuid.uuid4()}_{os.path.basename(file.filename)}"
    relative_path = os.path.join(str(kb_id), safe_name)
    abs_path = _resolve_path(relative_path)

    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    content = await file.read()
    if not content:
        raise ValidationException(detail="Empty file")

    with open(abs_path, "wb") as f:
        f.write(content)

    return relative_path


def get_file_path(relative_path: str) -> str:
    """返回文件的绝对路径，含路径穿越防护。"""
    return _resolve_path(relative_path)


def delete_file(relative_path: str) -> None:
    """删除文件。"""
    abs_path = _resolve_path(relative_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)
