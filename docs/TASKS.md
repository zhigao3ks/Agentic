# 项目任务拆解文档

> 基于 CLAUDE.md、SPEC.md 和 RESUME_GUIDE.md 生成，按开发阶段拆分，每个任务粒度尽可能小。

---

## 阶段零：项目初始化

### T0.1 创建项目目录结构

- **任务目标**：按照 SPEC.md 第 10 节创建完整的项目目录骨架，每个目录下放置 `.gitkeep` 占位。
- **创建文件**：
  - `app/__init__.py`
  - `app/api/__init__.py`
  - `app/core/__init__.py`
  - `app/services/__init__.py`
  - `app/agents/__init__.py`
  - `app/mcp_servers/__init__.py`
  - `app/mcp_client/__init__.py`
  - `app/models/__init__.py`
  - `app/schemas/__init__.py`
  - `tests/__init__.py`
  - `scripts/.gitkeep`
  - `docker/.gitkeep`
  - `storage/.gitkeep`
- **验收标准**：所有目录存在，`__init__.py` 文件存在，`tree` 命令输出符合预期。
- **测试要求**：无（纯目录结构，无需测试）。
- **是否提交**：是。

### T0.2 创建 requirements.txt

- **任务目标**：创建项目依赖文件，包含 FastAPI、Pydantic、SQLAlchemy、LangGraph、MCP SDK、Chroma、pytest 等核心依赖。
- **创建文件**：`requirements.txt`
- **验收标准**：文件包含项目所需的核心依赖，分为核心、数据库、RAG、Agent、MCP、测试等分组。
- **测试要求**：无（配置文件，后续 `pip install -r requirements.txt` 验证）。
- **是否提交**：是。

### T0.3 创建 .env.example 与 .gitignore

- **任务目标**：创建环境变量模板文件和 Git 忽略规则文件。
- **创建文件**：`.env.example`、`.gitignore`
- **验收标准**：
  - `.env.example` 包含数据库连接、Redis 连接、模型服务地址、JWT 密钥等配置项模板。
  - `.gitignore` 忽略 `.env`、`__pycache__/`、`*.pyc`、`.pytest_cache/`、`storage/uploads/` 等。
- **测试要求**：无（配置文件）。
- **是否提交**：是。

### T0.4 初始化 Git 仓库

- **任务目标**：初始化 Git 仓库并完成首次提交。
- **执行命令**：`git init`，`git add` 所有已创建文件，首次 commit。
- **验收标准**：`.git` 目录存在，首次 commit 成功。
- **测试要求**：`git status` 确认无未提交文件。
- **是否提交**：是（首次 commit）。

### T0.5 生成 docs/TASKS.md

- **任务目标**：生成项目任务拆解文档（即本文件）。
- **创建文件**：`docs/TASKS.md`
- **验收标准**：文件包含所有阶段的细粒度任务，每个任务包含目标、文件、验收标准、测试要求、是否提交。
- **测试要求**：无（文档文件）。
- **是否提交**：是。

---

## 阶段一：FastAPI 基础骨架

### T1.1 创建 app/core/config.py

- **任务目标**：使用 Pydantic Settings 实现配置管理，从 `.env` 和环境变量加载配置。
- **创建文件**：`app/core/config.py`
- **修改文件**：无
- **验收标准**：
  - 包含数据库 URL、Redis URL、JWT 密钥、模型服务地址等配置项。
  - 每个配置项有默认值或从环境变量读取。
  - 可以通过 `from app.core.config import settings` 导入使用。
- **测试要求**：`tests/test_config.py` — 测试默认值和环境变量覆盖。
- **是否提交**：是。

### T1.2 创建 app/core/logging.py

- **任务目标**：实现统一日志配置，支持控制台输出和文件轮转。
- **创建文件**：`app/core/logging.py`
- **验收标准**：
  - 配置 structlog 或标准 logging，输出 JSON 格式日志。
  - 支持日志级别配置。
  - 其他模块可通过 `get_logger(__name__)` 获取 logger。
- **测试要求**：`tests/test_logging.py` — 测试日志输出格式和级别过滤。
- **是否提交**：是。

### T1.3 创建 app/core/exceptions.py

- **任务目标**：定义项目统一异常类。
- **创建文件**：`app/core/exceptions.py`
- **验收标准**：
  - 定义 `AppException` 基类，包含 status_code、detail、error_code。
  - 定义常用子类：`NotFoundException`、`ValidationException`、`UnauthorizedException`、`ForbiddenException`。
- **测试要求**：`tests/test_exceptions.py` — 测试异常属性和序列化。
- **是否提交**：是。

### T1.4 创建 FastAPI 应用实例与健康检查

- **任务目标**：创建 `app/main.py` 作为应用入口，挂载健康检查路由。
- **创建文件**：`app/main.py`
- **修改文件**：无
- **验收标准**：
  - `GET /api/health` 返回 `{"status": "ok", "version": "0.1.0"}`。
  - 应用可以 `uvicorn app.main:app` 启动。
- **测试要求**：`tests/test_health.py` — 使用 TestClient 测试健康检查接口返回 200。
- **是否提交**：是。

### T1.5 创建 app/core/security.py

- **任务目标**：实现 JWT Token 生成与验证、密码哈希。
- **创建文件**：`app/core/security.py`
- **验收标准**：
  - `create_access_token(data, expires_delta)` 生成 JWT。
  - `verify_token(token)` 验证并返回 payload。
  - `hash_password(password)` 和 `verify_password(plain, hashed)` 使用 bcrypt。
- **测试要求**：`tests/test_security.py` — 测试 token 生成/验证、密码哈希/验证、过期 token 处理。
- **是否提交**：是。

---

## 阶段二：数据库连接与基础模型

### T2.1 创建 app/db/session.py

- **任务目标**：创建 SQLAlchemy 异步引擎和会话管理。
- **创建文件**：`app/db/__init__.py`、`app/db/session.py`
- **验收标准**：
  - 使用 `create_async_engine` 创建引擎。
  - 提供 `get_db()` 异步生成器用于依赖注入。
  - 提供 `init_db()` 用于创建表。
- **测试要求**：`tests/test_db.py` — 使用 SQLite 内存数据库测试会话创建和引擎连接。
- **是否提交**：是。

### T2.2 创建 app/db/base.py

- **任务目标**：创建 SQLAlchemy Declarative Base 和通用模型基类。
- **创建文件**：`app/db/base.py`
- **验收标准**：
  - 定义 `Base`（DeclarativeBase）。
  - 定义 `TimestampMixin`（created_at, updated_at）。
  - 定义 `UUIDMixin`（id 使用 UUID 主键）。
- **测试要求**：`tests/test_db.py` 中补充测试模型继承。
- **是否提交**：是。

