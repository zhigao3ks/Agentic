# MCP-Agentic RAG 后端系统 — 技术文档

## 1. 系统概述

本系统是一个面向企业知识库问答与数据分析场景的大模型应用后端，核心能力包括文档解析、RAG 检索增强、LangGraph Agent 工作流编排、MCP 工具协议接入和 WebSocket 流式输出。

### 1.1 技术架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户 / 前端页面 / API Client                │
└──────┬──────────────┬──────────────┬──────────────┬─────────┘
       │ REST API     │ WebSocket    │ MCP Client   │
       ▼              ▼              ▼              ▼
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI 后端服务                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ 认证模块  │ │ 知识库   │ │ 文档管理  │ │ 检索/问答     │   │
│  │ JWT+bcrypt│ │ CRUD     │ │ 6种格式  │ │ 混合检索      │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ Agent API│ │ MCP管理  │ │ WebSocket│ │ 会话管理      │   │
│  │ 7节点工作流│ │ 注册/调用 │ │ 流式输出  │ │ 多轮对话      │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
└──────────────────────────────────────────────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────────────────────────────┐
│PostgreSQL│ │  Redis   │ │          ChromaDB               │
│ 10张表   │ │ 会话缓存  │ │   向量索引 (按kb_id分collection) │
└──────────┘ └──────────┘ └──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                  LangGraph Agent 工作流                       │
│  query_analyzer → tool_planner → mcp_tool_agent             │
│       │                            │                        │
│       └── retriever ←──────────────┘                        │
│                 │                                            │
│          answer_generator → verifier                        │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    MCP 工具协议层                              │
│  ┌─────────────────────┐  ┌─────────────────────┐           │
│  │ KB MCP Server (x3)  │  │ SQL MCP Server (x3) │           │
│  │ search / detail /    │  │ list / describe /    │           │
│  │ chunk_context        │  │ execute_readonly    │           │
│  └─────────────────────┘  └─────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    LLM 模型服务层                              │
│  LiteLLM / vLLM / Ollama / OpenAI-compatible API            │
└──────────────────────────────────────────────────────────────┘
```

## 2. 数据流程详解

### 2.1 文档入库流程

```
用户上传文件
    │
    ▼
[1. 文件校验] file_validator.py
    │  - 扩展名校验 (pdf/docx/md/txt/csv/xlsx)
    │  - MIME 类型校验
    │  - 路径穿越检测
    │  - 大小限制 (MAX_UPLOAD_SIZE_MB)
    │
    ▼
[2. 文件存储] file_storage.py
    │  - 保存到 storage/{kb_id}/{uuid}_{filename}
    │  - 返回相对路径
    │
    ▼
[3. 文档解析] parser_service.py → 各解析器
    │  PDF   → PyMuPDF (fitz)
    │  DOCX  → python-docx
    │  MD    → 标题层级提取
    │  TXT   → 按空行分段
    │  CSV   → csv.reader
    │  XLSX  → openpyxl
    │  输出: ParsedDocument(text, pages, sections, metadata)
    │
    ▼
[4. 文本清洗] text_cleaner.py
    │  - 移除控制字符 (\\x00-\\x1f)
    │  - 统一换行为 \\n
    │  - 合并多个空行
    │  - 去除行首行尾空白
    │
    ▼
[5. 结构化切片] chunker.py
    │  - 按段落边界切分 (双换行)
    │  - 过长段落按句子边界切分 (。！？等)
    │  - chunk_size=800, chunk_overlap=120
    │  - 保留表格完整性
    │  - 生成元数据: page, section_title, start_char, end_char, token_count
    │
    ▼
[6. 向量化入库] indexing.py
    │  - 批量调用 Embedding 服务 (batch_size=32)
    │  - 写入 ChromaDB (collection="kb_{kb_id}")
    │  - 回写 embedding_id 到 chunks 表
    │
    ▼
[7. 状态更新] document.status = READY
```

### 2.2 RAG 问答流程

```
用户问题
    │
    ▼
[1. 问题分析] Query Analyzer Agent
    │  - 分析问题类型: knowledge_qa / data_analysis / general
    │  - 判断是否需要检索 / 工具调用
    │  - 提取关键词
    │
    ├── 普通知识问答 ──────────────────────────┐
    │                                         │
    ▼                                         ▼
[2a. 知识检索]                          [2b. 工具规划]
    Retriever Agent                      Tool Planner Agent
    │                                         │
    ▼                                         ▼
