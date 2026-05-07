# 项目开发需求文档

> 面向企业知识库问答与数据分析的 MCP-Agentic RAG 后端系统


| **文档版本** | V1.0                                               |
|--------------|----------------------------------------------------|
| **生成日期** | 2026-05-07                                         |
| **适用方向** | 大模型应用 / Agent / RAG / MCP / Python 后端实习岗 |

# 1. 项目概述

**项目名称：面向企业知识库问答与数据分析的 MCP-Agentic RAG 后端系统**

项目定位：面向企业、学校、科研团队或组织内部知识管理场景，构建一个集成 RAG 检索增强、Agent 工作流编排、MCP 工具协议、FastAPI 后端服务、WebSocket 流式输出、本地/远程大模型调用与评测监控的智能问答与分析系统。

核心目标：不是做简单的文档问答 Demo，而是做一个可以体现大模型应用开发、RAG 工程、Agent 工具调用、MCP 工程化、Python 后端服务与模型部署能力的综合项目。

> **边界说明：**如果项目尚处于原型阶段，简历中建议使用“设计并实现原型”“接入”“构建基础链路”等表述，避免写成已经生产级落地。

| **维度** | **内容**                                                                                                |
|----------|---------------------------------------------------------------------------------------------------------|
| 应用场景 | 企业内部文档问答、结构化数据分析、科研论文阅读、项目材料辅助分析、知识库决策支持                        |
| 核心技术 | FastAPI、LangGraph、MCP、RAG、Qwen/DeepSeek、vLLM、LiteLLM、WebSocket、PostgreSQL、Redis、Milvus/Chroma |
| 主要能力 | 文档解析、知识库构建、混合检索、Reranker 精排、Agent 编排、MCP 工具调用、引用溯源、流式输出、系统评测   |
| 岗位匹配 | 大模型应用开发、Agent 开发、RAG 工程、Python 后端开发、AI 平台开发实习岗                                |

# 2. 技术定位与系统价值

- RAG 负责把企业私有文档、业务材料和知识库内容转化为可检索上下文，缓解大模型无法访问私有知识和容易幻觉的问题。

- LangGraph / Agent 编排负责将复杂任务拆分为问题分析、检索、工具规划、答案生成和事实校验等步骤。

- MCP 作为统一工具协议层，将知识库检索、SQL 查询、文件读取、图表生成、评测计算等能力封装为可发现、可调用、可管理的 MCP Server。

- FastAPI 负责对外提供 REST API、WebSocket 流式接口、认证鉴权、任务调度和后端服务化能力。

- vLLM / LiteLLM / Ollama 负责模型服务部署与统一调用，支持本地模型和 OpenAI-compatible API。

> **MCP 的项目作用：**MCP 不替代 RAG，也不替代 LangGraph。RAG 提供知识，LangGraph 负责任务流程，MCP 负责把外部工具和数据源标准化暴露给 Agent。

# 3. 用户角色与典型场景

| **用户角色**  | **核心诉求**                   | **系统能力**                                        |
|---------------|--------------------------------|-----------------------------------------------------|
| 普通用户      | 上传文档并进行知识问答         | 文档上传、自动解析、知识库问答、引用来源返回        |
| 业务/科研人员 | 对大量材料进行总结、对比和分析 | 多文档检索、摘要生成、表格分析、图表生成            |
| 管理员        | 管理知识库、模型、权限和日志   | 用户管理、知识库权限、MCP Server 管理、调用日志审计 |
| 开发者        | 扩展 Agent 工具与后端能力      | MCP Tool 注册、Agent 工作流配置、模型服务配置       |

- 场景 1：上传公司制度、项目文档和会议纪要，系统自动构建知识库并支持带引用来源的问答。

- 场景 2：上传学科评估材料、指标数据和政策文件，系统进行指标解释、趋势归因和辅助决策建议。

- 场景 3：上传论文 PDF，系统辅助提取研究问题、方法、实验设置、创新点和局限性。

- 场景 4：用户提出复杂分析任务，系统通过多个 Agent 与 MCP 工具协作完成检索、统计、制表和结论生成。

# 4. 总体架构设计