### T2.3 创建 User 模型

- **任务目标**：创建用户数据库模型。
- **创建文件**：`app/models/user.py`
- **验收标准**：
  - 字段：id(UUID)、username、email、password_hash、role(enum: user/admin/developer)、is_active、created_at、updated_at。
  - 表名 `users`。
- **测试要求**：`tests/test_models.py` — 测试 User 模型字段和表名。
- **是否提交**：是。

### T2.4 创建 KnowledgeBase 模型

- **任务目标**：创建知识库数据库模型。
- **创建文件**：`app/models/knowledge_base.py`
- **验收标准**：
  - 字段：id(UUID)、name、description、owner_id(FK→users)、visibility(enum: private/team/public)、created_at、updated_at。
  - 表名 `knowledge_bases`。
- **测试要求**：`tests/test_models.py` — 测试 KnowledgeBase 模型。
- **是否提交**：是。

### T2.5 创建 Document 模型

- **任务目标**：创建文档数据库模型。
- **创建文件**：`app/models/document.py`
- **验收标准**：
  - 字段：id(UUID)、kb_id(FK)、filename、file_type、file_path、file_size、status(enum: uploaded/parsing/chunking/embedding/ready/error)、chunk_count、created_at、updated_at。
  - 表名 `documents`。
- **测试要求**：`tests/test_models.py` — 测试 Document 模型。
- **是否提交**：是。

### T2.6 创建 Chunk 模型

- **任务目标**：创建文档切片数据库模型。
- **创建文件**：`app/models/chunk.py`
- **验收标准**：
  - 字段：id(UUID)、document_id(FK)、kb_id(FK)、content、page、section_title、chunk_index、metadata(JSON)、embedding_id、created_at。
  - 表名 `chunks`。
- **测试要求**：`tests/test_models.py` — 测试 Chunk 模型。
- **是否提交**：是。

### T2.7 创建 ChatSession 与 ChatMessage 模型

- **任务目标**：创建会话和消息数据库模型。
- **创建文件**：`app/models/chat.py`
- **验收标准**：
  - ChatSession 字段：id(UUID)、user_id(FK)、kb_id(FK, nullable)、title、created_at、updated_at。
  - ChatMessage 字段：id(UUID)、session_id(FK)、role、content、citations(JSON)、created_at。
  - 表名 `chat_sessions`、`chat_messages`。
- **测试要求**：`tests/test_models.py` — 测试 ChatSession 和 ChatMessage 模型。
- **是否提交**：是。

### T2.8 创建 Agent 与 MCP 相关模型

- **任务目标**：创建 Agent 执行日志、MCP Server 注册、MCP Tool 和 MCP 调用日志模型。
- **创建文件**：`app/models/agent_run.py`、`app/models/mcp.py`
- **验收标准**：
  - AgentRun 字段：id、session_id、user_query、final_answer、status、steps(JSON)、latency_ms、created_at。
  - MCPServer 字段：id、name、transport、endpoint、enabled、timeout_seconds、created_at。
  - MCPTool 字段：id、server_id(FK)、name、description、input_schema(JSON)、permission_level。
  - MCPToolCall 字段：id、session_id、tool_name、tool_input(JSON)、tool_output(JSON)、status、latency_ms、created_at。
- **测试要求**：`tests/test_models.py` — 测试 AgentRun、MCPServer、MCPTool、MCPToolCall 模型。
- **是否提交**：是。

---

## 阶段三：用户认证

### T3.1 创建用户注册 Schema

- **任务目标**：定义用户注册和登录的 Pydantic Schema。
- **创建文件**：`app/schemas/user.py`、`app/schemas/auth.py`
- **验收标准**：
  - `UserCreate`：username、email、password（含校验）。
  - `UserLogin`：username、password。
  - `TokenResponse`：access_token、token_type。
  - `UserResponse`：id、username、email、role、created_at。
- **测试要求**：`tests/test_schemas.py` — 测试 schema 校验和序列化。
- **是否提交**：是。

### T3.2 创建 Auth Service

- **任务目标**：实现用户注册和登录业务逻辑。
- **创建文件**：`app/services/auth_service.py`
- **验收标准**：
  - `register(user_create)` 创建用户，检查用户名/邮箱唯一性，哈希密码。
  - `login(user_login)` 验证凭证，返回 JWT token。
  - `get_current_user(token)` 从 token 解析当前用户。
- **测试要求**：`tests/test_auth_service.py` — 使用内存数据库测试注册、登录、重复注册、错误密码。
- **是否提交**：是。

### T3.3 创建 Auth API 路由

- **任务目标**：实现认证相关 API 端点。
- **创建文件**：`app/api/__init__.py`、`app/api/auth.py`
- **修改文件**：`app/main.py`（注册路由）
- **验收标准**：
  - `POST /api/auth/register` 返回用户信息和 token。
  - `POST /api/auth/login` 返回 token。
  - `GET /api/auth/me` 返回当前用户信息（需认证）。
- **测试要求**：`tests/test_auth_api.py` — 使用 TestClient 测试三个端点。
- **是否提交**：是。

---

## 阶段四：知识库 CRUD

### T4.1 创建知识库 Schema

- **任务目标**：定义知识库的 Pydantic Schema。
- **创建文件**：`app/schemas/knowledge_base.py`
- **验收标准**：
  - `KnowledgeBaseCreate`：name、description、visibility。
  - `KnowledgeBaseUpdate`：name、description、visibility（可选）。
  - `KnowledgeBaseResponse`：包含 id、name、description、owner_id、visibility、document_count、chunk_count、created_at。
- **测试要求**：`tests/test_schemas.py` — 测试 schema 校验。
- **是否提交**：是。

### T4.2 创建 KnowledgeBase Service

- **任务目标**：实现知识库 CRUD 业务逻辑。
- **创建文件**：`app/services/kb_service.py`
- **验收标准**：
  - `create_kb(db, user_id, data)` 创建知识库。
  - `list_kbs(db, user_id)` 列出用户可访问的知识库。
  - `get_kb(db, kb_id)` 获取单个知识库详情。
  - `update_kb(db, kb_id, data)` 更新知识库。
  - `delete_kb(db, kb_id)` 删除知识库（级联删除文档和切片）。
- **测试要求**：`tests/test_kb_service.py` — 测试 CRUD 全部操作，包括权限和不存在情况。
- **是否提交**：是。

### T4.3 创建知识库 API 路由

- **任务目标**：实现知识库管理 API 端点。
- **创建文件**：`app/api/knowledge_base.py`
- **修改文件**：`app/main.py`（注册路由）
- **验收标准**：
  - `POST /api/kbs` 创建知识库。
  - `GET /api/kbs` 列出知识库。
  - `GET /api/kbs/{kb_id}` 获取详情。
  - `PUT /api/kbs/{kb_id}` 更新。
  - `DELETE /api/kbs/{kb_id}` 删除。
  - 所有端点需认证。