[3a. 混合检索]                          [3b. MCP执行]
    向量检索(Top20)  BM25检索(Top20)      MCP Tool Agent
         │              │                   │
         └── RRF融合 ──┘                   │
               │                           │
               ▼                           │
        Reranker 精排                       │
         (TopK=5~8)                         │
               │                           │
               └────────┬──────────────────┘
                       ▼
[4. 上下文构造] context_builder.py
    │  - 编号 [1] [2] ...
    │  - 按分数排序
    │  - 截断超长上下文 (MAX_CONTEXT_CHARS=4000)
    │
    ▼
[5. LLM 生成] Answer Generator Agent
    │  - 系统 Prompt: "基于上下文回答，标注引用编号"
    │  - 调用 LLM (Fake / OpenAI-compatible)
    │  - 证据不足时: "当前知识库中没有找到相关信息"
    │
    ▼
[6. 引用溯源] citation.py
    │  - 正则提取 [N] 引用标记
    │  - 关联回 chunk 元数据
    │  - 返回 document_id, chunk_id, page, section, score, preview
    │
    ▼
[7. 答案校验] Verifier Agent
    │  - 检查回答是否有证据支持
    │  - 校验引用准确性
    │  - 输出: pass / partial / fail
    │
    ▼
返回 {answer, citations, verification}
```

### 2.3 Agent 工作流状态流转

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ query_analyzer  │  → 分析问题：query_type, needs_retrieval, needs_tools
└────────┬────────┘
         │
    ┌────┴────┐ needs_tools?
    │ YES     │ NO
    ▼         ▼
┌──────────┐ ┌──────────┐
│  tool_   │ │ retriever│ → 混合检索 + Reranker
│  planner │ └─────┬────┘
└────┬─────┘       │
     │             │
┌────┴────┐        │
│has_calls?│ NO ───┘
│ YES      │
▼          │
┌──────────┐│
│mcp_tool  ││ → 逐个执行 MCP 工具调用
│_agent    ││
└────┬─────┘│
     │      │
     └──┬───┘
        ▼
┌─────────────────┐
│answer_generator │ → 构造 Prompt + LLM 生成
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    verifier     │ → 校验：pass / partial / fail
└────────┬────────┘
         │
         ▼
┌─────────────┐
│     END     │
└─────────────┘

最大步数: 10 (recursion_limit)
```

### 2.4 WebSocket 流式事件时序

```
Client                    Server
  │                         │
  │── WS Connect ──────────→│  accept()
  │                         │
  │── {"query":"...", ─────→│  run_streaming_agent()
  │    "kb_id":"..."}       │
  │                         │
  │←─ query_analyzed ──────│  {query_type, needs_tools}
  │                         │
  │←─ retrieval_started ───│  "开始检索知识库"
  │                         │
  │←─ retrieval_completed ─│  {chunk_count}
  │                         │
  │←─ mcp_tool_call ───────│  {tool, arguments} (可选)
  │←─ mcp_tool_result ────│  {tool, is_error} (可选)
  │                         │
  │←─ answer_delta ────────│  "根"  (token 级流式)
  │←─ answer_delta ────────│  "据"
  │←─ answer_delta ────────│  "文"
  │←─ answer_delta ────────│  "档"
  │  ... (逐 token)        │
  │←─ answer_delta ────────│  "。"  (最后 token)
  │                         │
  │←─ citation ────────────│  [{index, chunk_id, ...}]
  │                         │
  │←─ done ────────────────│  "完成"
  │                         │
  │── {"action":"cancel"} ─→│  (可选：停止生成)
```

## 3. 数据库设计

### 3.1 ER 关系

```
users (1) ──────< knowledge_bases (N)
  │                    │
  │                    ├──< documents (N)
  │                    │      │
  │                    │      └──< chunks (N)
  │                    │
  │                    └──< chat_sessions (N)
  │                           │
  │                           ├──< chat_messages (N)
  │                           ├──< agent_runs (N)
  │                           └──< mcp_tool_calls (N)
  │
mcp_servers (1) ──< mcp_tools (N)
```

### 3.2 核心表结构

