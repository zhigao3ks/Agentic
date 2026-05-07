"""FastAPI 应用入口。"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    logger.warning("app_exception", error_code=exc.error_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "detail": exc.detail},
    )


from app.api.agent import router as agent_router
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.document import router as doc_router
from app.api.knowledge_base import router as kb_router
from app.api.mcp import router as mcp_router
from app.api.retrieval import router as retrieval_router
from app.api.ws import router as ws_router

app.include_router(auth_router)
app.include_router(kb_router)
app.include_router(doc_router)
app.include_router(retrieval_router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(mcp_router)
app.include_router(ws_router)

# 静态文件 (前端联调页面) → 访问 http://localhost:8000/app
import os
_static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(_static_dir):
    app.mount("/app", StaticFiles(directory=_static_dir, html=True), name="static")


@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION}