```text
用户 / 前端页面 / API Client
│
▼
FastAPI 后端服务
├── 用户认证与权限模块
├── 知识库管理模块
├── 文档上传与解析模块
├── RAG 检索与重排序模块
├── LangGraph Agent 编排模块
├── MCP Client 与 Tool Registry 模块
├── 模型调用与流式输出模块
├── 会话管理与日志模块
└── 评测监控模块
│
├── PostgreSQL：用户、知识库、文档、会话、Agent/MCP 调用日志
├── Redis：会话缓存、任务状态、限流、短期记忆
├── Milvus / Chroma / FAISS：向量索引
└── MinIO / Local Storage：原始文件与解析结果
│
▼
Agent Orchestration Layer
├── Query Analyzer Agent
├── Retriever Agent
├── Tool Planner Agent
├── MCP Tool Agent
├── Answer Generator Agent
└── Verifier Agent
│
▼
MCP Tool Layer
├── Knowledge Base MCP Server
├── SQL Query MCP Server
├── File System MCP Server
├── Chart Generation MCP Server
└── Evaluation MCP Server
│
▼
LLM Gateway / Serving Layer
├── LiteLLM
├── vLLM
├── Ollama
└── OpenAI-compatible API
│
▼
Qwen / DeepSeek / Llama / 其他大模型
```

# 5. 技术选型

| **层级**     | **推荐技术**                                   | **说明**                                        |
|--------------|------------------------------------------------|-------------------------------------------------|
| 后端服务     | FastAPI、Pydantic、SQLAlchemy/SQLModel         | 提供 API、数据校验、ORM 与业务服务组织          |
| 数据库与缓存 | PostgreSQL、Redis                              | 业务数据持久化、会话状态、任务缓存、短期记忆    |
| 文档解析     | PyMuPDF、pdfplumber、python-docx、unstructured | 支持 PDF、Word、Markdown、TXT、CSV 等格式解析   |
| 向量检索     | bge-m3、Milvus/Chroma/FAISS                    | Embedding 向量化与语义召回                      |
| 关键词检索   | BM25                                           | 补充专有名词、编号、指标类问题的关键词召回能力  |
| 重排序       | bge-reranker-base/large、cross-encoder         | 对召回候选片段精排，提升上下文质量              |
| Agent 编排   | LangGraph、Qwen-Agent 思路                     | 状态化任务编排、工具规划、答案校验              |
| MCP 接入     | MCP Python SDK / FastMCP、自定义 MCP Client    | 统一外部工具、数据源和工作流接入方式            |
| 模型服务     | vLLM、Ollama、LiteLLM                          | 本地推理、模型网关、统一 OpenAI-compatible 调用 |
| 通信与部署   | WebSocket、Docker Compose、Nginx               | 流式输出、服务编排和部署                        |

# 6. 核心功能需求

## 6.1 用户认证与权限模块

| **编号** | **功能**                               | **优先级** |
|----------|----------------------------------------|------------|
| AUTH-01  | 用户注册、登录、JWT Token 认证         | P1         |
| AUTH-02  | 用户角色管理：普通用户、管理员、开发者 | P2         |
| AUTH-03  | 知识库访问权限控制：私有、团队、公开   | P2         |
| AUTH-04  | API Key 管理与调用限流                 | P3         |

## 6.2 知识库管理模块

| **编号** | **功能**                                                    | **优先级** |
|----------|-------------------------------------------------------------|------------|
| KB-01    | 创建、查询、更新、删除知识库                                | P1         |
| KB-02    | 知识库文档统计、chunk 数量统计、索引状态展示                | P2         |
| KB-03    | 知识库权限配置与成员管理                                    | P2         |
| KB-04    | 知识库配置：Embedding 模型、检索 TopK、是否启用 BM25/Rerank | P3         |

## 6.3 文档上传、解析与切片模块

- 支持 PDF、DOCX、Markdown、TXT、CSV/XLSX 等常见格式。

- 上传后对文件类型、大小、MIME 类型进行校验，原始文件存储到本地或 MinIO。

- 解析后进行文本清洗，保留标题、页码、段落、表格、章节等结构化元数据。

- 默认切片参数建议：chunk_size = 500~800 中文字符，chunk_overlap = 80~150 中文字符。

- 优先按照标题、章节、段落、表格边界切分，避免固定窗口破坏语义结构。

文档上传 → 格式校验 → 原始文件存储 → 文本解析 → 文本清洗
→ 结构化切片 → 元数据生成 → Embedding 向量化 → 向量入库 → 文档状态更新

## 6.4 Embedding 与索引模块

