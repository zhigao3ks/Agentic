"""认证 API 路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import RegisterResponse, TokenResponse, UserLogin
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service
from app.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await auth_service.register(db, body)
    return result


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await auth_service.login(db, body.username, body.password)
    return result


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user_dependency)):
    return UserResponse.model_validate(user)
