"""知识库管理 API 路由。"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseUpdate
from app.services import kb_service
from app.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/api/kbs", tags=["knowledge_bases"])


@router.post("", response_model=KnowledgeBaseResponse, status_code=201)
async def create(
    body: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    return await kb_service.create_kb(db, user, body)


@router.get("", response_model=list[KnowledgeBaseResponse])
async def list_all(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    return await kb_service.list_kbs(db, user)


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_one(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    return await kb_service.get_kb(db, kb_id, user)


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update(
    kb_id: uuid.UUID,
    body: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    return await kb_service.update_kb(db, kb_id, user, body)


@router.delete("/{kb_id}", status_code=204)
async def delete(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    await kb_service.delete_kb(db, kb_id, user)
