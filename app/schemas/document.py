"""文档相关 Pydantic Schema。"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    kb_id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    status: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kb_id: uuid.UUID
    filename: str
    file_type: str
    file_path: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
