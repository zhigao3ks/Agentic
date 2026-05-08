# MCP-Agentic RAG 后端系统 — 测试文档

## 0. 前置准备：配置 Qwen API

### 0.1 获取 API Key

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 进入「模型广场」→ 选择需要的 Qwen 模型（推荐 `qwen-plus` 或 `qwen-max`）
4. 右上角点击「API-KEY 管理」→ 创建新的 API Key
5. 复制保存 API Key（形如 `sk-xxxxxxxxxxxxxxxxxxxxxxxx`）

### 0.2 配置 .env 文件

编辑项目根目录下的 `.env` 文件（已创建），将 LLM、Embedding、Reranker 都指向 Qwen/DashScope API：

```ini
# ============================================================
# Qwen / DashScope API 配置（OpenAI 兼容模式）
# ============================================================

# --- LLM 大模型 ---
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=sk-your-dashscope-api-key-here
LLM_MODEL=qwen-plus
# 备选模型: qwen-turbo(更快) / qwen-max(更强) / qwen-long(长文本)

# --- Embedding 向量模型 ---
EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
EMBEDDING_API_KEY=sk-your-dashscope-api-key-here
EMBEDDING_MODEL=text-embedding-v4
# DashScope 的 Embedding 模型: text-embedding-v4 (1024维)

# --- Reranker（可选，暂用 fake）---
# DashScope 目前没有标准 Reranker API，开发环境使用 FakeReranker
# 如需真实 Reranker，可后续部署本地 BGE-Reranker 模型
RERANKER_BASE_URL=http://localhost:8001/v1
RERANKER_API_KEY=not-needed
RERANKER_MODEL=bge-reranker-base

# --- 数据库（本地 SQLite）---
DATABASE_URL=sqlite+aiosqlite:///storage/agentic_rag.db

# --- 向量数据库 ---
CHROMA_PERSIST_DIR=./storage/chroma

# --- JWT ---
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 0.3 启动服务

```bash
# 清理旧数据库
rm -f storage/agentic_rag.db

# 启动服务（带 --reload 热更新）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：
- **API 文档 (Swagger)**：http://localhost:8000/docs
- **前端联调面板**：http://localhost:8000/app

### 0.4 验证 API 连接

```bash
# 测试 DashScope 连接
curl -X POST https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions \
  -H "Authorization: Bearer sk-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"你好"}]}'

# 预期返回:
# {"choices":[{"message":{"content":"你好！有什么我可以帮助你的吗？"}}],...}
```

---

## 1. 基础功能测试

### 1.1 健康检查

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | `curl http://localhost:8000/api/health` | `{"status":"ok","version":"0.1.0"}` |
| 2 | 浏览器打开 `http://localhost:8000/docs` | 显示 Swagger API 文档页面 |
| 3 | 浏览器打开 `http://localhost:8000/app` | 显示前端联调面板，左下角显示「运行中」 |

### 1.2 用户注册

**curl 方式：**
```bash
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testPass123"
  }' | python3 -m json.tool
```

**预期响应：**
```json
{
  "user": {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "username": "testuser",
    "email": "test@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2026-05-08T..."
  },
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**前端方式：**
1. 打开 `http://localhost:8000/app`
2. 点击右上角「🔐 认证」按钮
3. 选择「注册」tab
4. 填写：用户名 `testuser`、邮箱 `test@example.com`、密码 `testPass123`
5. 点击「注册」
6. 右上角出现绿色 toast「注册成功！」

### 1.3 用户登录

**curl 方式：**
```bash
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testPass123"}' | python3 -m json.tool
```

**前端方式：**
1. 退出后重新打开，或点击「🔐 认证」
2. 选择「登录」tab
3. 输入用户名 `testuser`、密码 `testPass123`
4. 点击「登录」
5. 顶部 Token 栏显示 Token 前缀

### 1.4 获取当前用户信息

```bash
TOKEN="sk-faebd51670e446f3ac6375e496764515"

curl -s http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## 2. 知识库管理测试

### 2.1 创建知识库

```bash
TOKEN="your-jwt-token-here"

# 创建知识库
curl -s -X POST http://localhost:8000/api/kbs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试知识库",
    "description": "用于功能测试的知识库",
    "visibility": "team"
  }' | python3 -m json.tool