- **测试要求**：`tests/test_kb_api.py` — 使用 TestClient 测试所有端点。
- **是否提交**：是。

---

## 阶段五：文档上传与解析

### T5.1 创建文档上传 Schema

- **任务目标**：定义文档上传和响应的 Pydantic Schema。
- **创建文件**：`app/schemas/document.py`
- **验收标准**：
  - `DocumentUploadResponse`：id、kb_id、filename、file_type、file_size、status。
  - `DocumentResponse`：完整文档信息（含 chunk_count、created_at）。
  - `DocumentListResponse`：分页列表。
- **测试要求**：`tests/test_schemas.py` — 测试 schema。
- **是否提交**：是。

### T5.2 实现文件上传校验

- **任务目标**：实现上传文件类型、大小、MIME 校验逻辑。
- **创建文件**：`app/services/file_validator.py`
- **验收标准**：
  - 校验文件扩展名（允许 pdf、docx、md、txt、csv、xlsx）。
  - 校验 MIME 类型。
  - 校验文件大小（默认上限 50MB）。
  - 拒绝空文件和文件名包含 `..` 或 `/` 的文件。
- **测试要求**：`tests/test_file_validator.py` — 测试各种合法和非法文件。
- **是否提交**：是。

### T5.3 实现文件存储服务

- **任务目标**：实现原始文件本地存储服务。
- **创建文件**：`app/services/file_storage.py`
- **验收标准**：
  - `save_file(upload_file, kb_id)` 保存文件到 `storage/{kb_id}/{uuid}_{filename}`。
  - `get_file_path(file_path)` 返回文件绝对路径，校验路径在 storage/ 内。
  - `delete_file(file_path)` 删除文件。
  - 防止路径穿越，所有路径必须在 `storage/` 范围内。
- **测试要求**：`tests/test_file_storage.py` — 测试保存、读取、删除和路径穿越防护。
- **是否提交**：是。

### T5.4 实现 PDF 解析服务

- **任务目标**：使用 PyMuPDF 解析 PDF 文件，提取文本和元数据。
- **创建文件**：`app/services/parsers/pdf_parser.py`
- **验收标准**：
  - 提取每页文本、页码、页数。
  - 提取文档标题（如有）。
  - 提取章节标题（基于字体大小和样式）。
  - 异常时返回明确错误。
- **测试要求**：`tests/test_parsers.py` — 使用测试 PDF 文件测试解析结果。
- **是否提交**：是。

### T5.5 实现 DOCX 解析服务

- **任务目标**：使用 python-docx 解析 DOCX 文件。
- **创建文件**：`app/services/parsers/docx_parser.py`
- **验收标准**：
  - 提取段落文本和样式（标题、正文）。
  - 提取表格内容。
  - 保留章节结构。
- **测试要求**：`tests/test_parsers.py` — 使用测试 DOCX 文件。
- **是否提交**：是。

### T5.6 实现 Markdown/TXT 解析服务

- **任务目标**：解析 Markdown 和纯文本文件。
- **创建文件**：`app/services/parsers/md_parser.py`、`app/services/parsers/txt_parser.py`
- **验收标准**：
  - Markdown：提取标题层级、段落、代码块。
  - TXT：按空行分段，保留原文。
- **测试要求**：`tests/test_parsers.py` — 使用测试 MD/TXT 文件。
- **是否提交**：是。

### T5.7 实现 CSV/XLSX 解析服务

- **任务目标**：解析 CSV 和 Excel 文件。
- **创建文件**：`app/services/parsers/csv_parser.py`、`app/services/parsers/excel_parser.py`
- **验收标准**：
  - CSV：解析为表格文本，保留列名和数据行。
  - XLSX：解析每个 sheet 为独立段落。
  - 限制最大行数（默认 10000 行）。
- **测试要求**：`tests/test_parsers.py` — 使用测试 CSV/XLSX 文件。
- **是否提交**：是。

### T5.8 实现解析调度服务

- **任务目标**：根据文件类型统一调度解析器，返回标准化解析结果。
- **创建文件**：`app/services/parser_service.py`
- **验收标准**：
  - 根据 `file_type` 选择对应解析器。
  - 返回统一的 `ParsedDocument` 数据结构（含 text、pages、sections、tables 等）。
  - 不支持的文件类型抛出明确异常。
- **测试要求**：`tests/test_parser_service.py` — 测试各种文件类型的调度。
- **是否提交**：是。

### T5.9 创建文档上传 API

- **任务目标**：实现文档上传端点，串联校验→存储→解析→切片→向量化流程（初期可 mock 后续步骤）。
- **创建文件**：`app/api/document.py`
- **修改文件**：`app/main.py`（注册路由）
- **验收标准**：
  - `POST /api/kbs/{kb_id}/documents/upload` 上传文件。
  - 返回文档元数据和状态（status=uploaded，后续解析异步进行）。
  - `GET /api/kbs/{kb_id}/documents` 列出知识库下文档。
  - `GET /api/documents/{document_id}` 获取文档详情。
  - `DELETE /api/documents/{document_id}` 删除文档及其切片。
- **测试要求**：`tests/test_document_api.py` — 测试上传、列表、详情、删除。
- **是否提交**：是。

---

## 阶段六：文档切片

### T6.1 实现文本清洗工具

- **任务目标**：实现文本清洗函数，去除多余空白、控制字符、乱码。
- **创建文件**：`app/services/text_cleaner.py`
- **验收标准**：
  - 合并多余空格和换行。
  - 移除控制字符（保留换行和制表符用于结构）。
  - 统一中英文标点无影响（不做转换，只清理）。
- **测试要求**：`tests/test_text_cleaner.py` — 测试常见清洗场景。
- **是否提交**：是。

### T6.2 实现结构化切片器

- **任务目标**：基于文档结构（标题、章节、段落、表格）进行语义切片。
- **创建文件**：`app/services/chunker.py`
- **验收标准**：
  - 优先按标题/章节边界切分。
  - chunk_size 默认 500~800 中文字符，可配置。
  - chunk_overlap 默认 80~150 中文字符，可配置。
  - 保留表格完整性（表格不切开）。
  - 单个段落过长时按句子边界切分。
- **测试要求**：`tests/test_chunker.py` — 测试中英文文档切片，测试边界保留、表格完整性、overlap。
- **是否提交**：是。

### T6.3 实现切片元数据生成

- **任务目标**：为每个 chunk 生成结构化元数据。
- **创建文件**：合并到 `app/services/chunker.py`
- **验收标准**：
  - 每个 chunk 元数据包含：document_id、kb_id、page（如有）、section_title、chunk_index、start_char、end_char、token_count（估算）。
