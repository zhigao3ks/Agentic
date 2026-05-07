# CLAUDE.md

## 项目定位

本项目是“面向企业知识库问答与数据分析的 MCP-Agentic RAG 后端系统”。

目标是基于 FastAPI 构建一个可运行、可测试、可部署的大模型应用后端，核心能力包括文档解析、RAG 检索问答、LangGraph Agent 编排、MCP 工具接入、WebSocket 流式输出、数据库持久化和 Docker 部署。

详细需求以 `docs/SPEC.md` 为准，简历与面试表达以 `docs/RESUME_GUIDE.md` 为准，任务拆解以 `docs/TASKS.md` 为准。

## 回复语言

默认使用简体中文回复。

以下内容可以保留源语言：代码、命令、配置、API 路径、数据库字段、报错信息、第三方库名称、协议名称、模型名称和 Git commit message。

## 回复方式

执行开发任务时，按以下结构回复：

1. 任务理解：说明本次要做什么。
2. 修改计划：列出计划创建或修改的文件。
3. 实现说明：说明核心实现逻辑。
4. 测试结果：说明运行了哪些测试或命令；失败时保留原始报错，并用中文解释原因。
5. 变更总结：总结完成内容、影响范围和下一步建议。

纯问答、调研、代码审查、debug 分析和 Git 操作不强制使用五段式结构。

## 开发原则

1. 不要一次性生成整个项目。
2. 每次只完成一个可测试的小任务。
3. 每个新模块完成并测试通过后，再进入下一个模块。
4. API 层只负责请求接收、参数校验和响应返回。
5. 业务逻辑必须放在 service、agent、rag 或 mcp 相关模块中。
6. 不要把复杂逻辑直接写在 FastAPI route 函数中。
7. 不要把所有代码堆进 `main.py`。
8. 修改已有代码前先说明影响范围。
9. 不要无说明大规模重构。
10. 不要删除用户已有代码，除非说明原因并获得确认。

## 推荐分层

项目优先采用以下分层：

- `app/api/`：FastAPI 路由。
- `app/schemas/`：Pydantic 请求和响应结构。
- `app/models/`：数据库模型。
- `app/services/`：业务逻辑。
- `app/agents/`：LangGraph Agent 节点和工作流。
- `app/mcp_client/`：MCP Client、工具注册和工具调用。
- `app/mcp_servers/`：自定义 MCP Server。
- `app/core/`：配置、日志、安全和异常处理。
- `app/db/`：数据库连接和会话管理。
- `tests/`：测试代码。
- `docs/`：项目文档。

新增目录或明显偏离该结构时，先说明原因。

## 编码规范

1. 使用 Python type hints。
2. 使用 Pydantic 定义请求和响应结构。
3. 核心逻辑通过 service 或 agent 封装，便于测试和复用。
4. 单个 Python 文件建议不超过 300 行；超过时应考虑拆分。
5. 不写无意义 placeholder；允许在明确标注 TODO 的接口桩中使用 `raise NotImplementedError`。
6. 外部模型、Embedding、Reranker 和 MCP 调用必须可替换为 fake 或 mock 实现。
7. 测试中不要调用真实大模型 API、付费服务或不稳定外部服务。
8. 不要硬编码密钥、数据库密码、Token 或绝对路径。
9. 不要为了演示效果伪造评测结果。

## 安全底线


1. 防止路径穿越，例如 `../` 访问。
2. SQL 工具默认只允许只读查询。
3. 禁止执行 `DROP`、`DELETE`、`UPDATE`、`INSERT`、`ALTER`、`TRUNCATE` 等危险 SQL。
4. SQL 查询必须参数化，禁止直接拼接未校验的用户输入。
5. MCP 工具调用必须有工具白名单、参数校验、超时控制和日志记录。
6. Agent 不允许执行任意 shell 命令。

## RAG、Agent 与 MCP 分工

1. RAG 负责文档解析、chunk 切片、向量检索、BM25、Reranker、上下文构造和引用溯源。
2. LangGraph 负责 Agent 状态流转和任务编排。
3. MCP 负责将外部能力标准化暴露给 Agent，例如知识库检索、SQL 查询、文件读取、图表生成和评测工具。
4. MCP 不替代 RAG，也不替代 LangGraph。

具体工具列表、接口参数和实现细节不要写在 `CLAUDE.md` 中，应写入 `docs/SPEC.md` 或 `docs/TASKS.md`。

## 测试要求

1. 每完成一个核心模块，必须补充 pytest 测试。
2. 测试失败时先解释原因，再修复。
3. 不允许删除测试来规避失败。
4. 外部模型、向量库、Reranker 和 MCP Server 在测试中优先使用 fake/mock。
5. 每次开发任务结束前，应说明运行了哪些测试；如果没有运行测试，必须说明原因。

## Git 规范

独立任务完成后建议提交一次 Git commit。

Commit message 统一使用英文，建议格式：

- `feat: add health check endpoint`
- `feat: implement document chunking service`
- `feat: add basic rag pipeline`
- `feat: integrate langgraph workflow`
- `feat: add mcp client registry`
- `test: add retrieval service tests`
- `fix: handle empty retrieval results`
- `docs: update project tasks`

提交前说明修改文件、测试结果、未完成 TODO 和下一步建议。

## 开发顺序

优先按以下顺序推进：

1. 项目初始化。
2. FastAPI 基础骨架、配置、日志、健康检查。
3. 数据库连接和基础模型。
4. 知识库与文档管理。
5. 文档解析和 chunk 切片。
6. Embedding 与向量库抽象。
7. 基础 RAG 问答和引用溯源。
8. BM25、Reranker 和检索优化。
9. LangGraph Agent 工作流。
10. MCP Client。
11. Knowledge Base MCP Server。
12. SQL Query MCP Server。
13. MCP Tool Agent 接入 LangGraph。
14. WebSocket 流式输出。
15. Docker Compose、README 和面试文档。

如果用户要求跳过顺序，先说明风险，再按用户指定任务执行。