| **编号** | **功能**                                              | **优先级** |
|----------|-------------------------------------------------------|------------|
| EMB-01   | 调用 bge-m3 / bge-large-zh 等模型生成文本向量         | P1         |
| EMB-02   | 向量写入 Milvus / Chroma / FAISS，并按 kb_id 隔离索引 | P1         |
| EMB-03   | 支持批量向量化、增量更新与删除同步                    | P2         |
| EMB-04   | 支持 Embedding 模型配置与版本记录                     | P3         |

## 6.5 混合检索与 Reranker 模块

用户问题
→ Query Rewrite（可选）
→ 向量检索 TopK=20
→ BM25 关键词检索 TopK=20
→ 候选结果融合
→ Reranker 精排
→ 选取 TopK=5~8 作为上下文
→ 送入 LLM 生成答案

- 向量检索用于语义召回，适合概念相近但词面不同的问题。

- BM25 用于关键词召回，适合专有名词、政策编号、指标名称、术语类问题。

- Reranker 对候选 chunk 进行精排，减少无关上下文进入大模型。

- 系统需要保存每次检索结果、分数、TopK 和是否命中引用，用于后续评测。

## 6.6 MCP 工具协议模块

MCP 模块是本项目的核心亮点之一。系统将知识库检索、SQL 查询、文件访问、图表生成和评测计算封装为独立 MCP Server，FastAPI 后端作为 MCP Client 连接这些 Server，由 Agent 根据任务需要动态调用。

| **MCP Server**              | **主要工具**                                                     | **项目价值**                      |
|-----------------------------|------------------------------------------------------------------|-----------------------------------|
| Knowledge Base MCP Server   | search_knowledge_base、get_document_detail、get_chunk_context    | 把 RAG 检索能力标准化暴露给 Agent |
| SQL Query MCP Server        | list_tables、describe_table、execute_sql、summarize_query_result | 支持结构化数据问答和数据分析任务  |
| File System MCP Server      | list_files、read_file、extract_text、get_file_metadata           | 支持受控文件访问和文档解析任务    |
| Chart Generation MCP Server | generate_bar_chart、generate_line_chart、generate_table_summary  | 支持把分析结果转成图表或表格      |
| Evaluation MCP Server       | calculate_recall_at_k、calculate_mrr、evaluate_faithfulness      | 支持 RAG 检索和回答质量评测       |

| **编号** | **MCP Client 功能**                             | **优先级** |
|----------|-------------------------------------------------|------------|
| MCP-C-01 | 支持连接本地 MCP Server                         | P1         |
| MCP-C-02 | 支持获取 Server 暴露的工具列表与 schema         | P1         |
| MCP-C-03 | 支持按工具名称调用 MCP Tool 并解析返回结果      | P1         |
| MCP-C-04 | 支持工具参数校验、权限控制、超时控制和错误处理  | P1         |
| MCP-C-05 | 记录 MCP 调用日志：输入、输出、状态、耗时、异常 | P1         |
| MCP-C-06 | 支持多个 MCP Server 注册、启停和动态刷新        | P2         |

Agent 产生工具调用意图
→ Tool Planner Agent 选择 MCP Tool
→ MCP Client 校验权限与参数
→ 调用对应 MCP Server
→ 获取工具结果
→ 写入 mcp_tool_calls 日志
→ 返回给 Answer Generator Agent

## 6.7 Agent 编排模块

| **Agent**              | **职责**                                           | **是否调用 MCP**                 |
|------------------------|----------------------------------------------------|----------------------------------|
| Query Analyzer Agent   | 分析用户问题类型、意图、是否需要检索或工具调用     | 否                               |
| Retriever Agent        | 执行知识库检索，获取候选证据                       | 可调用 Knowledge Base MCP Server |
| Tool Planner Agent     | 判断需要调用哪些 MCP 工具，并生成参数              | 是                               |
| MCP Tool Agent         | 统一负责 MCP 工具调用、结果解析和错误处理          | 是                               |
| Answer Generator Agent | 基于证据和工具结果生成最终回答                     | 否                               |
| Verifier Agent         | 检查回答是否有证据支持、引用是否准确、是否存在幻觉 | 可调用 Evaluation MCP Server     |

用户问题 → Query Analyzer Agent
├─ 普通知识问答：Retriever Agent → Answer Generator Agent → Verifier Agent
├─ 数据分析问题：Tool Planner Agent → SQL/Chart MCP Server → Answer Generator Agent
├─ 文档分析问题：File/KnowledgeBase MCP Server → Answer Generator Agent
└─ 评测优化问题：Evaluation MCP Server → 分析报告生成