- **测试要求**：`tests/test_chunker.py` 中补充元数据测试。
- **是否提交**：是。

### T6.4 实现文档处理流水线

- **任务目标**：串联解析→清洗→切片→保存 chunk 的完整流水线。
- **创建文件**：`app/services/document_pipeline.py`
- **验收标准**：
  - `process_document(db, document_id)` 执行完整流水线。
  - 更新 document 状态：uploaded→parsing→chunking→ready。
  - 异常时更新状态为 error 并记录错误信息。
- **测试要求**：`tests/test_document_pipeline.py` — 端到端测试文档处理流程。
- **是否提交**：是。

---

## 阶段七：Embedding 与向量库

### T7.1 定义 Embedding 服务抽象

- **任务目标**：定义 Embedding 服务的 Protocol/ABC 接口，支持多种实现。
- **创建文件**：`app/services/embedding/base.py`
- **验收标准**：
  - `EmbeddingService` 抽象类，定义 `embed_texts(texts) -> List[List[float]]`。
  - `embed_query(text) -> List[float]`。
  - 支持批量处理，默认 batch_size。
- **测试要求**：`tests/test_embedding.py` — 测试接口定义（不测试具体实现）。
- **是否提交**：是。

### T7.2 实现 Fake Embedding 服务

- **任务目标**：实现 Fake Embedding 用于测试，生成固定维度向量。
- **创建文件**：`app/services/embedding/fake.py`
- **验收标准**：
  - `FakeEmbeddingService` 实现 `EmbeddingService` 接口。
  - 基于文本哈希生成确定性向量（相同文本→相同向量）。
  - 默认维度 1024。
- **测试要求**：`tests/test_embedding.py` — 测试 fake embedding 的确定性和维度。
- **是否提交**：是。

### T7.3 实现 BGE-M3 Embedding 服务

- **任务目标**：实现基于 OpenAI-compatible API 的 Embedding 服务。
- **创建文件**：`app/services/embedding/bge.py`
- **验收标准**：
  - 通过 OpenAI-compatible `/v1/embeddings` 接口调用 bge-m3。
  - 支持配置 base_url 和 api_key。
  - 支持 batch 请求和重试。
  - 实现 `EmbeddingService` 接口。
- **测试要求**：`tests/test_embedding.py` — 使用 mock API 测试。
- **是否提交**：是。

### T7.4 定义向量库抽象

- **任务目标**：定义向量数据库的抽象接口。
- **创建文件**：`app/services/vector_store/base.py`
- **验收标准**：
  - `VectorStore` 抽象类。
  - `add_vectors(ids, vectors, metadatas)` 添加向量。
  - `search(query_vector, top_k, filter)` 向量检索。
  - `delete(ids)` 删除向量。
  - `delete_by_filter(filter)` 按条件删除（如按 kb_id）。
- **测试要求**：`tests/test_vector_store.py` — 测试接口定义。
- **是否提交**：是。

### T7.5 实现 Chroma 向量库

- **任务目标**：基于 Chroma 实现向量存储和检索。
- **创建文件**：`app/services/vector_store/chroma_store.py`
- **验收标准**：
  - 实现 `VectorStore` 接口。
  - 按 kb_id 创建独立 collection（`kb_{kb_id}`）。
  - 支持 metadata 过滤（按 kb_id、document_id 过滤）。
- **测试要求**：`tests/test_vector_store.py` — 使用 chromadb 内存模式测试增删查。
- **是否提交**：是。

### T7.6 实现 Embedding + 向量库写入流水线

- **任务目标**：将文档 chunk 向量化并写入向量库。
- **创建文件**：`app/services/indexing.py`
- **验收标准**：
  - `index_chunks(db, kb_id, chunks)` 批量向量化并写入向量库。
  - 记录 embedding_id 到 chunk 记录。
  - 支持增量索引（新增 chunk）和删除同步。
- **测试要求**：`tests/test_indexing.py` — 使用 FakeEmbedding + Chroma 内存模式测试。
- **是否提交**：是。

---

## 阶段八：基础 RAG 问答与引用溯源

### T8.1 实现向量检索服务

- **任务目标**：对用户问题执行向量检索，返回候选 chunk。
- **创建文件**：`app/services/retrieval/vector_retriever.py`
- **验收标准**：
  - `retrieve(query, kb_id, top_k)` 返回 TopK chunk 及相似度分数。
  - 查询向量由 Embedding 服务生成。
  - 支持按 kb_id 过滤。
- **测试要求**：`tests/test_retrieval.py` — 使用 FakeEmbedding + Chroma 内存模式测试检索结果。
- **是否提交**：是。

### T8.2 实现上下文构造器

- **任务目标**：将检索结果构造为 LLM prompt context。
- **创建文件**：`app/services/context_builder.py`
- **验收标准**：
  - 将 chunk 列表格式化为上下文文本。
  - 包含 chunk 索引、来源标记。
  - 不超过模型最大上下文长度。
  - 按分数降序排列。
- **测试要求**：`tests/test_context_builder.py` — 测试上下文格式、截断、排序。
- **是否提交**：是。

### T8.3 定义 LLM 服务抽象

- **任务目标**：定义 LLM 调用的抽象接口。
- **创建文件**：`app/services/llm/base.py`
- **验收标准**：
  - `LLMService` 抽象类。
  - `generate(prompt, system_prompt, temperature)` 返回文本。
  - `generate_stream(prompt, system_prompt, temperature)` 返回文本流（生成器）。
- **测试要求**：无（纯接口定义，无需测试）。
- **是否提交**：是。

### T8.4 实现 Fake LLM 服务

- **任务目标**：实现 Fake LLM 用于测试。
- **创建文件**：`app/services/llm/fake.py`
- **验收标准**：
  - 基于 prompt 中的关键词返回预设响应。
  - 支持流式输出（逐字返回）。
  - 请求中可以包含 mock 响应列表。
- **测试要求**：`tests/test_llm.py` — 测试 fake LLM 的生成和流式输出。
- **是否提交**：是。

### T8.5 实现 OpenAI-compatible LLM 服务

- **任务目标**：基于 OpenAI-compatible API 封装 LLM 调用。
- **创建文件**：`app/services/llm/openai_llm.py`
- **验收标准**：
  - 通过 `/v1/chat/completions` 调用模型。
  - 支持 stream 模式。
  - 记录 token 用量和耗时。
  - 支持重试和超时配置。
- **测试要求**：`tests/test_llm.py` — 使用 mock API 测试。
- **是否提交**：是。

### T8.6 实现引用溯源服务

