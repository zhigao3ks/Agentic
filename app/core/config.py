"""应用配置管理，基于 Pydantic Settings 从 .env 和环境变量加载配置。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # --- 应用 ---
    APP_NAME: str = "MCP-Agentic RAG Backend"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    # --- 数据库 ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_rag"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- JWT ---
    JWT_SECRET_KEY: str = "change-me-to-a-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- 模型服务 ---
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_API_KEY: str = "ollama"
    LLM_MODEL: str = "qwen2.5:7b"

    # --- Embedding 服务 ---
    EMBEDDING_BASE_URL: str = "http://localhost:11434/v1"
    EMBEDDING_API_KEY: str = "ollama"
    EMBEDDING_MODEL: str = "bge-m3"

    # --- Reranker 服务 ---
    RERANKER_BASE_URL: str = "http://localhost:8001/v1"
    RERANKER_API_KEY: str = "not-needed"
    RERANKER_MODEL: str = "bge-reranker-base"

    # --- 向量数据库 ---
    CHROMA_PERSIST_DIR: str = "./storage/chroma"

    # --- 文件存储 ---
    STORAGE_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # --- 日志 ---
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./storage/logs/app.log"


settings = Settings()