- 防止 Agent 失控：最大步数限制、工具白名单、参数 schema 校验、工具调用超时、失败回退策略。

- 当检索结果不足或证据不支持回答时，系统应明确返回“不确定”或提示用户补充资料，而不是编造答案。

## 6.8 对话、流式输出与引用溯源模块

| **编号** | **功能**                                                    | **优先级** |
|----------|-------------------------------------------------------------|------------|
| CHAT-01  | 创建会话、保存历史消息、支持多轮对话                        | P1         |
| CHAT-02  | WebSocket 流式输出 answer_delta、tool_call、citation 等事件 | P1         |
| CHAT-03  | 支持停止生成、异常中断与任务状态恢复                        | P2         |
| CHAT-04  | 返回引用来源：文档名、页码、章节、chunk_id、证据片段        | P1         |
| CHAT-05  | 支持用户反馈：点赞、点踩、问题标签                          | P2         |

```text
WebSocket 事件示例：
{"event":"query_analyzed", "data":"识别为数据分析问题"}
{"event":"retrieval_started", "data":"开始检索知识库"}
{"event":"mcp_tool_call", "data":{"tool":"execute_sql"}}
{"event":"answer_delta", "data":"根据检索结果..."}
{"event":"citation", "data":\[{"doc":"项目申报书.pdf", "page":5}\]}
{"event":"done", "data":"完成"}
```

## 6.9 模型服务模块

- 使用 LiteLLM 封装统一 LLM 调用层，屏蔽本地模型与远程模型接口差异。

- 使用 vLLM 部署 Qwen / DeepSeek / Llama 等模型，提供 OpenAI-compatible API 与流式输出。

- 开发阶段可以先用 Ollama 或云端 API 跑通链路，再替换为 vLLM 本地部署。

- 模型调用层应记录 prompt、模型名、token 用量、响应耗时和异常信息，便于调试与成本分析。

## 6.10 评测模块

| **指标**           | **说明**                                            |
|--------------------|-----------------------------------------------------|
| Recall@K           | 标准证据是否出现在 TopK 检索结果中                  |
| MRR                | 正确证据排名是否靠前                                |
| Answer Relevance   | 回答是否切题                                        |
| Faithfulness       | 回答是否忠实于检索证据                              |
| Citation Accuracy  | 引用是否真实支持回答                                |
| Latency            | 请求响应时间、首 token 延迟、检索耗时、工具调用耗时 |
| Hallucination Rate | 无证据回答或错误归因比例                            |

# 7. 数据库设计

| **表名**        | **关键字段**                                                           | **说明**               |
|-----------------|------------------------------------------------------------------------|------------------------|
| users           | id、username、email、password_hash、role、created_at                   | 用户账户与角色信息     |
| knowledge_bases | id、name、description、owner_id、visibility                            | 知识库元数据与权限范围 |
| documents       | id、kb_id、filename、file_type、file_path、status、chunk_count         | 文档元数据和解析状态   |
| chunks          | id、document_id、kb_id、content、page、section_title、metadata         | 文档切片与引用元数据   |
| chat_sessions   | id、user_id、kb_id、title、created_at                                  | 会话信息               |
| chat_messages   | id、session_id、role、content、citations、created_at                   | 多轮对话消息           |
| agent_runs      | id、session_id、user_query、final_answer、status、latency_ms           | Agent 执行日志         |
| mcp_servers     | id、name、transport、endpoint、enabled、timeout_seconds                | MCP Server 注册信息    |
| mcp_tools       | id、server_id、name、description、input_schema、permission_level       | MCP Tool 元数据        |
| mcp_tool_calls  | id、session_id、tool_name、tool_input、tool_output、status、latency_ms | MCP 工具调用日志       |

# 8. API 接口设计

| **模块** | **接口**                                                                                                        |
|----------|-----------------------------------------------------------------------------------------------------------------|
| 认证     | POST /api/auth/register；POST /api/auth/login；GET /api/auth/me                                                 |
| 知识库   | POST /api/kbs；GET /api/kbs；GET /api/kbs/{kb_id}；PUT /api/kbs/{kb_id}；DELETE /api/kbs/{kb_id}                |
| 文档     | POST /api/kbs/{kb_id}/documents/upload；GET /api/kbs/{kb_id}/documents；GET /api/documents/{document_id}/chunks |
| 检索     | POST /api/retrieval/search                                                                                      |
| 对话     | POST /api/chat；WS /api/chat/stream；GET /api/chat/sessions/{session_id}                                        |
| MCP      | GET /api/mcp/servers；GET /api/mcp/tools；POST /api/mcp/tools/refresh；POST /api/mcp/tools/call                 |
| 评测     | POST /api/eval/datasets；POST /api/eval/run；GET /api/eval/results/{run_id}                                     |