| 表名 | 关键字段 | 说明 |
|------|---------|------|
| users | id, username, email, password_hash, role(enum) | 用户账户 |
| knowledge_bases | id, name, description, owner_id(FK), visibility(enum) | 知识库 |
| documents | id, kb_id(FK), filename, file_type, file_path, status(enum:6种状态), chunk_count | 文档 |
| chunks | id, document_id(FK), kb_id(FK), content, page, section_title, chunk_index, metadata(JSON), embedding_id | 切片 |
| chat_sessions | id, user_id(FK), kb_id(FK), title | 会话 |
| chat_messages | id, session_id(FK), role(enum), content, citations(JSON) | 消息 |
| agent_runs | id, session_id(FK), user_query, final_answer, status, steps(JSON), latency_ms | Agent 日志 |
| mcp_servers | id, name(unique), transport(enum), endpoint, enabled | MCP Server |
| mcp_tools | id, server_id(FK), name, description, input_schema(JSON), permission_level(enum) | MCP 工具 |
| mcp_tool_calls | id, session_id(FK), tool_name, tool_input(JSON), tool_output(JSON), status, latency_ms | 调用日志 |

### 3.3 索引策略

- `users.username` — UNIQUE INDEX (登录查询)
- `documents.kb_id` — INDEX (按知识库查询文档)
- `chunks.kb_id` — INDEX (按知识库查询切片)
- `chunks.document_id` — INDEX (按文档查询切片)
- `chunks.embedding_id` — WHERE IS NULL (增量索引)
- `chat_sessions.user_id` — INDEX (按用户查询会话)
- `chat_messages.session_id` — INDEX (按会话查询消息)
- `mcp_tool_calls.session_id` — INDEX (按会话查询调用日志)

## 4. 安全设计

### 4.1 认证与授权

```
请求 → HTTPBearer 提取 Token
     → JWT 验证 (python-jose + HS256)
     → 解析 user_id + username
     → 查询数据库获取 User 对象
     → 注入到路由处理函数
```

### 4.2 SQL 注入防护 (5层)

```
第1层: 语句类型检查 — 仅允许 SELECT 开头
第2层: 关键字黑名单 — 正则阻断 DROP/DELETE/UPDATE/INSERT/ALTER/TRUNCATE/CREATE
第3层: 表名校验   — regex ^[a-zA-Z_][a-zA-Z0-9_]*$ 防注入
第4层: 行数限制   — 默认 100, 最大 1000, 自动追加 LIMIT
第5层: 超时控制   — asyncio.wait_for 5秒超时
```

### 4.3 文件安全

```
- 路径穿越防护: os.path.realpath 校验在 STORAGE_DIR 范围内
- 文件名清洗: os.path.basename 去除路径前缀
- 扩展名白名单: pdf/docx/md/txt/csv/xlsx
- MIME 类型校验: 仅允许声明的白名单类型
```

### 4.4 MCP 权限控制

```
权限级别: public (0) < user (1) < admin (2)
工具注册: 每个工具定义 permission_level
调用时: 用户 role level >= 工具 required level
白名单: 不在白名单的工具一律拒绝
审计: 所有调用写入 mcp_tool_calls 表
```

## 5. 服务依赖关系

```
app/main.py
  ├── app/api/*.py          (路由层)
  │     └── app/services/   (业务层)
  │           ├── auth_service.py
  │           ├── kb_service.py
  │           ├── document_service.py → file_validator, file_storage, parser_service, document_pipeline
  │           ├── rag_service.py → retriever, context_builder, llm, citation
  │           ├── indexing.py → embedding, vector_store
  │           ├── streaming_agent.py → ws_manager
  │           └── dependencies.py → embedding, vector_store (全局单例)
  │
  ├── app/agents/           (Agent 层)
  │     └── graph.py → query_analyzer, retriever, tool_planner, mcp_tool_agent, answer_generator, verifier
  │
  └── app/mcp_client/       (MCP Client 层)
        └── registry, tool_discovery, tool_caller, permissions, call_logger
```

## 6. 扩展点

| 扩展方向 | 方案 |
|---------|------|
| 向量库切换 | 实现 VectorStore ABC 的 Milvus 版本 |
| 新增 MCP Server | 创建 `app/mcp_servers/<name>/server.py`，实现 list_tools + call_tool |
| 新增文档格式 | 创建 `app/services/parsers/<name>_parser.py`，注册到 parser_service |
| 新增 Agent 节点 | 在 graph.py 中添加节点和条件边 |
| LLM 切换 | 实现 LLMService ABC，注入到 dependencies |
| 生产部署 | 替换 SQLite → PostgreSQL, Chroma 内存 → 持久化, FakeLLM → vLLM/Ollama |
