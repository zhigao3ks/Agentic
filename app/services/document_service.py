"""文档管理业务逻辑。"""

import os
import uuid

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.models.document import Document, DocumentStatus
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse, DocumentUploadResponse
from app.services import file_storage, file_validator, parser_service


async def upload_document(
    db: AsyncSession,
    kb_id: uuid.UUID,
    file: UploadFile,
    user: User,
) -> DocumentUploadResponse:
    """上传文档：校验→存储→解析→创建记录。"""
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalars().first()
    if not kb:
        raise NotFoundException(detail="Knowledge base not found")
    if kb.owner_id != user.id:
        from app.core.exceptions import ForbiddenException
        raise ForbiddenException(detail="Only the owner can upload documents")

    ext = file_validator.validate_upload(file)

    relative_path = await file_storage.save_file(file, str(kb_id))
    abs_path = file_storage.get_file_path(relative_path)

    try:
        parsed = parser_service.parse_document(abs_path, ext)
    except Exception:
        file_storage.delete_file(relative_path)
        raise ValidationException(detail=f"Failed to parse {ext.upper()} file")

    doc = Document(
        kb_id=kb_id,
        filename=os.path.basename(file.filename),
        file_type=ext,
        file_path=relative_path,
        file_size=file.size or 0,
        status=DocumentStatus.UPLOADED,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    return DocumentUploadResponse(
        id=doc.id,
        kb_id=doc.kb_id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status=doc.status.value,
    )


async def list_documents(
    db: AsyncSession,
    kb_id: uuid.UUID,
    user: User,
) -> DocumentListResponse:
    result = await db.execute(
        select(Document).where(Document.kb_id == kb_id).order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    count_result = await db.execute(select(func.count(Document.id)).where(Document.kb_id == kb_id))
    total = count_result.scalar() or 0

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in docs],
        total=total,
    )


async def get_document(db: AsyncSession, document_id: uuid.UUID) -> DocumentResponse:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalars().first()
    if not doc:
        raise NotFoundException(detail="Document not found")
    return DocumentResponse.model_validate(doc)


async def delete_document(db: AsyncSession, document_id: uuid.UUID) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalars().first()
    if not doc:
        raise NotFoundException(detail="Document not found")

    file_storage.delete_file(doc.file_path)
    await db.delete(doc)
    await db.flush()