# 记录返回的 kb_id，后续步骤需要
```

### 2.2 列出知识库

```bash
curl -s http://localhost:8000/api/kbs \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**前端方式：** 左侧导航 →「📚 知识库管理」→ 下拉框点击刷新即可看到刚创建的知识库。

### 2.3 更新知识库

```bash
KB_ID="your-kb-id"

curl -s -X PUT http://localhost:8000/api/kbs/$KB_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"更新后的知识库名称"}' | python3 -m json.tool
```

---

## 3. 文档上传与解析测试

### 3.1 准备测试文档

```bash
# 创建测试用 Markdown 文件
cat > /tmp/test_python.md << 'EOF'
# Python 编程语言简介

## 概述
Python 是一种解释型、面向对象的高级编程语言，由 Guido van Rossum 于 1991 年首次发布。
Python 以其简洁的语法、强大的标准库和丰富的第三方生态而闻名。

## 主要特点
- 简洁易读的语法，使用缩进表示代码块
- 动态类型系统，支持自动内存管理
- 丰富的标准库，涵盖网络、文件、数据库等领域
- 跨平台支持，可在 Windows、Linux、macOS 上运行

## 应用领域
Python 广泛应用于以下领域：
1. 数据科学与机器学习（NumPy、Pandas、TensorFlow、PyTorch）
2. Web 开发（Django、FastAPI、Flask）
3. 自动化运维与测试
4. 科学计算与学术研究

## FastAPI 框架
FastAPI 是一个现代、快速的 Web 框架，基于 Python 3.6+ 的类型提示。
主要特性包括：
- 自动生成 OpenAPI 文档
- 异步支持（async/await）
- 内置请求参数校验
- 高性能，与 Node.js 和 Go 相当
EOF

# 创建测试用 TXT 文件
cat > /tmp/test_safety.txt << 'EOF'
信息安全管理制度

一、总则
为保障公司信息系统安全，保护公司核心数据和客户隐私，特制定本制度。

二、密码管理策略
1. 所有系统密码长度不少于 12 位
2. 必须包含大小写字母、数字和特殊字符
3. 每 90 天更换一次密码
4. 禁止使用生日、手机号等弱密码
5. 禁止在多个系统间共享密码

三、数据分级标准
公开数据：可对外发布的信息
内部数据：仅供公司内部使用的信息
机密数据：仅限相关部门访问的信息
绝密数据：仅限核心管理层访问的信息

四、安全事件响应流程
1. 发现安全事件后 1 小时内上报信息安全部门
2. 4 小时内启动应急响应
3. 24 小时内完成初步调查报告
4. 72 小时内完成全面整改

五、违规处罚
违反信息安全制度者，视情节严重程度给予警告、罚款、降职或辞退处分。
造成重大损失的，将追究法律责任。
EOF
```

### 3.2 上传文档

```bash
TOKEN="your-jwt-token-here"
KB_ID="your-kb-id"

# 上传 Markdown 文件
curl -s -X POST http://localhost:8000/api/kbs/$KB_ID/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_python.md" | python3 -m json.tool

# 上传 TXT 文件
curl -s -X POST http://localhost:8000/api/kbs/$KB_ID/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test_safety.txt" | python3 -m json.tool
```

**预期响应：**
```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "kb_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "filename": "test_python.md",
  "file_type": "md",
  "file_size": 1234,
  "status": "ready"
}
```

> 上传后系统自动完成：解析 → 清洗 → 切片 → 向量化。status 为 `ready` 表示已入库。

### 3.3 查看文档列表

```bash
curl -s http://localhost:8000/api/kbs/$KB_ID/documents \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**前端方式：** 知识库管理页面 → 选择知识库 → 自动显示文档列表（含状态标签、chunk 计数）。

---

## 4. RAG 检索与问答测试

### 4.1 向量检索

```bash
TOKEN="your-jwt-token-here"
KB_ID="your-kb-id"

curl -s -X POST http://localhost:8000/api/retrieval/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python 有哪些应用领域",
    "kb_id": "'$KB_ID'",
    "top_k": 5
  }' | python3 -m json.tool