- **任务目标**：从 LLM 回答中提取引用，关联回原始 chunk。
- **创建文件**：`app/services/citation.py`
- **验收标准**：
  - 解析 LLM 回答中的引用标记（如 `[1]`、`[doc1]`）。
  - 返回引用列表：document_id、chunk_id、filename、page、section_title、score、content_preview。
  - 如果回答中无引用标记，根据 LLM 回答与 chunk 的内容匹配度推断引用。
- **测试要求**：`tests/test_citation.py` — 测试引用解析和匹配。
- **是否提交**：是。

### T8.7 实现基础 RAG 问答服务

- **任务目标**：串联检索→上下文构造→LLM 生成→引用溯源的完整 RAG 流程。
- **创建文件**：`app/services/rag_service.py`
- **验收标准**：
  - `ask(query, kb_id, session_id)` 执行完整 RAG 流程。
  - 返回 answer 和 citations。
  - 处理检索结果为空的情况（返回"未找到相关信息"）。
- **测试要求**：`tests/test_rag_service.py` — 使用 Fake 组件端到端测试。
- **是否提交**：是。

### T8.8 创建检索与问答 API

- **任务目标**：实现检索和 RAG 问答的 REST API。
- **创建文件**：`app/api/retrieval.py`、`app/api/chat.py`
- **修改文件**：`app/main.py`（注册路由）
- **验收标准**：
  - `POST /api/retrieval/search` 返回检索结果和分数。
  - `POST /api/chat` 返回 answer 和 citations。
  - `GET /api/chat/sessions/{session_id}` 返回对话历史。
- **测试要求**：`tests/test_chat_api.py` — 使用 TestClient + Fake 组件测试。
- **是否提交**：是。

---

## 阶段九：混合检索与 Reranker

### T9.1 实现 BM25 索引与检索服务

- **任务目标**：基于 rank-bm25 实现关键词检索。
- **创建文件**：`app/services/retrieval/bm25_retriever.py`
- **验收标准**：
  - 按 kb_id 独立维护 BM25 索引。
  - `build_index(kb_id, chunks)` 构建/更新索引。
  - `retrieve(query, kb_id, top_k)` 返回 BM25 检索结果。
  - 新增/删除 chunk 时支持增量更新索引。
- **测试要求**：`tests/test_bm25.py` — 测试索引构建、检索、增量更新。
- **是否提交**：是。

### T9.2 实现结果融合策略

- **任务目标**：融合向量检索和 BM25 检索结果。
- **创建文件**：`app/services/retrieval/fusion.py`
- **验收标准**：
  - 实现 RRF（Reciprocal Rank Fusion）融合算法。
  - 支持权重调整（向量检索权重、BM25 权重）。
  - 去重（同一 chunk 在两个结果集中时保留较高分）。
- **测试要求**：`tests/test_fusion.py` — 测试 RRF 融合和去重。
- **是否提交**：是。

### T9.3 实现 Reranker 服务抽象与 Fake 实现

- **任务目标**：定义 Reranker 抽象接口并提供 Fake 实现。
- **创建文件**：`app/services/reranker/base.py`、`app/services/reranker/fake.py`
- **验收标准**：
  - `RerankerService` 抽象类，定义 `rerank(query, chunks, top_k)`。
  - `FakeReranker` 随机打乱并截断（仅用于测试链路）。
- **测试要求**：`tests/test_reranker.py` — 测试接口和 Fake 实现。
- **是否提交**：是。

### T9.4 实现 BGE Reranker 服务

- **任务目标**：基于 OpenAI-compatible API 或本地模型实现 Reranker。
- **创建文件**：`app/services/reranker/bge_reranker.py`
- **验收标准**：
  - 对候选 chunk 列表进行相关性打分。
  - 返回排序后的 TopK chunk 及 Reranker 分数。
  - 支持 batch 请求和超时配置。
- **测试要求**：`tests/test_reranker.py` — 使用 mock API 测试。
- **是否提交**：是。

### T9.5 集成混合检索流水线

- **任务目标**：将向量检索→BM25→融合→Reranker 集成为统一的检索流水线。
- **创建文件**：`app/services/retrieval/hybrid_pipeline.py`
- **验收标准**：
  - `search(query, kb_id, options)` 执行完整混合检索流水线。
  - 支持配置开关：是否启用 BM25、是否启用 Reranker、各阶段 TopK。
  - 返回最终 TopK chunk 及各阶段分数。
- **测试要求**：`tests/test_hybrid_pipeline.py` — 使用 Fake 组件端到端测试。
- **是否提交**：是。

---

## 阶段十：LangGraph Agent 工作流

### T10.1 定义 Agent 状态

- **任务目标**：定义 LangGraph 工作流的状态结构。
- **创建文件**：`app/agents/state.py`
- **验收标准**：
  - `AgentState` TypedDict 包含：query、kb_id、session_id、messages、retrieved_chunks、tool_calls、tool_results、answer、citations、verification_result、status、step_count、error。
  - 使用 `Annotated` 和 `operator.add` 实现 messages 的累加。
- **测试要求**：`tests/test_agent_state.py` — 测试状态创建、字段更新和序列化。
- **是否提交**：是。

### T10.2 实现 Query Analyzer Agent

- **任务目标**：分析用户问题的意图、类型和是否需要工具调用。
- **创建文件**：`app/agents/query_analyzer.py`
- **验收标准**：
  - `analyze_query(state)` 作为 LangGraph 节点函数。
  - 判断问题类型：knowledge_qa / data_analysis / document_analysis / comparison / general。
  - 判断是否需要检索、是否需要工具调用。
  - 输出分析结果写入 state。
- **测试要求**：`tests/test_query_analyzer.py` — 使用 FakeLLM 测试不同问题类型的分析结果。
- **是否提交**：是。

### T10.3 实现 Retriever Agent

- **任务目标**：根据问题分析结果执行知识库检索。
- **创建文件**：`app/agents/retriever.py`
- **验收标准**：
  - `retrieve(state)` 作为 LangGraph 节点函数。
  - 根据 query_analysis 选择检索策略（纯向量 / 混合检索）。
  - 将检索结果写入 state.retrieved_chunks。
- **测试要求**：`tests/test_retriever_agent.py` — 使用 Fake 检索服务测试。
- **是否提交**：是。

### T10.4 实现 Answer Generator Agent

- **任务目标**：基于检索证据生成最终回答。
- **创建文件**：`app/agents/answer_generator.py`
- **验收标准**：
  - `generate_answer(state)` 作为 LangGraph 节点函数。
  - 构造包含检索证据和系统指令的 prompt。
  - 要求 LLM 在回答中标注引用 `[N]`。
  - 证据不足时返回"信息不足，无法回答"。
- **测试要求**：`tests/test_answer_generator.py` — 使用 FakeLLM 测试不同检索结果下的回答。
- **是否提交**：是。

