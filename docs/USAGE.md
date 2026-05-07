# MCP-Agentic RAG 后端系统 — 使用文档

## 1. 环境准备

### 1.1 系统要求

- Python 3.10+
- pip
- (可选) Docker + Docker Compose

### 1.2 安装依赖

```bash
cd mcp-agentic-rag-backend
pip install -r requirements.txt
```

### 1.3 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，关键配置项：

```ini
# 开发环境默认使用 SQLite（无需额外安装数据库）
DATABASE_URL=sqlite+aiosqlite:///storage/agentic_rag.db

# JWT 密钥（生产环境务必修改）
JWT_SECRET_KEY=change-me-to-a-random-secret-key

# 文件上传限制
MAX_UPLOAD_SIZE_MB=50

# 日志级别
LOG_LEVEL=INFO
```

## 2. 启动服务

### 2.1 初始化演示数据（可选）

```bash
python scripts/init_db.py
```

输出：
```
[OK] 10 张表创建完成
[OK] 演示数据插入完成
  users: 3 行
  knowledge_bases: 2 行
  documents: 5 行
  chunks: 28 行
  ...
```

### 2.2 启动后端

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：
- API 文档：http://localhost:8000/docs
- 联调面板：http://localhost:8000/app

### 2.3 Docker 部署

```bash
# 配置 .env (使用 PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/agentic_rag

# 启动
docker compose -f docker/docker-compose.yml up -d
```

## 3. 前端联调面板使用

访问 `http://localhost:8000/app`，按以下步骤操作：

### Step 1: 检测服务

点击「检测服务」确认后端已连接。

### Step 2: 注册账号

填写用户名、邮箱、密码，点击「注册」。成功后顶部显示 Token。

### Step 3: 创建知识库

输入知识库名称（如"测试知识库"），选择可见性（team），点击「创建知识库」。

### Step 4: 上传文档

点击「刷新列表」选择刚创建的知识库，选择文件（支持 PDF/DOCX/MD/TXT/CSV/XLSX），点击「上传文档」。

上传后系统自动完成：解析 → 清洗 → 切片 → 向量化 → 入库。

### Step 5: 问答测试

**同步问答**：在「RAG 问答」面板输入问题，点击「发送」。

**WebSocket 流式**：在「WebSocket 流式」面板输入问题，点击「开始流式问答」，观察 token 逐字流式输出。

**Agent 工作流**：输入分析类问题，点击「执行 Agent」，观察完整的 7 节点工作流输出。

**MCP 工具**：点击「列出 MCP Servers」和「列出 MCP 工具」查看可用的 MCP 工具。

### 一键初始化

点击「一键初始化」按钮自动完成注册 → 创建 KB → 上传示例文档。

## 4. API 使用指南

### 4.1 用户认证

```bash
# 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@x.com","password":"testPass123"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"testPass123"}'

# 响应: {"access_token": "eyJ...", "token_type": "bearer"}
```

### 4.2 知识库管理

```bash
TOKEN="eyJ..."

# 创建知识库
curl -X POST http://localhost:8000/api/kbs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"公司文档","description":"内部制度文档","visibility":"team"}'

# 列出知识库
curl http://localhost:8000/api/kbs \
  -H "Authorization: Bearer $TOKEN"

# 获取详情
curl http://localhost:8000/api/kbs/{kb_id} \
  -H "Authorization: Bearer $TOKEN"

# 更新
curl -X PUT http://localhost:8000/api/kbs/{kb_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"新名称"}'

# 删除
curl -X DELETE http://localhost:8000/api/kbs/{kb_id} \
  -H "Authorization: Bearer $TOKEN"
```

### 4.3 文档上传

```bash
curl -X POST http://localhost:8000/api/kbs/{kb_id}/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf"

# 列出文档
curl http://localhost:8000/api/kbs/{kb_id}/documents \
  -H "Authorization: Bearer $TOKEN"

# 获取文档详情
curl http://localhost:8000/api/documents/{doc_id} \
  -H "Authorization: Bearer $TOKEN"

# 删除文档
curl -X DELETE http://localhost:8000/api/documents/{doc_id} \
  -H "Authorization: Bearer $TOKEN"
```

