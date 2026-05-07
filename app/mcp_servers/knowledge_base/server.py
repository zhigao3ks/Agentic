"""Knowledge Base MCP Server —— 提供 3 个工具：search、document_detail、chunk_context。

启动方式：python -m app.mcp_servers.knowledge_base.server
"""

import asyncio
import json
import uuid

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("knowledge-base-mcp")


def _get_services():
    """初始化数据库会话和服务。"""
    from app.db.session import _get_session_factory
    from app.services.dependencies import get_embedding_service, get_vector_store

    return _get_session_factory(), get_embedding_service(), get_vector_store()


async def _ensure_tables():
    from app.db.session import init_db
    await init_db()


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_knowledge_base",
            description="在指定知识库中检索相关文档片段",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索查询"},
                    "kb_id": {"type": "string", "description": "知识库 ID"},
                    "top_k": {"type": "integer", "description": "返回结果数", "default": 10},
                },
                "required": ["query", "kb_id"],
            },
        ),
        Tool(
            name="get_document_detail",
            description="获取文档元数据详情",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "文档 ID"},
                },
                "required": ["document_id"],
            },
        ),
        Tool(
            name="get_chunk_context",
            description="获取指定 chunk 及其前后相邻 chunk 的内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "chunk_id": {"type": "string", "description": "Chunk ID"},
                    "context_size": {"type": "integer", "description": "前后上下文数量", "default": 2},
                },
                "required": ["chunk_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    await _ensure_tables()

    if name == "search_knowledge_base":
        return await _search(arguments)
    elif name == "get_document_detail":
        return await _document_detail(arguments)
    elif name == "get_chunk_context":
        return await _chunk_context(arguments)
    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False))]


async def _search(args: dict) -> list[TextContent]:
    query = args.get("query", "")
    kb_id = args.get("kb_id", "")
    top_k = args.get("top_k", 10)

    try:
        kb_uuid = uuid.UUID(kb_id)
    except ValueError:
        return [TextContent(type="text", text=json.dumps({"error": "Invalid kb_id"}, ensure_ascii=False))]

    session_factory, emb, store = _get_services()
    from app.services.retrieval.vector_retriever import VectorRetriever
    retriever = VectorRetriever(emb, store)

    results = await retriever.retrieve(query, kb_uuid, top_k)

    if not results:
        return [TextContent(type="text", text=json.dumps({"chunks": [], "total": 0}, ensure_ascii=False))]

    async with session_factory() as db:
        from sqlalchemy import select
        from app.models.chunk import Chunk

        chunk_ids = []
        for r in results:
            cid = r.get("metadata", {}).get("chunk_id", "")
            if cid:
                try:
                    chunk_ids.append(uuid.UUID(cid))
                except ValueError:
                    pass

        chunk_map = {}
        if chunk_ids:
            db_result = await db.execute(select(Chunk).where(Chunk.id.in_(chunk_ids)))
            chunk_map = {str(c.id): c for c in db_result.scalars().all()}

        output = []
        for r in results:
            cid = r.get("metadata", {}).get("chunk_id", "")
            ch = chunk_map.get(cid)
            output.append({
                "chunk_id": cid,
                "document_id": r.get("metadata", {}).get("document_id", ""),
                "content": ch.content if ch else "",
                "score": r.get("score", 0),
                "page": r.get("metadata", {}).get("page"),
                "section_title": r.get("metadata", {}).get("section_title", ""),
            })

    return [TextContent(type="text", text=json.dumps({"chunks": output, "total": len(output)}, ensure_ascii=False))]


async def _document_detail(args: dict) -> list[TextContent]:
    document_id = args.get("document_id", "")

    try:
        doc_uuid = uuid.UUID(document_id)
    except ValueError:
        return [TextContent(type="text", text=json.dumps({"error": "Invalid document_id"}, ensure_ascii=False))]

    session_factory, _, _ = _get_services()
    async with session_factory() as db:
        from sqlalchemy import select
        from app.models.document import Document

        result = await db.execute(select(Document).where(Document.id == doc_uuid))
        doc = result.scalars().first()

        if not doc:
            return [TextContent(type="text", text=json.dumps({"error": "Document not found"}, ensure_ascii=False))]

        data = {
            "id": str(doc.id),
            "kb_id": str(doc.kb_id),
            "filename": doc.filename,
            "file_type": doc.file_type,
            "status": doc.status.value,
            "chunk_count": doc.chunk_count,
            "file_size": doc.file_size,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        }

    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False))]


async def _chunk_context(args: dict) -> list[TextContent]:
    chunk_id = args.get("chunk_id", "")
    context_size = args.get("context_size", 2)

    try:
        ch_uuid = uuid.UUID(chunk_id)
    except ValueError:
        return [TextContent(type="text", text=json.dumps({"error": "Invalid chunk_id"}, ensure_ascii=False))]

    session_factory, _, _ = _get_services()
    async with session_factory() as db:
        from sqlalchemy import select
        from app.models.chunk import Chunk

        result = await db.execute(select(Chunk).where(Chunk.id == ch_uuid))
        target = result.scalars().first()
        if not target:
            return [TextContent(type="text", text=json.dumps({"error": "Chunk not found"}, ensure_ascii=False))]

        result = await db.execute(
            select(Chunk)
            .where(Chunk.document_id == target.document_id)
            .order_by(Chunk.chunk_index)
        )
        all_chunks = result.scalars().all()

        target_idx = next((i for i, c in enumerate(all_chunks) if c.id == ch_uuid), -1)
        start = max(0, target_idx - context_size)
        end = min(len(all_chunks), target_idx + context_size + 1)

        context_chunks = []
        for i in range(start, end):
            c = all_chunks[i]
            context_chunks.append({
                "chunk_id": str(c.id),
                "chunk_index": c.chunk_index,
                "content": c.content,
                "is_target": c.id == ch_uuid,
            })

    return [TextContent(type="text", text=json.dumps({"chunks": context_chunks, "target_index": target_idx - start}, ensure_ascii=False))]


def main():
    """启动 KB MCP Server（stdio 模式）。"""
    async def _run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":
    main()