### T10.5 实现 Verifier Agent

- **任务目标**：校验回答是否有证据支持，引用是否准确。
- **创建文件**：`app/agents/verifier.py`
- **验收标准**：
  - `verify(state)` 作为 LangGraph 节点函数。
  - 检查回答中的声明是否有对应 chunk 支持。
  - 检查引用编号是否与实际 chunk 对应。
  - 输出验证结果（pass / partial / fail）和具体问题列表。
- **测试要求**：`tests/test_verifier.py` — 使用 FakeLLM 测试验证逻辑。
- **是否提交**：是。

### T10.6 组装 LangGraph 工作流

- **任务目标**：将各个 Agent 节点组装为 LangGraph StateGraph。
- **创建文件**：`app/agents/graph.py`
- **验收标准**：
  - 定义节点：query_analyzer → retriever → answer_generator → verifier。
  - 定义条件边：verify 不通过时重试（最多 2 次），或返回"无法生成可靠回答"。
  - 工作流可编译为 `Runnable` 并通过 `invoke` 执行。
  - 设置最大步数限制（默认 10 步）。
- **测试要求**：`tests/test_graph.py` — 使用 Fake 组件端到端测试工作流。
- **是否提交**：是。

### T10.7 实现 Agent 执行日志

- **任务目标**：记录每次 Agent 运行的输入、步骤、输出和耗时。
- **创建文件**：`app/services/agent_logger.py`
- **验收标准**：
  - `log_agent_run(db, session_id, state, latency_ms)` 写入 agent_runs 表。
  - 记录每个节点的执行状态和耗时。
  - 记录最终答案和验证结果。
- **测试要求**：`tests/test_agent_logger.py` — 使用内存数据库测试日志写入。
- **是否提交**：是。

### T10.8 创建 Agent API

- **任务目标**：提供 Agent 问答的 REST API。
- **创建文件**：`app/api/agent.py`
- **修改文件**：`app/main.py`（注册路由）
- **验收标准**：
  - `POST /api/agent/chat` 触发 Agent 工作流，返回 answer 和 citations。
  - 返回 agent_run_id 用于追踪。
  - 支持查询参数控制是否启用 Verifier。
- **测试要求**：`tests/test_agent_api.py` — 使用 TestClient + Fake 组件测试。
- **是否提交**：是。

---

## 阶段十一：MCP Client

### T11.1 定义 MCP Server 注册表

- **任务目标**：实现 MCP Server 的注册、发现和管理。
- **创建文件**：`app/mcp_client/registry.py`
- **验收标准**：
  - `register_server(name, transport, endpoint)` 注册 MCP Server。
  - `get_server(name)` 获取注册的 Server。
  - `list_servers()` 列出所有已注册 Server。
  - `remove_server(name)` 注销 Server。
  - 支持从数据库（mcp_servers 表）加载初始注册信息。
- **测试要求**：`tests/test_mcp_registry.py` — 测试注册、发现、注销。
- **是否提交**：是。

### T11.2 实现 MCP Tool 发现

- **任务目标**：连接 MCP Server 并获取暴露的工具列表和参数 schema。
- **创建文件**：`app/mcp_client/tool_discovery.py`
- **验收标准**：
  - `discover_tools(server_name)` 返回工具列表及 input_schema。
  - 缓存工具列表（支持手动刷新）。
  - 连接失败时返回明确错误。
- **测试要求**：`tests/test_mcp_discovery.py` — 使用 Mock MCP Server 测试。
- **是否提交**：是。

### T11.3 实现 MCP Tool 调用

- **任务目标**：按工具名称调用 MCP Server 并解析返回结果。
- **创建文件**：`app/mcp_client/tool_caller.py`
- **验收标准**：
  - `call_tool(server_name, tool_name, arguments)` 调用工具。
  - 支持 stdio 和 HTTP 两种 transport。
  - 参数校验（使用工具的 input_schema）。
  - 超时控制（默认 30 秒，可配置）。
  - 返回解析后的结果。
- **测试要求**：`tests/test_mcp_caller.py` — 使用 Mock MCP Server 测试调用和超时。
- **是否提交**：是。

### T11.4 实现 MCP 权限控制

- **任务目标**：对 MCP 工具调用进行权限校验。
- **创建文件**：`app/mcp_client/permissions.py`
- **验收标准**：
  - 每个工具定义 permission_level（public / user / admin）。
  - 调用前校验当前用户是否有权调用。
  - 高风险工具（如 SQL execute）记录审计日志。
- **测试要求**：`tests/test_mcp_permissions.py` — 测试不同权限级别的调用。
- **是否提交**：是。

### T11.5 实现 MCP 调用日志

- **任务目标**：记录所有 MCP 工具调用的输入、输出、状态和耗时。
- **创建文件**：`app/mcp_client/call_logger.py`
- **验收标准**：
  - 写入 mcp_tool_calls 表。
  - 记录 tool_name、tool_input、tool_output、status、latency_ms。
  - 异常时记录 error 信息。
- **测试要求**：`tests/test_mcp_logger.py` — 使用内存数据库测试。
- **是否提交**：是。

### T11.6 创建 MCP Client API

- **任务目标**：提供 MCP Server 管理和工具调用的 REST API。
- **创建文件**：`app/api/mcp.py`
- **修改文件**：`app/main.py`（注册路由）
- **验收标准**：
  - `GET /api/mcp/servers` 列出注册的 MCP Server。
  - `GET /api/mcp/tools` 列出所有可用工具。
  - `POST /api/mcp/tools/refresh` 刷新工具列表。
  - `POST /api/mcp/tools/call` 调用指定工具（需认证和权限校验）。
- **测试要求**：`tests/test_mcp_api.py` — 使用 TestClient + Mock MCP Server 测试。
- **是否提交**：是。

---

## 阶段十二：Knowledge Base MCP Server

### T12.1 创建 KB MCP Server 骨架

- **任务目标**：使用 FastMCP 创建 Knowledge Base MCP Server 基础框架。
- **创建文件**：`app/mcp_servers/knowledge_base/__init__.py`、`app/mcp_servers/knowledge_base/server.py`
- **验收标准**：
  - 使用 FastMCP 创建 MCP Server 实例。
  - Server 可以独立启动（`python -m app.mcp_servers.knowledge_base.server`）。
  - 注册 3 个工具的占位函数，返回 mock 数据。
- **测试要求**：`tests/test_kb_mcp_server.py` — 测试 Server 启动和工具注册。
- **是否提交**：是。

### T12.2 实现 search_knowledge_base 工具

