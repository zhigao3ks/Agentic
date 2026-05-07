# 面试展示文档

## 项目一句话定位

基于 FastAPI + LangGraph + MCP 的企业知识库 Agentic RAG 后端系统，集成文档解析、混合检索、Agent 工作流、MCP 工具协议和 WebSocket 流式输出。

## 核心架构

```
FastAPI 后端
  ├── RAG 层：文档解析 → 切片 → Embedding → 向量库 → 混合检索 → Reranker
  ├── Agent 层：Query Analyzer → Tool Planner → Retriever/MCP Tool Agent → Answer Generator → Verifier
  ├── MCP 层：Knowledge Base MCP Server (3 tools) + SQL Query MCP Server (3 tools)
  └── 流式输出：WebSocket 事件推送 (9 种事件类型)
```

## 技术选型与理由

| 选择 | 理由 |
|------|------|
| FastAPI | 原生 async、自动 OpenAPI、WebSocket 支持、Pydantic 校验 |
| LangGraph | 状态化 Agent 编排、条件路由、步数限制、可观测 |
| MCP | 工具标准化接入、工具发现/参数 schema/权限控制、解耦 Agent 与工具 |
| ChromaDB | 轻量向量库、按 kb_id 分 collection、嵌入式部署 |
| BM25 + RRF | 补充关键词召回、多路融合、提升专有名词/编号类问题召回 |
| SQLAlchemy 2.0 async | 类型安全、与 FastAPI async 一致、支持 SQLite(测试) 和 PostgreSQL(生产) |

## MCP、RAG、LangGraph 三者关系

- RAG：知识层 — 提供私有文档检索能力
- LangGraph：流程层 — 状态化多步骤任务编排
- MCP：工具协议层 — 标准化暴露外部能力给 Agent

三者不互相替代，分层协作。

## 个人贡献总结

1. 设计并实现完整的 RAG 检索链路：文档上传 → 6 种格式解析 → 结构化切片 → Embedding 向量化 → 向量库 → BM25+向量混合检索 → RRF 融合 → Reranker 精排 → 引用溯源
2. 基于 LangGraph 构建 7 节点 Agent 工作流，支持条件路由（是否需要工具调用），步数限制，校验回退
3. 接入 MCP 协议，实现 MCP Client（注册/发现/调用/权限/日志）和 2 个 MCP Server（Knowledge Base + SQL Query），含 SQL 安全校验（5 层防护）
4. 基于 FastAPI 构建 15 个 REST 端点 + WebSocket 流式输出，PostgreSQL 管理 10 张业务表
5. 使用 SQLAlchemy 2.0 async、Pydantic v2、ChromaDB、pytest（289 测试全部通过）
6. Docker Compose 一键部署

## 高频问答

**Q: chunk 怎么切？**
优先保留标题、章节、段落和表格边界。默认 chunk_size 800 字符，overlap 120 字符。保存 page、section_title 等元数据。

**Q: Reranker 放在什么位置？**
向量检索 TopK=20 + BM25 TopK=20 → RRF 融合 → Reranker 精排 → 最终 TopK=5~8 送入 LLM。

**Q: 如何减少幻觉？**
四方面：检索阶段提高证据质量；prompt 要求答案基于证据；Verifier Agent 校验引用支持；证据不足时明确返回"不确定"。

**Q: MCP 调用有什么安全风险？**
工具白名单 + Pydantic 参数校验 + SQL 只允许 SELECT + 限制返回行数 + 文件访问目录限制 + 超时控制 + 工具调用日志。

**Q: WebSocket 流式输出怎么实现？**
后端建立 WS 长连接，用户发送 query 后依次推送 9 种事件：query_analyzed → retrieval_started → mcp_tool_call → answer_delta → citation → done。LLM streaming token 以 answer_delta 逐字推送。

**Q: 这个项目最难的地方？**
1. 文档解析和 chunk 切片要保留语义结构
2. Agent 条件路由的节点编排和状态管理
3. MCP 工具的安全性（SQL 注入、文件穿越、权限越权）
4. 测试覆盖（289 个测试，Fake/Mock 全部外部依赖）

## 项目数据

- 测试：289 passed
- API 端点：15 个 REST + 1 个 WebSocket
- 数据库表：10 张
- MCP Server：2 个（6 个工具）
- Agent 节点：7 个
- 文档解析格式：6 种（PDF/DOCX/MD/TXT/CSV/XLSX）
- 代码行数：~8000+