```

**预期结果：** 返回 5 条相关 chunk，每条包含 `content`、`score`、`metadata`（页码、章节等）。

### 4.2 同步 RAG 问答

```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python 有哪些主要特点和应用领域？请引用相关来源。",
    "kb_id": "'$KB_ID'"
  }' | python3 -m json.tool
```

**预期响应：**
```json
{
  "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "answer": "Python 的主要特点包括：简洁易读的语法[1]、动态类型系统[1]...",
  "citations": [
    {
      "index": 1,
      "chunk_id": "...",
      "document_id": "...",
      "score": 0.85,
      "content_preview": "Python 是一种解释型、面向对象的高级编程语言...",
      "page": null,
      "section_title": "概述"
    }
  ]
}
```

### 4.3 跨文档知识问答

```bash
# 同时上传多个文档后，测试跨文档检索
curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "公司信息安全制度中关于密码管理和违规处罚的规定是什么？",
    "kb_id": "'$KB_ID'"
  }' | python3 -m json.tool
```

**前端方式：** 左侧导航 →「💬 智能问答」→ 选择知识库 → 输入问题 → 点击「发送」（或按 Enter）。

### 4.4 WebSocket 流式问答

**前端方式（推荐）：**
1. 导航到「💬 智能问答」
2. 选择知识库
3. 点击「📡 流式输出」按钮启用流式模式
4. 输入问题 → 点击「发送」
5. 右侧面板实时显示：
   - 事件流（query_analyzed → retrieval_started → ... → done）
   - 回答 token 逐字流式输出

**JavaScript 客户端测试：**
```javascript
const ws = new WebSocket("ws://localhost:8000/api/chat/stream");
ws.onopen = () => ws.send(JSON.stringify({query:"什么是 FastAPI？", kb_id:"your-kb-id"}));
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## 5. Agent 工作流测试

### 5.1 基础 Agent 问答

```bash
TOKEN="your-jwt-token-here"
KB_ID="your-kb-id"

curl -s -X POST http://localhost:8000/api/agent/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "请详细分析知识库中关于 Python 的信息，并总结其关键特点",
    "kb_id": "'$KB_ID'",
    "enable_verifier": true
  }' | python3 -m json.tool
```

**预期响应：**
```json
{
  "agent_run_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "query": "请详细分析知识库中关于 Python 的信息...",
  "answer": "根据知识库内容，Python 具有以下关键特点...",
  "citations": [...],
  "status": "completed",
  "verification": {
    "result": "pass",
    "issues": []
  },
  "latency_ms": 2340
}
```

### 5.2 Agent 工作流节点验证

Agent 工作流依次经过以下节点（可通过 `verification` 字段和 `latency_ms` 确认执行完整）：

| 节点 | 职责 | 验证方式 |
|------|------|----------|
| Query Analyzer | 分析问题类型，判断是否需要检索 | 看返回的 answer 是否与知识库内容相关 |
| Retriever | 执行混合检索 | citations 中有引用来源 |
| Answer Generator | 基于证据生成回答 | answer 包含具体内容，非模板回复 |
| Verifier | 校验回答与证据一致性 | verification.result = "pass" |

**前端方式：** 左侧导航 →「🤖 Agent 工作流」→ 选择知识库 → 输入分析问题 → 点击「执行 Agent」→ 查看执行结果和步骤。

### 5.3 禁用 Verifier 测试

```bash
curl -s -X POST http://localhost:8000/api/agent/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python 是什么？",
    "kb_id": "'$KB_ID'",
    "enable_verifier": false
  }' | python3 -m json.tool
```

对比启用/禁用 Verifier 的响应时间差异（禁用更快）。

---

## 6. MCP 工具测试

### 6.1 查看 MCP Servers

```bash
TOKEN="your-jwt-token-here"

curl -s http://localhost:8000/api/mcp/servers \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### 6.2 查看 MCP 工具列表

```bash
curl -s http://localhost:8000/api/mcp/tools \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**前端方式：** 左侧导航 →「🔧 MCP 工具」→ 切换「Servers」/「工具列表」tab 查看。

### 6.3 MCP 工具调用 — 知识库检索