- **任务目标**：通过 MCP 工具暴露知识库检索能力。
- **修改文件**：`app/mcp_servers/knowledge_base/server.py`
- **验收标准**：
  - 输入参数：query(str)、kb_id(str)、top_k(int, 默认 10)。
  - 输出：chunk 列表，含 content、document_id、filename、score、page、section_title。
  - 支持按 kb_id 过滤。
- **测试要求**：`tests/test_kb_mcp_server.py` — 测试工具参数 schema 和 mock 调用。
- **是否提交**：是。

### T12.3 实现 get_document_detail 工具

- **任务目标**：通过 MCP 工具获取文档元数据。
- **修改文件**：`app/mcp_servers/knowledge_base/server.py`
- **验收标准**：
  - 输入：document_id(str)。
  - 输出：filename、file_type、status、chunk_count、上传时间等。
- **测试要求**：`tests/test_kb_mcp_server.py` — 测试工具。
- **是否提交**：是。

### T12.4 实现 get_chunk_context 工具

- **任务目标**：通过 MCP 工具获取指定 chunk 的上下文（前后相邻 chunk）。
- **修改文件**：`app/mcp_servers/knowledge_base/server.py`
- **验收标准**：
  - 输入：chunk_id(str)、context_size(int, 默认 2)。
  - 输出：目标 chunk 及其前后 N 个 chunk 的内容。
- **测试要求**：`tests/test_kb_mcp_server.py` — 测试工具。
- **是否提交**：是。

---

## 阶段十三：SQL Query MCP Server

### T13.1 创建 SQL MCP Server 骨架

- **任务目标**：使用 FastMCP 创建 SQL Query MCP Server 基础框架。
- **创建文件**：`app/mcp_servers/sql_query/__init__.py`、`app/mcp_servers/sql_query/server.py`
- **验收标准**：
  - 使用 SQLite 作为默认数据源（可配置）。
  - 注册 3 个工具的占位函数。
- **测试要求**：`tests/test_sql_mcp_server.py` — 测试 Server 启动。
- **是否提交**：是。

### T13.2 实现 list_tables 工具

- **任务目标**：列出数据源中所有表名。
- **修改文件**：`app/mcp_servers/sql_query/server.py`
- **验收标准**：
  - 无参数。
  - 输出：表名列表和每个表的行数估算。
- **测试要求**：`tests/test_sql_mcp_server.py` — 使用测试 SQLite 数据库测试。
- **是否提交**：是。

### T13.3 实现 describe_table 工具

- **任务目标**：返回指定表的列名、类型、是否可空等 schema 信息。
- **修改文件**：`app/mcp_servers/sql_query/server.py`
- **验收标准**：
  - 输入：table_name(str)。
  - 输出：列名、类型、是否为主键、是否可空、示例值（前 3 行）。
  - 表不存在时返回明确错误。
- **测试要求**：`tests/test_sql_mcp_server.py` — 测试。
- **是否提交**：是。

### T13.4 实现 execute_readonly_sql 工具

- **任务目标**：安全执行只读 SQL 查询。
- **修改文件**：`app/mcp_servers/sql_query/server.py`
- **验收标准**：
  - 输入：sql_query(str)、limit(int, 默认 100)。
  - 安全校验：仅允许 SELECT，禁止 DROP/DELETE/UPDATE/INSERT/ALTER/TRUNCATE。
  - 参数化查询，禁止拼接用户输入。
  - 限制返回行数（默认 100，最大 1000）。
  - 设置查询超时（默认 5 秒）。
  - 所有查询记录日志。
- **测试要求**：`tests/test_sql_mcp_server.py` — 测试 SELECT 成功、危险 SQL 拒绝、超时、行数限制。
- **是否提交**：是。

---

## 阶段十四：MCP Tool Agent 接入 LangGraph

### T14.1 实现 Tool Planner Agent

- **任务目标**：根据用户问题分析结果，规划需要调用哪些 MCP 工具及参数。
- **创建文件**：`app/agents/tool_planner.py`
- **验收标准**：
  - `plan_tools(state)` 作为 LangGraph 节点函数。
  - 根据 query_analysis 判断需要调用哪些 MCP 工具。
  - 生成工具调用计划（工具名、参数）。
  - 写入 state.tool_calls。
- **测试要求**：`tests/test_tool_planner.py` — 使用 FakeLLM 测试规划逻辑。
- **是否提交**：是。

### T14.2 实现 MCP Tool Agent

- **任务目标**：统一执行 MCP 工具调用，解析结果，处理错误。
- **创建文件**：`app/agents/mcp_tool_agent.py`
- **验收标准**：
  - `execute_tools(state)` 作为 LangGraph 节点函数。
  - 遍历 state.tool_calls，依次调用 MCP Client。
  - 结果写入 state.tool_results。
  - 单个工具失败不影响其他工具，错误记录到 results。
- **测试要求**：`tests/test_mcp_tool_agent.py` — 使用 Mock MCP Client 测试。
- **是否提交**：是。

### T14.3 将 MCP 节点集成到 LangGraph 工作流

- **任务目标**：将 Tool Planner Agent 和 MCP Tool Agent 加入 StateGraph。
- **修改文件**：`app/agents/graph.py`
- **验收标准**：
  - 新增条件边：query_analyzer 判断需要工具时 → tool_planner → mcp_tool_agent → answer_generator。
  - 不需要工具时直接走原有 retriever → answer_generator 路径。
  - 端到端工作流通畅。
- **测试要求**：`tests/test_graph.py` — 补充工具调用路径测试。
- **是否提交**：是。

---

## 阶段十五：WebSocket 流式输出

### T15.1 定义 WebSocket 事件 Schema

- **任务目标**：定义 WebSocket 流式输出的事件类型和数据结构。
- **创建文件**：`app/schemas/ws_events.py`
- **验收标准**：
  - 定义事件类型枚举：query_analyzed、retrieval_started、retrieval_completed、mcp_tool_call、mcp_tool_result、answer_delta、citation、error、done。
  - 每个事件有对应的 Pydantic model。
- **测试要求**：`tests/test_schemas.py` — 测试事件序列化。
- **是否提交**：是。

### T15.2 实现 WebSocket 连接管理器

- **任务目标**：管理 WebSocket 连接的生命周期。
- **创建文件**：`app/services/ws_manager.py`
- **验收标准**：
  - `connect(websocket, session_id)` 注册连接。
  - `disconnect(session_id)` 注销连接。
  - `send_event(session_id, event)` 发送事件到指定会话。
  - `broadcast_event(event)` 广播事件。
  - 支持同一会话多个连接（多设备）。
- **测试要求**：`tests/test_ws_manager.py` — 测试连接、发送、断开。
- **是否提交**：是。

### T15.3 实现 Agent 流式工作流

