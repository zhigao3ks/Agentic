"""认证业务逻辑。"""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import create_access_token, hash_password, verify_password, verify_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

security = HTTPBearer()


async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI 依赖：从 Authorization Header 解析当前用户。"""
    return await get_current_user(db, credentials.credentials)


async def register(db: AsyncSession, data: UserCreate) -> dict:
    """注册新用户，返回用户信息和 JWT token。"""
    existing = await db.execute(
        select(User).where((User.username == data.username) | (User.email == data.email))
    )
    if existing.scalars().first():
        raise ConflictException(detail="Username or email already exists")

    user = User(username=data.username, email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {
        "user": UserResponse.model_validate(user),
        "access_token": token,
        "token_type": "bearer",
    }


async def login(db: AsyncSession, username: str, password: str) -> dict:
    """验证用户凭证，返回 JWT token。"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedException(detail="Invalid username or password")

    token = create_access_token({"sub": str(user.id), "username": user.username})
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(db: AsyncSession, token: str) -> User:
    """从 JWT token 解析并返回当前用户。"""
    payload = verify_token(token)
    if payload is None:
        raise UnauthorizedException(detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalars().first()
    if not user:
        raise UnauthorizedException(detail="User not found")

    return user