```bash
KB_ID="your-kb-id"
# 使用非 UUID 格式的 KB ID? 先把 KB ID 记下来

curl -s -X POST http://localhost:8000/api/mcp/tools/call \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server": "knowledge-base-mcp",
    "tool": "search_knowledge_base",
    "arguments": {
      "query": "信息安全",
      "kb_id": "'$KB_ID'",
      "top_k": 3
    }
  }' | python3 -m json.tool
```

**前端方式：** MCP 工具页 → 「调用工具」tab → 填写 Server 和工具名 → 点击「执行调用」→ 查看结果。

### 6.4 MCP 工具调用 — SQL 查询

```bash
curl -s -X POST http://localhost:8000/api/mcp/tools/call \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server": "sql-query-mcp",
    "tool": "list_tables",
    "arguments": {}
  }' | python3 -m json.tool
```

### 6.5 SQL 安全测试（验证危险操作被拦截）

```bash
# 测试 DROP 被拦截
curl -s -X POST http://localhost:8000/api/mcp/tools/call \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server": "sql-query-mcp",
    "tool": "execute_readonly_sql",
    "arguments": {"sql_query": "DROP TABLE users"}
  }' | python3 -m json.tool
# 预期: {"error": "Only SELECT queries are allowed"}

# 测试合法 SELECT
curl -s -X POST http://localhost:8000/api/mcp/tools/call \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server": "sql-query-mcp",
    "tool": "execute_readonly_sql",
    "arguments": {"sql_query": "SELECT username, role FROM users"}
  }' | python3 -m json.tool
# 预期: 返回用户列表
```

---

## 7. 引用溯源测试

### 7.1 验证引用准确性

```bash
# 问一个知识库中明确有答案的问题
curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "公司密码管理策略的具体要求是什么？列出所有条款。",
    "kb_id": "'$KB_ID'"
  }' | python3 -m json.tool
```

**验证要点：**
- `citations` 数组不为空
- 每个 citation 包含 `document_id`、`content_preview`
- `content_preview` 与实际知识库文档内容匹配
- 回答中的引用编号 `[1]` `[2]` 与 citations 对应

---

## 8. 会话管理测试

### 8.1 创建多轮对话

```bash
TOKEN="your-jwt-token-here"
KB_ID="your-kb-id"

# 第一轮
S1=$(curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"Python 是什么？","kb_id":"'$KB_ID'"}')
echo $S1 | python3 -m json.tool
SESSION_ID=$(echo $S1 | python3 -c "import sys,json; print(json.load(sys.stdin)['session_id'])")

# 获取会话历史
curl -s http://localhost:8000/api/chat/sessions/$SESSION_ID \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 预期: messages 数组包含 user 和 assistant 两条消息
```

---

## 9. 权限控制测试

### 9.1 知识库访问隔离

```bash
# 用户 A 创建私有知识库
USER_A_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"usera","email":"usera@test.com","password":"testPass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

KB_A=$(curl -s -X POST http://localhost:8000/api/kbs \
  -H "Authorization: Bearer $USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"用户A私有库","visibility":"private"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 用户 B 注册
USER_B_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"userb","email":"userb@test.com","password":"testPass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 用户 B 尝试访问用户 A 的私有知识库 → 应被拒绝
curl -s http://localhost:8000/api/kbs/$KB_A \
  -H "Authorization: Bearer $USER_B_TOKEN"
# 预期: 403 Forbidden

# 用户 B 的 KB 列表不包含用户 A 的私有 KB
curl -s http://localhost:8000/api/kbs \
  -H "Authorization: Bearer $USER_B_TOKEN"
# 预期: 返回空列表（或不包含"用户A私有库"）
```

### 9.2 MCP 工具权限

```bash
# 普通用户调用 admin 级别工具（execute_readonly_sql）→ 应被拒绝
# 先用普通用户 token
curl -s -X POST http://localhost:8000/api/mcp/tools/call \
  -H "Authorization: Bearer $USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server": "sql-query-mcp",
    "tool": "execute_readonly_sql",
    "arguments": {"sql_query": "SELECT 1"}
  }'
# 预期: 403 Forbidden
```

---

## 10. 异常场景测试

### 10.1 空知识库问答