- **任务目标**：在 Agent 工作流执行过程中通过 WebSocket 推送事件。
- **创建文件**：`app/services/streaming_agent.py`
- **验收标准**：
  - 每个 Agent 节点执行前后通过 WebSocket 推送事件。
  - LLM 生成时以 answer_delta 事件逐 token 推送。
  - 工具调用时推送 mcp_tool_call 和 mcp_tool_result 事件。
  - 完成时推送 done 事件。
- **测试要求**：`tests/test_streaming_agent.py` — 使用 Fake 组件测试事件流。
- **是否提交**：是。

### T15.4 创建 WebSocket 端点

- **任务目标**：实现 WebSocket 流式问答端点。
- **创建文件**：`app/api/ws.py`
- **修改文件**：`app/main.py`（注册 WebSocket 路由）
- **验收标准**：
  - `WS /api/chat/stream` 建立 WebSocket 连接。
  - 接收 JSON 消息（query、kb_id、session_id）。
  - 触发 Agent 工作流，流式推送事件。
  - 支持停止生成（接收 cancel 消息）。
  - 异常时推送 error 事件并关闭连接。
- **测试要求**：`tests/test_ws_api.py` — 使用 TestClient WebSocket 测试端点。
- **是否提交**：是。

### T15.5 完善 Chat Session API

- **任务目标**：完善会话管理和多轮对话支持。
- **修改文件**：`app/api/chat.py`、`app/services/chat_service.py`
- **验收标准**：
  - `POST /api/chat/sessions` 创建新会话。
  - `GET /api/chat/sessions` 列出用户会话。
  - `GET /api/chat/sessions/{session_id}` 获取会话历史和消息。
  - `DELETE /api/chat/sessions/{session_id}` 删除会话。
  - 多轮对话上下文由 session 中的历史消息自动构建。
- **测试要求**：`tests/test_chat_api.py` — 补充多轮对话测试。
- **是否提交**：是。

---

## 阶段十六：Docker Compose、README 与面试文档

### T16.1 创建 Dockerfile

- **任务目标**：为 FastAPI 后端创建 Docker 镜像构建文件。
- **创建文件**：`docker/Dockerfile`
- **验收标准**：
  - 基于 Python 3.10+ slim 镜像。
  - 安装依赖，复制代码。
  - 暴露 8000 端口。
  - 使用 uvicorn 启动。
- **测试要求**：`docker build -f docker/Dockerfile .` 构建成功。
- **是否提交**：是。

### T16.2 创建 docker-compose.yml

- **任务目标**：编排后端服务、PostgreSQL、Redis、Chroma 等所有服务。
- **创建文件**：`docker/docker-compose.yml`
- **验收标准**：
  - 包含服务：backend、postgres、redis、chroma。
  - 环境变量通过 .env 文件注入。
  - 数据卷持久化。
  - 服务健康检查。
  - 网络配置。
- **测试要求**：`docker compose -f docker/docker-compose.yml config` 检查配置有效性。
- **是否提交**：是。

### T16.3 创建项目 README.md

- **任务目标**：编写项目 README，包含项目简介、架构图、快速开始、API 文档链接、部署说明。
- **创建文件**：`README.md`
- **验收标准**：
  - 包含项目名称和一句话描述。
  - 包含技术架构图（ASCII art 或引用图片）。
  - 包含本地开发启动步骤。
  - 包含 Docker Compose 部署步骤。
  - 包含核心 API 列表。
  - 包含项目目录结构说明。
- **测试要求**：无（文档文件）。
- **是否提交**：是。

### T16.4 创建 INTERVIEW_NOTES.md

- **任务目标**：编写面试展示文档，供面试时快速回顾项目要点。
- **创建文件**：`docs/INTERVIEW_NOTES.md`
- **验收标准**：
  - 包含项目一句话定位。
  - 包含核心架构图。
  - 包含关键技术选型和理由。
  - 包含 MCP、RAG、LangGraph 三者关系说明。
  - 包含个人贡献总结。
  - 包含高频面试问答（对齐 RESUME_GUIDE.md 第 8 节）。
- **测试要求**：无（文档文件）。
- **是否提交**：是。

### T16.5 整体验收测试

- **任务目标**：运行所有测试，确保全部通过。
- **执行命令**：`pytest tests/ -v`
- **验收标准**：所有测试绿色通过，无 skip（除非有明确理由）。
- **测试要求**：`pytest tests/ -v --cov=app --cov-report=term-missing`。
- **是否提交**：否（仅验证，如发现问题则修复后提交）。

---

## 附录：任务统计

| 阶段 | 任务数 | 说明 |
|------|--------|------|
| 阶段零：项目初始化 | 5 | 目录结构、配置文件、Git 初始化、TASKS.md |
| 阶段一：FastAPI 基础骨架 | 5 | 配置、日志、异常、健康检查、安全 |
| 阶段二：数据库与基础模型 | 8 | 会话管理、8 个数据库模型 |
| 阶段三：用户认证 | 3 | Schema、Service、API |
| 阶段四：知识库 CRUD | 3 | Schema、Service、API |
| 阶段五：文档上传与解析 | 9 | 校验、存储、5 种解析器、调度、API |
| 阶段六：文档切片 | 4 | 清洗、切片、元数据、流水线 |
| 阶段七：Embedding 与向量库 | 6 | 抽象、Fake、BGE-M3、向量库抽象、Chroma、写入流水线 |
| 阶段八：基础 RAG 问答 | 8 | 检索、上下文、LLM 抽象+Fake+OpenAI、引用、RAG 服务、API |
| 阶段九：混合检索与 Reranker | 5 | BM25、融合、Reranker 抽象+Fake+BGE、混合流水线 |
| 阶段十：LangGraph Agent | 8 | 状态、4 个 Agent 节点、工作流组装、日志、API |
| 阶段十一：MCP Client | 6 | 注册表、工具发现、调用、权限、日志、API |
| 阶段十二：KB MCP Server | 4 | 骨架 + 3 个工具 |
| 阶段十三：SQL MCP Server | 4 | 骨架 + 3 个工具 |
| 阶段十四：MCP + Agent 集成 | 3 | Tool Planner、MCP Tool Agent、工作流集成 |
| 阶段十五：WebSocket 流式输出 | 5 | 事件 Schema、连接管理、流式 Agent、WS 端点、Chat API |
| 阶段十六：部署与文档 | 5 | Dockerfile、Compose、README、INTERVIEW_NOTES、验收测试 |
| **合计** | **83** | |

---

> **使用说明**：
> 1. 每个任务完成后运行指定测试，测试通过后再提交。
> 2. 如果用户要求跳过顺序，先说明风险，再按用户指定任务执行。
> 3. 每个阶段内任务尽量按编号顺序执行。
> 4. P2/P3 优先级的功能可在 P1 全部完成后统一补充。
