# MCP-Agentic RAG Backend

面向企业知识库问答与数据分析的 MCP-Agentic RAG 后端系统。

基于 **FastAPI + LangGraph + MCP + ChromaDB** 构建，集成了文档解析、RAG 检索增强、Agent 工作流编排、MCP 工具协议和 WebSocket 流式输出。

## 系统架构

```
用户/前端 → FastAPI (REST + WebSocket)
              ├── 认证 (JWT)
              ├── 知识库 CRUD
              ├── 文档上传/解析/切片
              ├── RAG 检索 (向量 + BM25 + Reranker)
              ├── LangGraph Agent (4 节点 + MCP 工具路由)
              ├── MCP Client (注册表/发现/调用/权限/日志)
              ├── MCP Servers (Knowledge Base + SQL Query)
              └── WebSocket 流式输出

数据层: PostgreSQL + Redis + ChromaDB + 本地文件存储
```

## 快速开始

### 环境要求

- Python 3.10+
- (可选) Docker Compose

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入实际配置

# 初始化数据库（演示数据）
python scripts/init_db.py

# 启动服务
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

### Docker 部署

```bash
cp .env.example .env
# 编辑 .env 配置数据库连接

docker compose -f docker/docker-compose.yml up -d
```

## 项目结构

```
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── api/                 # REST + WebSocket 路由
│   │   ├── auth.py          # 认证 (register/login/me)
│   │   ├── knowledge_base.py # 知识库 CRUD
│   │   ├── document.py      # 文档上传/解析
│   │   ├── retrieval.py     # 检索接口
│   │   ├── chat.py          # 同步问答 + 会话
│   │   ├── agent.py         # Agent 工作流
│   │   ├── mcp.py           # MCP 管理
│   │   └── ws.py            # WebSocket 流式输出
│   ├── agents/              # LangGraph Agent 节点
│   │   ├── state.py         # 状态定义
│   │   ├── graph.py         # 工作流组装
│   │   ├── query_analyzer.py
│   │   ├── retriever.py
│   │   ├── tool_planner.py
│   │   ├── mcp_tool_agent.py
│   │   ├── answer_generator.py
│   │   └── verifier.py
│   ├── mcp_client/          # MCP Client
│   │   ├── registry.py      # Server 注册表
│   │   ├── tool_discovery.py
│   │   ├── tool_caller.py
│   │   ├── permissions.py   # 权限控制
│   │   └── call_logger.py
│   ├── mcp_servers/         # MCP Server 实现
│   │   ├── knowledge_base/  # KB MCP Server (3 tools)
│   │   └── sql_query/       # SQL MCP Server (3 tools)
│   ├── services/            # 业务服务
│   │   ├── rag_service.py   # RAG 问答流程
│   │   ├── chunker.py       # 结构化切片
│   │   ├── indexing.py      # 向量化入库
│   │   ├── context_builder.py
│   │   ├── citation.py      # 引用溯源
│   │   ├── embedding/       # Embedding (Fake + BGE-M3)
│   │   ├── vector_store/    # 向量库 (Chroma)
│   │   ├── reranker/        # Reranker (Fake + BGE)
│   │   ├── retrieval/       # 检索 (向量 + BM25 + 混合)
│   │   ├── llm/             # LLM (Fake + OpenAI)
│   │   ├── parsers/         # 文档解析 (PDF/DOCX/MD/TXT/CSV/XLSX)
│   │   └── ws_manager.py    # WebSocket 连接管理
│   ├── models/              # 数据库模型 (10 表)
│   ├── schemas/             # Pydantic Schema
│   ├── core/                # 配置/日志/安全/异常
│   └── db/                  # 数据库会话
├── tests/                   # 测试 (289 个)
├── docs/                    # 项目文档
├── docker/                  # Docker 部署
├── scripts/                 # 工具脚本
└── storage/                 # 本地文件存储
```

## 核心 API

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/register` | 用户注册 |
| `POST` | `/api/auth/login` | 用户登录 |
| `GET` | `/api/auth/me` | 当前用户信息 |
| `POST` | `/api/kbs` | 创建知识库 |
| `GET` | `/api/kbs` | 知识库列表 |
| `POST` | `/api/kbs/{id}/documents/upload` | 上传文档 |
| `POST` | `/api/retrieval/search` | 检索 |
| `POST` | `/api/chat` | RAG 问答 |
| `WS` | `/api/chat/stream` | 流式问答 |
| `POST` | `/api/agent/chat` | Agent 工作流 |
| `GET` | `/api/mcp/servers` | MCP Server 列表 |
| `GET` | `/api/mcp/tools` | MCP 工具列表 |
| `POST` | `/api/mcp/tools/call` | 调用 MCP 工具 |
| `GET` | `/api/health` | 健康检查 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Pydantic + SQLAlchemy 2.0 async |
| 数据库 | PostgreSQL + Redis + ChromaDB |
| Agent | LangGraph StateGraph + 条件路由 |
| MCP | MCP Python SDK (Client + Server) |
| 检索 | 向量检索 + BM25 + RRF 融合 + Reranker |
| LLM | OpenAI-compatible API (vLLM / Ollama / LiteLLM) |
| 流式 | WebSocket + SSE token 级推送 |
| 部署 | Docker Compose |

## 测试

```bash
# 运行全部测试
pytest tests/ -v

# 覆盖率报告
pytest tests/ -v --cov=app --cov-report=term-missing
```

## MCP、RAG、LangGraph 三者关系

- **RAG** 负责知识检索：文档解析 → 切片 → 向量化 → 混合检索 → 上下文构造
- **LangGraph** 负责 Agent 状态编排：问题分析 → 工具规划 → 检索/工具执行 → 答案生成 → 校验
- **MCP** 负责标准化暴露外部工具：将知识库检索、SQL 查询等封装为独立 MCP Server，Agent 通过 MCP Client 统一调用
