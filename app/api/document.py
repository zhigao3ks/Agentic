"""文档管理 API 路由。"""

import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse, DocumentUploadResponse
from app.services import document_service
from app.services.auth_service import get_current_user_dependency

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/kbs/{kb_id}/documents/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload(
    kb_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    return await document_service.upload_document(db, kb_id, file, user)


@router.get("/kbs/{kb_id}/documents", response_model=DocumentListResponse)
async def list_docs(
    kb_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    return await document_service.list_documents(db, kb_id, user)


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_doc(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    return await document_service.get_document(db, document_id)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_doc(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user_dependency),
):
    await document_service.delete_document(db, document_id)
