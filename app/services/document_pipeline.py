"""文档处理流水线：解析→清洗→切片→保存 chunks。"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.chunk import Chunk
from app.models.document import Document, DocumentStatus
from app.services import chunker, parser_service, text_cleaner
from app.services.file_storage import get_file_path

logger = get_logger(__name__)


async def process_document(db: AsyncSession, document_id: uuid.UUID) -> None:
    """处理单个文档的完整流水线。"""
    from sqlalchemy import select

    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalars().first()
    if not doc:
        logger.warning("document not found", document_id=str(document_id))
        return

    try:
        # 1. 解析
        await _update_status(db, doc, DocumentStatus.PARSING)
        abs_path = get_file_path(doc.file_path)
        parsed = parser_service.parse_document(abs_path, doc.file_type)

        # 2. 清洗
        cleaned_text = text_cleaner.clean_text(parsed.text)

        # 3. 切片
        chunks = chunker.chunk_text(
            text=cleaned_text,
            pages=parsed.pages,
            sections=parsed.sections,
        )

        # 4. 保存 chunks
        await _update_status(db, doc, DocumentStatus.CHUNKING)
        for ch in chunks:
            chunk_record = Chunk(
                document_id=doc.id,
                kb_id=doc.kb_id,
                content=ch.content,
                page=ch.page,
                section_title=ch.section_title,
                chunk_index=ch.chunk_index,
                chunk_metadata={
                    "start_char": ch.start_char,
                    "end_char": ch.end_char,
                    "token_count": ch.token_count,
                },
            )
            db.add(chunk_record)

        # 5. 更新文档状态
        doc.chunk_count = len(chunks)
        doc.status = DocumentStatus.READY
        await db.flush()

        logger.info("document processed", document_id=str(document_id), chunks=len(chunks))

    except Exception as e:
        logger.error("document processing failed", document_id=str(document_id), error=str(e))
        await _update_status(db, doc, DocumentStatus.ERROR)


async def _update_status(db: AsyncSession, doc: Document, status: DocumentStatus) -> None:
    doc.status = status
    await db.flush()
