# 简历项目经历

## 项目名称

**面向企业知识库的 MCP-Agentic RAG 智能问答后端系统**

## 项目时间

2026.05（个人项目）

## 技术栈

`FastAPI` `LangGraph` `MCP` `SQLAlchemy 2.0` `ChromaDB` `BM25` `Pydantic` `WebSocket` `PostgreSQL` `Redis` `Docker` `Pytest` `Qwen`

## 项目描述

独立设计并实现了一个集成 RAG 检索增强、LangGraph Agent 工作流编排和 MCP 工具协议的企业知识库智能问答后端系统。系统支持 PDF/Word/Markdown/TXT/CSV/Excel 共 6 种格式文档的自动解析、结构化切片、向量化入库，并基于 BM25 + 向量检索 + RRF 融合 + Reranker 的多阶段混合检索策略提供带引用溯源的 RAG 问答。引入 LangGraph 构建 7 节点 Agent 工作流（含条件路由），通过 MCP 协议将知识库检索和 SQL 查询封装为标准化工具服务，支持 WebSocket 流式输出和多轮对话记忆。项目包含 289 个 Pytest 测试用例，覆盖所有核心模块。

## 个人贡献

**1. RAG 检索链路设计与实现**
- 设计并实现了完整的文档处理流水线：文件上传校验（扩展名/MIME/路径穿越防护）→ 6 种格式解析（PyMuPDF/pdfplumber/python-docx/openpyxl）→ 文本清洗 → 结构化切片（按段落/句子边界，chunk_size=800，overlap=120，保留表格完整性）→ bge-m3 Embedding 向量化 → ChromaDB 向量入库
- 实现 BM25 关键词检索 + 向量语义检索 + RRF 融合 + Reranker 精排的四阶段混合检索策略，针对专有名词和语义问题分别优化召回
- 实现引用溯源：从 LLM 回答中正则提取 `[N]` 标记，关联回 chunk 元数据（document_id、page、section_title、score、content_preview）

**2. LangGraph Agent 工作流编排**
- 基于 LangGraph StateGraph 设计 7 节点 Agent 工作流：Query Analyzer → Tool Planner → MCP Tool Agent → Retriever → Answer Generator → Verifier
- 实现条件路由：Query Analyzer 根据问题意图（LLM 输出 JSON）动态决定走工具调用路径还是检索路径，步数限制 10 步防止失控
- 各节点通过 TypedDict 状态共享数据，messages 字段使用 `operator.add` 累加实现全链路可观测

**3. MCP 工具协议接入**
- 基于 MCP Python SDK 实现 MCP Client 层：Server 注册表、工具发现（list_tools + inputSchema 获取）、工具调用（参数校验 + 超时控制 + asyncio 异步包装）、三级权限控制（public/user/admin）
- 开发 2 个 MCP Server：Knowledge Base MCP Server（search_knowledge_base/get_document_detail/get_chunk_context）和 SQL Query MCP Server（list_tables/describe_table/execute_readonly_sql）
- SQL MCP Server 实现 5 层安全防护：仅允许 SELECT、关键字黑名单正则阻断、表名 regex 校验、自动 LIMIT 限制、5 秒超时

**4. FastAPI 后端工程**
- 设计 10 张数据库表（users/knowledge_bases/documents/chunks/chat_sessions/chat_messages/agent_runs/mcp_servers/mcp_tools/mcp_tool_calls），使用 SQLAlchemy 2.0 异步 ORM + UUID 主键 + Enum 类型 + JSON 字段
- 实现 15 个 REST API 端点 + 1 个 WebSocket 端点，包含 JWT 认证、知识库 CRUD、文档上传/解析/切片全自动流水线、同步/流式 RAG 问答、Agent 工作流、MCP 管理
- WebSocket 流式输出支持 9 种事件类型（query_analyzed/retrieval_started/mcp_tool_call/answer_delta/citation/done/error），LLM token 级逐字推送
- 实现多轮对话记忆：自动加载 session 最近 10 条消息作为对话历史注入 prompt

**5. 工程化与测试**
- 使用 Pydantic v2 定义全部请求/响应 Schema，含 EmailStr 校验、字段长度约束
- 编写 289 个 Pytest 测试用例，使用 FakeLLM/FakeEmbedding/FakeReranker + SQLite 内存数据库实现全模块无外部依赖测试
- 开发单页前端联调面板（暗色主题、6 模块导航、WebSocket 事件流可视化、引用弹窗），基于原生 JS + CSS 无框架依赖
- Docker Compose 一键部署（backend + PostgreSQL + Redis + ChromaDB），支持 SQLite 本地零安装开发模式

## 项目亮点

- **三者协同**：RAG（知识检索）+ LangGraph（流程编排）+ MCP（工具标准化）三层解耦，各自独立可替换
- **混合检索**：BM25 + 向量 + RRF 融合 + Reranker，兼顾关键词匹配和语义理解
- **安全设计**：SQL 注入 5 层防护、文件路径穿越校验、MCP 工具白名单 + 三级权限
- **流式体验**：WebSocket 9 种事件类型，LLM token 级实时推送，支持中途取消
- **289 测试**：Fake/Mock 全部外部依赖，不依赖真实 LLM API 即可验证全链路逻辑

## 项目数据

| 维度 | 数据 |
|------|------|
| 代码提交 | 24 次 |
| 测试用例 | 289 个，全部通过 |
| API 端点 | 15 REST + 1 WebSocket |
| 数据库表 | 10 张 |
| Agent 节点 | 7 个（含 2 个条件路由） |
| MCP Server | 2 个（共 6 个工具） |
| 文档解析格式 | 6 种 |
