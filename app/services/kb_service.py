"""知识库业务逻辑。"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase, Visibility
from app.models.user import User
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseUpdate


async def create_kb(db: AsyncSession, user: User, data: KnowledgeBaseCreate) -> KnowledgeBaseResponse:
    kb = KnowledgeBase(
        name=data.name,
        description=data.description,
        owner_id=user.id,
        visibility=Visibility(data.visibility),
    )
    db.add(kb)
    await db.flush()
    await db.refresh(kb)
    return _to_response(kb, 0, 0)


async def list_kbs(db: AsyncSession, user: User) -> list[KnowledgeBaseResponse]:
    query = select(KnowledgeBase).where(
        (KnowledgeBase.owner_id == user.id) | (KnowledgeBase.visibility != Visibility.PRIVATE)
    )
    result = await db.execute(query)
    kbs = result.scalars().all()

    kb_ids = [kb.id for kb in kbs]
    doc_counts = {}
    chunk_counts = {}
    if kb_ids:
        doc_result = await db.execute(
            select(Document.kb_id, func.count(Document.id)).where(Document.kb_id.in_(kb_ids)).group_by(Document.kb_id)
        )
        doc_counts = dict(doc_result.all())
        chunk_result = await db.execute(
            select(Chunk.kb_id, func.count(Chunk.id)).where(Chunk.kb_id.in_(kb_ids)).group_by(Chunk.kb_id)
        )
        chunk_counts = dict(chunk_result.all())

    return [_to_response(kb, doc_counts.get(kb.id, 0), chunk_counts.get(kb.id, 0)) for kb in kbs]


async def get_kb(db: AsyncSession, kb_id: uuid.UUID, user: User) -> KnowledgeBaseResponse:
    kb = await _get_or_404(db, kb_id)
    _check_access(kb, user)

    doc_count = await db.scalar(select(func.count(Document.id)).where(Document.kb_id == kb_id))
    chunk_count = await db.scalar(select(func.count(Chunk.id)).where(Chunk.kb_id == kb_id))
    return _to_response(kb, doc_count or 0, chunk_count or 0)


async def update_kb(db: AsyncSession, kb_id: uuid.UUID, user: User, data: KnowledgeBaseUpdate) -> KnowledgeBaseResponse:
    kb = await _get_or_404(db, kb_id)
    _check_owner(kb, user)

    if data.name is not None:
        kb.name = data.name
    if data.description is not None:
        kb.description = data.description
    if data.visibility is not None:
        kb.visibility = Visibility(data.visibility)

    await db.flush()
    await db.refresh(kb)

    doc_count = await db.scalar(select(func.count(Document.id)).where(Document.kb_id == kb_id))
    chunk_count = await db.scalar(select(func.count(Chunk.id)).where(Chunk.kb_id == kb_id))
    return _to_response(kb, doc_count or 0, chunk_count or 0)


async def delete_kb(db: AsyncSession, kb_id: uuid.UUID, user: User) -> None:
    kb = await _get_or_404(db, kb_id)
    _check_owner(kb, user)
    await db.delete(kb)
    await db.flush()


async def _get_or_404(db: AsyncSession, kb_id: uuid.UUID) -> KnowledgeBase:
    result = await db.execute(select(KnowledgeBase).where(KnowledgeBase.id == kb_id))
    kb = result.scalars().first()
    if not kb:
        raise NotFoundException(detail="Knowledge base not found")
    return kb


def _check_owner(kb: KnowledgeBase, user: User) -> None:
    if kb.owner_id != user.id:
        raise ForbiddenException(detail="Only the owner can modify this knowledge base")


def _check_access(kb: KnowledgeBase, user: User) -> None:
    if kb.visibility == Visibility.PRIVATE and kb.owner_id != user.id:
        raise ForbiddenException(detail="Access denied")


def _to_response(kb: KnowledgeBase, doc_count: int, chunk_count: int) -> KnowledgeBaseResponse:
    return KnowledgeBaseResponse(
        id=kb.id,
        name=kb.name,
        description=kb.description,
        owner_id=kb.owner_id,
        visibility=kb.visibility.value,
        document_count=doc_count,
        chunk_count=chunk_count,
        created_at=kb.created_at,
        updated_at=kb.updated_at,
    )
