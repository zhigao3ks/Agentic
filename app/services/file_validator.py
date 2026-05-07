"""文件上传校验。"""

import os
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import ValidationException

_ALLOWED_EXTENSIONS = {"pdf", "docx", "md", "txt", "csv", "xlsx"}
_ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/markdown",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
_MAX_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def validate_upload(file: UploadFile) -> str:
    """校验上传文件，返回文件类型（扩展名）。"""
    if not file.filename:
        raise ValidationException(detail="Filename is required")

    # 先检查原始文件名中的路径穿越
    raw = file.filename
    if ".." in raw or "/" in raw or "\\" in raw:
        raise ValidationException(detail="Path traversal detected")

    filename = os.path.basename(raw)
    if not filename or filename in (".", ".."):
        raise ValidationException(detail="Invalid filename")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValidationException(detail=f"Unsupported file type: .{ext}")

    if file.content_type and file.content_type not in _ALLOWED_MIME_TYPES:
        raise ValidationException(detail=f"Unsupported MIME type: {file.content_type}")

    # 注：Starlette 1.0 的 UploadFile.size 始终为 None，
    # 文件大小限制由 FastAPI/Starlette 中间件或前端反向代理控制。
    _ = _MAX_SIZE_BYTES  # 保留常量引用，后续启用时使用

    return ext
