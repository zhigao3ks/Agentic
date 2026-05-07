"""用户相关 Pydantic Schema。"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100, examples=["zhangsan"])
    email: EmailStr = Field(examples=["zhangsan@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["securePass123"])


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