# 9. 非功能需求

| **类别** | **要求**                                                                                  |
|----------|-------------------------------------------------------------------------------------------|
| 性能     | 普通问答 3~8 秒内响应；首 token 延迟 1~3 秒；检索延迟 0.5~1.5 秒；MVP 支持 10~30 并发请求 |
| 安全     | JWT 鉴权、文件上传校验、MCP 工具白名单、SQL 只读限制、路径访问限制、日志脱敏              |
| 可维护性 | API 层、服务层、Agent 层、MCP 层解耦；工具可独立扩展；配置集中管理                        |
| 可观测性 | 记录检索分数、Agent 步骤、MCP 调用、模型耗时、token 使用量和错误堆栈                      |
| 部署     | Docker Compose 一键启动，支持 PostgreSQL、Redis、向量库、后端服务和 MCP Server 编排       |

# 10. 项目目录结构建议

```text
agentic-rag-mcp-backend/
├── app/
│ ├── main.py
│ ├── api/ \# auth、kb、document、retrieval、chat、agent、mcp、eval
│ ├── core/ \# config、security、logging、exceptions
│ ├── services/ \# parser、chunker、embedding、vector、bm25、rerank、llm、mcp_client
│ ├── agents/ \# state、graph、query_analyzer、tool_planner、mcp_tool、answer、verifier
│ ├── mcp_servers/ \# knowledge_base、sql_query、file_system、chart_generation、evaluation
│ ├── models/ \# user、kb、document、chunk、chat、agent、mcp
│ ├── schemas/ \# Pydantic schemas
│ └── tests/
├── scripts/ \# init_db、ingest_demo_docs、run_eval、start_mcp_servers
├── docker/ \# Dockerfile、docker-compose.yml
├── README.md
├── requirements.txt
└── .env.example
```

# 11. 开发里程碑

| **阶段**                 | **目标**              | **交付内容**                                                                                 |
|--------------------------|-----------------------|----------------------------------------------------------------------------------------------|
| 阶段一：基础 RAG 后端    | 跑通文档问答闭环      | FastAPI、文档上传、解析、切片、Embedding、向量检索、普通 RAG 问答、引用溯源                  |
| 阶段二：Agentic RAG      | 引入状态化 Agent 编排 | Query Analyzer、Retriever、Answer Generator、Verifier、LangGraph 工作流、Agent 日志          |
| 阶段三：MCP 工具协议接入 | 形成项目核心亮点      | MCP Client、MCP Server 注册、Knowledge Base/SQL/File/Chart/Evaluation MCP Server、权限与日志 |
| 阶段四：工程化与模型服务 | 体现后端和部署能力    | PostgreSQL、Redis、WebSocket、Docker Compose、vLLM、LiteLLM、评测模块                        |

# 12. 验收标准

- 能够上传至少 3 种格式文档，并自动解析、切片、向量化和入库。

- 能够对指定知识库进行问答，并返回引用来源。

- 能够通过 BM25 + 向量检索 + Reranker 完成多阶段召回排序。

- 能够通过 WebSocket 返回流式回答和中间事件。

- 至少实现 3 个 MCP Server，并支持 Agent 调用。

- 能够记录 Agent 执行日志、MCP 工具调用日志和模型调用耗时。

- 能够基于小型评测集输出 Recall@K、MRR、Citation Accuracy 和 Latency。

- 能够通过 Docker Compose 启动主要服务，并在 README 中提供完整运行步骤。

# 13. 参考资料

- Model Context Protocol 官方文档：https://modelcontextprotocol.io/docs/getting-started/intro

- MCP Specification：https://modelcontextprotocol.io/specification/2025-11-25

- Anthropic MCP Introduction：https://www.anthropic.com/news/model-context-protocol

- LangGraph GitHub：https://github.com/langchain-ai/langgraph

- Dify GitHub：https://github.com/langgenius/dify

- RAGFlow GitHub：https://github.com/infiniflow/ragflow

- LlamaIndex GitHub：https://github.com/run-llama/llama_index

- vLLM GitHub：https://github.com/vllm-project/vllm

- LiteLLM GitHub：https://github.com/BerriAI/litellm