```bash
# 创建一个空知识库（不上传文档）
EMPTY_KB=$(curl -s -X POST http://localhost:8000/api/kbs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"空知识库","visibility":"team"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 对空知识库提问
curl -s -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"有什么内容？","kb_id":"'$EMPTY_KB'"}'
# 预期: answer 包含 "没有找到相关信息"
```

### 10.2 文件上传校验

```bash
# 上传不支持的文件类型 → 422
echo "fake exe" > /tmp/test.exe
curl -s -X POST http://localhost:8000/api/kbs/$KB_ID/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/tmp/test.exe"
# 预期: 422 Validation Error

# 路径穿越攻击 → 422
# （curl 无法发送带 ../ 的文件名，但后端已有防护）
```

### 10.3 未登录访问保护接口

```bash
# 无 Token 访问知识库列表 → 401/403
curl -s http://localhost:8000/api/kbs

# 无 Token 访问问答 → 401/403
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"test","kb_id":"dummy"}'
```

---

## 11. 前端联调面板测试清单

按顺序操作，每步验证结果：

| # | 操作 | 验证点 |
|---|------|--------|
| 1 | 打开 `http://localhost:8000/app` | 左下角显示绿色「运行中」 |
| 2 | 点击「🔐 认证」→「注册」 | 弹窗显示注册表单 |
| 3 | 填写信息 → 点击「注册」 | 右上角绿色 toast「注册成功」 |
| 4 | 导航到「📚 知识库管理」 | 下拉框通过「刷新列表」能看到知识库 |
| 5 | 点击「+ 新建知识库」 | 弹窗创建知识库 |
| 6 | 选择知识库 → 选择文件 →「上传文档」| 弹窗提示上传成功 |
| 7 | 导航到「💬 智能问答」| 选择知识库后能看到它 |
| 8 | 输入问题 → 点击「发送」 | 聊天区显示用户问题和 AI 回答（含引用） |
| 9 | 点击「📡 流式输出」→ 再发送问题 | 右侧面板实时显示事件流和逐字回答 |
| 10 | 导航到「🤖 Agent 工作流」| 选择 KB → 输入问题 → 执行 |
| 11 | 查看结果 | 显示 answer + verification + latency_ms |
| 12 | 导航到「🔧 MCP 工具」| 查看 Server 列表、工具卡片 |
| 13 | 切换到「调用工具」tab | 填写参数 → 执行 → 查看结果 |
| 14 | 导航到「📊 仪表盘」| 统计卡片更新为最新数据 |

---

## 12. 性能基准测试

```bash
# 使用 pytest-benchmark 或简单计时
TOKEN="your-jwt-token-here"
KB_ID="your-kb-id"

echo "=== RAG 问答耗时测试 ==="
for i in 1 2 3; do
  time curl -s -X POST http://localhost:8000/api/chat \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"query":"Python 的特点","kb_id":"'$KB_ID'"}' > /dev/null
done

echo "=== Agent 工作流耗时测试 ==="
for i in 1 2 3; do
  time curl -s -X POST http://localhost:8000/api/agent/chat \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"query":"分析 Python","kb_id":"'$KB_ID'","enable_verifier":false}' > /dev/null
done
```

**参考指标：**
| 操作 | 预期耗时 |
|------|---------|
| 文档上传（含解析+切片+向量化） | 1-5 秒 |
| RAG 问答（qwen-plus） | 2-6 秒 |
| Agent 工作流（含 verifier） | 5-15 秒 |
| Agent 工作流（不含 verifier） | 3-8 秒 |

---

## 13. 全部测试通过标准

- [ ] 健康检查返回 OK
- [ ] 注册/登录正常
- [ ] 知识库 CRUD 正常
- [ ] 文档上传、解析、切片、向量化全链路正常
- [ ] RAG 问答返回带引用的回答
- [ ] WebSocket 流式推送全部事件类型
- [ ] Agent 工作流 7 节点全部执行
- [ ] MCP Server 列表/工具列表正常
- [ ] SQL 危险操作被拦截
- [ ] 权限隔离正确
- [ ] 空知识库优雅降级
- [ ] 前端面板各项功能正常
- [ ] 289 个 pytest 全部通过