### 4.4 检索与问答

```bash
# 检索
curl -X POST http://localhost:8000/api/retrieval/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"考勤制度","kb_id":"{kb_id}","top_k":5}'

# 同步问答
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"迟到怎么处罚？","kb_id":"{kb_id}"}'

# 获取会话历史
curl http://localhost:8000/api/chat/sessions/{session_id} \
  -H "Authorization: Bearer $TOKEN"
```

### 4.5 Agent 工作流

```bash
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query":"分析知识库中的安全制度",
    "kb_id":"{kb_id}",
    "enable_verifier":true
  }'

# 响应:
# {
#   "agent_run_id": "...",
#   "answer": "...",
#   "citations": [...],
#   "status": "completed",
#   "verification": {"result": "pass", ...},
#   "latency_ms": 2340
# }
```

### 4.6 WebSocket 流式问答

```javascript
// JavaScript 客户端示例
const ws = new WebSocket("ws://localhost:8000/api/chat/stream");

ws.onopen = () => {
  ws.send(JSON.stringify({
    query: "什么是 RAG？",
    kb_id: "your-kb-id"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.event: "query_analyzed" | "retrieval_started" |
  //   "retrieval_completed" | "mcp_tool_call" | "mcp_tool_result" |
  //   "answer_delta" | "citation" | "done" | "error"
  console.log(data.event, data.data);
};

// 取消生成
ws.send(JSON.stringify({action: "cancel"}));
```

### 4.7 MCP 管理

```bash
# 列出 MCP Servers
curl http://localhost:8000/api/mcp/servers \
  -H "Authorization: Bearer $TOKEN"

# 列出 MCP 工具
curl http://localhost:8000/api/mcp/tools \
  -H "Authorization: Bearer $TOKEN"

# 调用 MCP 工具
curl -X POST http://localhost:8000/api/mcp/tools/call \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"server":"knowledge-base-mcp","tool":"search_knowledge_base","arguments":{"query":"安全制度","kb_id":"{kb_id}"}}'
```

## 5. 支持的文档格式

| 格式 | 扩展名 | MIME 类型 | 解析器 |
|------|--------|-----------|--------|
| PDF | `.pdf` | `application/pdf` | PyMuPDF (fitz) |
| Word | `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | python-docx |
| Markdown | `.md` | `text/markdown` | 标题层级提取 |
| 纯文本 | `.txt` | `text/plain` | 按空行分段 |
| CSV | `.csv` | `text/csv` | csv.reader |
| Excel | `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | openpyxl |

## 6. 测试

```bash
# 运行全部测试
pytest tests/ -v

# 按阶段运行
pytest tests/test_auth_api.py tests/test_auth_service.py -v  # 认证
pytest tests/test_kb_api.py tests/test_kb_service.py -v      # 知识库
pytest tests/test_document_api.py -v                         # 文档
pytest tests/test_rag_service.py -v                          # RAG
pytest tests/test_agent_graph.py -v                          # Agent
pytest tests/test_kb_mcp_server.py -v                        # MCP Server
pytest tests/test_ws_api.py -v                               # WebSocket

# 覆盖率报告
pytest tests/ -v --cov=app --cov-report=term-missing
```

## 7. 常见问题

**Q: 上传文档后问答返回"未找到相关信息"？**
确认文档已成功上传且状态为 `ready`（查看知识库详情中的 document_count）。如果 chunks 为 0，检查文件是否为空或格式是否正确。

**Q: WebSocket 连接失败？**
确认后端已启动，且使用 `ws://` 协议（非 `http://`）。

**Q: MCP 工具调用返回 "Server not found"？**
MCP Server 需要独立启动（通过 stdio）。当前开发模式下 API 端点主要用于查看注册信息。

**Q: 如何切换到 PostgreSQL？**
修改 `.env` 中的 `DATABASE_URL` 为 PostgreSQL 连接串，重新启动服务。

**Q: 如何接入真实 LLM？**
修改 `.env` 中的 `LLM_BASE_URL` 和 `LLM_MODEL` 指向你的 LLM 服务地址（Ollama/vLLM/OpenAI-compatible API）。
