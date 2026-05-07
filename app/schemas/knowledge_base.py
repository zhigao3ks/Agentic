"""知识库相关 Pydantic Schema。"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200, examples=["公司制度与规范"])
    description: str = Field(default="", max_length=2000, examples=["包含考勤、报销等内部制度文档"])
    visibility: str = Field(default="private", pattern="^(private|team|public)$", examples=["team"])


class KnowledgeBaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    visibility: str | None = Field(default=None, pattern="^(private|team|public)$")


class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    owner_id: uuid.UUID
    visibility: str
    document_count: int = 0
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime
