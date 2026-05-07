"""认证相关 Pydantic Schema。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    username: str = Field(min_length=1, examples=["zhangsan"])
    password: str = Field(min_length=1, examples=["securePass123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user: UserResponse  # noqa: F821  # 由 auth_service 在运行时组装
    access_token: str
    token_type: str = "bearer"


from app.schemas.user import UserResponse  # noqa: E402  # 延迟导入避免循环引用
