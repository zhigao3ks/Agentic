# 简历包装与面试回复文档

> 面向大模型 / Agent / RAG / MCP / 后端开发实习岗


| **文档版本** | V1.0                                               |
|--------------|----------------------------------------------------|
| **生成日期** | 2026-05-07                                         |
| **适用方向** | 大模型应用 / Agent / RAG / MCP / Python 后端实习岗 |

# 1. 求职定位

**目标岗位：大模型应用开发实习生、Agent 开发实习生、RAG 工程实习生、Python 后端开发实习生、AI 平台开发实习生。**

核心叙事：你不是单纯做算法或论文，而是具备“多智能体系统设计 + RAG 应用工程 + Qwen/LoRA 模型经验 + FastAPI 后端开发 + MCP 工具协议扩展”的复合型能力。

| **简历关键词** | **呈现方式**                                                           |
|----------------|------------------------------------------------------------------------|
| 大模型应用     | 突出 Qwen/DeepSeek 调用、Prompt 设计、RAG、工具调用、流式生成          |
| Agent          | 突出任务拆解、角色分工、状态编排、工具规划、事实校验                   |
| RAG            | 突出文档解析、chunk 切片、Embedding、混合检索、Reranker、引用溯源      |
| MCP            | 突出外部工具协议化接入、MCP Client/Server、Tool Registry、权限与日志   |
| 后端开发       | 突出 FastAPI、PostgreSQL、Redis、WebSocket、Docker、接口设计、异步任务 |
| 模型服务       | 突出 vLLM、Ollama、LiteLLM、OpenAI-compatible API、本地部署            |

# 2. 推荐主项目名称

**最终推荐名称：面向企业知识库问答与数据分析的 MCP-Agentic RAG 后端系统**

一句话定位：面向企业内部文档问答、结构化数据分析和复杂知识任务处理场景，构建集成 RAG 检索增强、LangGraph Agent 编排、MCP 工具协议、FastAPI 后端服务与大模型流式推理的智能问答与分析系统。

> **名称解释：**“企业知识库问答与数据分析”明确应用场景，“MCP-Agentic RAG”明确技术路线，“后端系统”对齐实习岗位要求。

# 3. 简历项目描述：标准版

**项目名称：面向企业知识库问答与数据分析的 MCP-Agentic RAG 后端系统**

**项目描述：**

基于 FastAPI、LangGraph、MCP 和向量数据库构建企业知识库问答与数据分析系统，支持 PDF/Word/Markdown 等多格式文档上传、结构化切片、Embedding 向量化、BM25 + 向量混合检索、Reranker 精排、引用溯源与 WebSocket 流式输出。系统通过 Query Analyzer、Retriever、MCP Tool Agent、Answer Generator、Verifier 等多 Agent 协作流程，将问题分析、知识检索、工具调用、答案生成和事实校验解耦，提升复杂知识任务的可解释性与可靠性。

**个人贡献：**

1.  设计并实现文档解析与 RAG 检索链路，完成文档上传、文本清洗、结构化切片、Embedding 向量化、向量入库和引用溯源。

2.  引入 BM25 + 向量检索 + Reranker 的多阶段召回排序机制，提升专有名词、指标类问题和语义问答场景下的检索稳定性。

3.  基于 LangGraph 设计 Agent 工作流，将问题分析、检索、工具规划、答案生成和事实校验拆分为多个可观测节点。

4.  接入 MCP 工具协议，将知识库检索、SQL 查询、文件读取、图表生成和评测计算封装为 MCP Server，并实现 MCP Client、工具注册、权限控制、超时控制和调用日志。

5.  基于 FastAPI 构建后端接口，使用 PostgreSQL 管理用户、知识库、文档、会话和工具调用日志，使用 Redis 缓存会话状态，并通过 WebSocket 实现大模型流式输出。

6.  封装统一模型调用层，支持 vLLM/Ollama/云端 OpenAI-compatible API 接入，并记录模型调用耗时、token 使用量和异常信息。

# 4. 简历项目描述：不同岗位版本

## 4.1 大模型应用开发版

基于 FastAPI、LangGraph、MCP 和向量数据库构建企业知识库多智能体问答系统，支持多格式文档上传、结构化切片、混合检索、Reranker 精排、引用溯源和 WebSocket 流式输出。设计 Query Analyzer、Retriever、MCP Tool Agent、Answer Generator、Verifier 等多 Agent 流程，并通过 MCP 将知识库检索、SQL 查询、文件读取、图表生成等能力封装为标准化工具服务，提升系统复杂问题处理能力和可扩展性。

## 4.2 RAG 工程版

设计并实现面向企业文档的 RAG 后端系统，构建“文档解析—结构化切片—Embedding 向量化—BM25 关键词召回—向量检索—Reranker 精排—LLM 生成—引用溯源”的完整链路。针对长文档问答中的召回不准和幻觉问题，引入混合检索、证据校验和引用追踪机制，并使用 Recall@K、MRR、Citation Accuracy 和 Latency 评估系统效果。

## 4.3 Agent / MCP 版

设计基于 MCP 工具协议的 Agentic RAG 系统，通过 LangGraph 构建问题分析、工具规划、MCP 工具调用、答案生成和事实校验的状态化 Agent 工作流。将数据库查询、文档检索、文件读取、图表生成和评测计算封装为独立 MCP Server，并在后端实现 MCP Client、Tool Registry、权限校验、超时控制和调用日志追踪，降低 Agent 工具扩展成本。

## 4.4 Python 后端开发版

基于 FastAPI 构建大模型应用后端服务，使用 PostgreSQL 管理用户、知识库、文档、会话和 MCP 工具调用日志，使用 Redis 缓存会话状态和任务进度，集成 Chroma/Milvus 实现向量检索，并通过 WebSocket 支持大模型流式输出。系统支持 Docker Compose 一键部署，并提供知识库管理、文档上传、检索问答、MCP 工具调用和评测接口。

# 5. 你现有简历项目的重包装方向

| **原项目**                             | **建议包装方向**                           | **可突出技术点**                                           |
|----------------------------------------|--------------------------------------------|------------------------------------------------------------|
| 高校治理多智能体数据分析与辅助决策平台 | 组织知识库 + 数据分析 Agent + 决策支持系统 | RAG、Agent、指标分析、可视化、SQL/表格工具调用、MCP Server |
| 面向教育场景的多智能体伴学交互系统     | 实时语音 Agent 伴学系统                    | Qwen、LoRA、ASR/TTS/VAD、WebSocket、记忆管理、云边路由     |
| IPSE 任务规划与高保真评测系统          | 多 Agent 规划生成与仿真评测闭环            | Planner/Verifier、仿真反馈、评价指标、闭环优化             |
| Text2SQL / 校对系统相关经历            | 数据库问答与 SQL Tool Agent                | 自然语言解析、SQL 生成、安全执行、结果总结、MCP SQL Server |
| 多模态挑战赛经历                       | 复杂场景理解与多模型协同推理               | 模型集成、置信度筛选、思维链、多智能体评审                 |

# 6. 技能栈模块写法

| **类别**     | **简历写法**                                                                          |
|--------------|---------------------------------------------------------------------------------------|
| 编程与后端   | Python、FastAPI、Pydantic、SQLAlchemy/SQLModel、WebSocket、RESTful API、Docker、Linux |
| 数据库与缓存 | PostgreSQL、MySQL、Redis、Chroma/Milvus/FAISS                                         |
| 大模型应用   | Qwen、DeepSeek、Ollama、vLLM、LiteLLM、OpenAI-compatible API、Prompt Engineering      |
| RAG          | 文档解析、Chunk 切片、Embedding、BM25、Hybrid Retrieval、Reranker、引用溯源、RAG 评测 |
| Agent        | LangGraph、Qwen-Agent、Tool Calling、MCP、Agent Workflow、Memory、Verifier            |
| 模型训练     | Transformers、PEFT、LoRA/QLoRA、BitsAndBytes、Accelerate                              |

# 7. 面试自我介绍模板

## 7.1 60 秒版本

您好，我目前是计算机技术方向硕士，主要做大模型应用、多智能体系统和 RAG 相关工作。我的项目经历主要集中在三个方向：第一是面向高校治理的数据分析与辅助决策平台，涉及多源数据处理、知识检索、Agent 分析和可视化；第二是面向教育场景的实时语音伴学系统，包含 Qwen 模型微调、ASR/TTS/VAD、WebSocket 流式交互和多 Agent 任务编排；第三是我近期重点补强的 MCP-Agentic RAG 后端系统，基于 FastAPI、LangGraph、MCP 和向量数据库实现企业知识库问答与数据分析。我的优势是既了解大模型、RAG、Agent 的应用逻辑，也有 Python 后端、数据库、WebSocket 和模型部署的工程经验，希望投递大模型应用开发、Agent、RAG 或后端开发相关实习岗位。

## 7.2 2 分钟版本

您好，我叫黄志高，目前研究方向主要集中在大模型决策、多智能体协同和大小模型协同。我的经历比较偏大模型应用工程：一方面我参与过高校治理场景的多智能体数据分析平台，负责数据处理、指标分析、可视化和基于大模型的分析 Agent 设计；另一方面我做过教育场景的多智能体伴学系统，涉及 Qwen 模型的 LoRA 定向微调、ASR/TTS/VAD 集成、WebSocket 全双工语音链路以及云边动态路由。

为了更贴近实习岗位，我还把这些经验进一步整理成一个 MCP-Agentic RAG 后端项目，系统支持企业文档上传、文档解析、chunk 切片、Embedding、BM25 + 向量混合检索、Reranker 精排、引用溯源和 WebSocket 流式输出。同时，我引入 MCP 作为 Agent 工具接入协议，将知识库检索、SQL 查询、文件读取、图表生成和评测计算封装为 MCP Server，并用 LangGraph 编排问题分析、工具规划、答案生成和事实校验流程。这个项目主要体现我在大模型应用、RAG、Agent 工具调用和 FastAPI 后端工程方面的能力。

# 8. 高频面试问答

**Q1：你这个项目里的 MCP 是干什么的？**

MCP 在我的项目中主要承担 Agent 工具协议层的作用。传统 Agent 往往把 Python 函数直接注册为工具，和业务代码耦合较强。我的设计是将知识库检索、SQL 查询、文件读取、图表生成和评测计算封装为独立 MCP Server，FastAPI 后端作为 MCP Client 连接这些 Server。这样 Agent 不需要关心工具内部实现，只需要根据工具描述和参数 schema 调用对应能力，工具扩展、权限控制和日志追踪都会更清晰。

**Q2：MCP、RAG、LangGraph 三者是什么关系？**

RAG 负责知识检索，解决大模型无法访问私有知识和容易幻觉的问题；LangGraph 负责 Agent 的状态化任务编排，把复杂任务拆成分析、检索、工具调用、生成和校验多个节点；MCP 负责把外部工具和数据源标准化暴露给 Agent。三者分别对应知识层、流程层和工具协议层。

**Q3：为什么不用普通 Tool Calling，而要用 MCP？**

普通 Tool Calling 通常是项目内部函数注册，适合小型 Demo，但当工具数量增多、需要接入数据库、文件系统、图表服务、评测服务时，直接函数调用会造成强耦合。MCP 可以把工具封装为独立 Server，统一工具发现、参数 schema、调用协议和权限控制，更适合工程化扩展。

**Q4：RAG 的完整流程是什么？**

我的流程是文档上传、格式校验、文本解析、结构化切片、Embedding 向量化、向量入库、用户问题重写、向量检索、BM25 关键词召回、候选结果融合、Reranker 精排、构造上下文、LLM 生成答案、Verifier 校验并返回引用来源。

**Q5：为什么要做 BM25 + 向量混合检索？**

向量检索适合语义相似问题，但对专有名词、编号、指标名、政策条款这类精确词面匹配不稳定；BM25 对关键词匹配更敏感。因此我会先分别召回候选片段，再进行分数融合和 Reranker 精排，兼顾语义相关性和关键词准确性。

**Q6：chunk 怎么切？**

我不会只按固定长度硬切，而是优先保留标题、章节、段落和表格边界。默认 chunk_size 设为 500~800 中文字符，overlap 设为 80~150 字符，同时保存 page、section_title、source_file、start_char、end_char 等元数据，便于引用溯源。

**Q7：Reranker 放在什么位置？**

Reranker 放在初步召回之后、送入大模型之前。向量检索和 BM25 先扩大召回范围，例如各取 Top20，然后由 Reranker 对候选 chunk 与问题的相关性进行精排，最终取 Top5~8 作为上下文。

**Q8：如何减少幻觉？**

主要从四方面做：第一，检索阶段提高证据质量；第二，prompt 中要求答案必须基于证据；第三，Verifier Agent 检查答案是否被引用片段支持；第四，当检索证据不足时明确返回不确定或提示补充资料，而不是强行生成。

**Q9：WebSocket 流式输出怎么实现？**

后端通过 WebSocket 建立长连接，用户发送 query 后，服务端依次推送 query_analyzed、retrieval_started、mcp_tool_call、answer_delta、citation、done 等事件。模型服务层使用 streaming completion，把 token 增量转发给前端，从而降低首 token 等待时间并提升交互体验。

**Q10：MCP 调用有什么安全风险，怎么控制？**

风险主要包括工具越权、SQL 修改数据、任意文件读取、超时阻塞和恶意参数。我的控制方式包括工具白名单、Pydantic 参数校验、SQL 只允许 SELECT、限制返回行数、限制文件访问目录、设置超时时间、记录工具调用日志和对敏感信息脱敏。

**Q11：vLLM 在项目中解决什么问题？**

vLLM 用于本地大模型服务化，提供高吞吐和较好的显存利用能力，并暴露 OpenAI-compatible API。这样 FastAPI 后端可以通过统一模型调用层访问本地 Qwen/DeepSeek 等模型，也便于后续替换模型或扩展并发。

**Q12：这个项目最难的地方是什么？**

我认为难点有三个：第一是文档解析和 chunk 切片要尽量保留语义结构；第二是检索链路要兼顾召回率、精度和延迟；第三是 Agent 工具调用需要可控，尤其是 MCP 工具权限、参数校验、失败回退和日志追踪。

# 9. 投递消息 / 邮件模板

## 9.1 Boss / 牛客 / 实习僧简短私信

您好，我是计算机技术方向硕士，主要方向是大模型应用、RAG、Agent 和 Python 后端开发。近期项目包括基于 FastAPI + LangGraph + MCP 的企业知识库 Agentic RAG 后端系统，涉及文档解析、混合检索、Reranker、MCP 工具调用、WebSocket 流式输出和 vLLM 模型服务。希望有机会应聘贵团队大模型应用 / Agent / 后端相关实习岗位，附件是我的简历，期待进一步沟通。

## 9.2 邮件投递版

邮件主题：大模型应用开发实习生_黄志高_计算机技术硕士

老师/HR 您好：
我是黄志高，目前为计算机技术方向硕士，主要研究和项目经历集中在大模型应用、多智能体系统、RAG 和 Python 后端开发。我的项目包括面向高校治理的多智能体数据分析平台、面向教育场景的实时语音伴学系统，以及基于 FastAPI、LangGraph、MCP 和向量数据库的企业知识库 Agentic RAG 后端系统。
我熟悉 Qwen/DeepSeek 调用、LoRA 微调、文档解析、Embedding、混合检索、Reranker、MCP 工具协议、WebSocket 流式输出和后端接口开发，希望投递贵团队大模型应用 / Agent / RAG / 后端开发相关实习岗位。附件为我的简历，期待您的回复。

## 9.3 面试开场项目引入

我最近重点整理和补强的是一个面向企业知识库问答与数据分析的 MCP-Agentic RAG 后端系统。它不是单纯的文档问答，而是把 RAG 检索、Agent 状态编排、MCP 工具协议和 FastAPI 后端服务结合起来：RAG 负责知识检索，LangGraph 负责多步骤任务流程，MCP 负责把 SQL 查询、文件读取、图表生成等工具标准化暴露给 Agent，FastAPI 负责接口、会话、流式输出和日志管理。

# 10. 简历注意事项

- 不要堆砌“多智能体、RAG、MCP、vLLM”等关键词，必须绑定具体模块和功能。

- 未完成的功能建议写“设计并实现原型”“接入基础链路”“支持初步调用”，不要写成生产级。

- 如果没有真实评测数据，避免写“提升 xx%”，可以写“构建评测指标体系，支持 Recall@K、MRR、Latency 等指标统计”。

- 项目描述中要体现后端工程：接口、数据库、缓存、日志、鉴权、Docker、WebSocket。

- 面试时优先讲架构和技术取舍，而不是只讲用了哪些库。

# 11. 一周内可补强任务清单

| **优先级** | **任务**                                                      | **产出**              |
|------------|---------------------------------------------------------------|-----------------------|
| Day 1      | 搭建 FastAPI 项目结构、配置 PostgreSQL/Redis/Chroma           | 可启动后端骨架        |
| Day 2      | 实现文档上传、PDF/TXT/DOCX 解析和 chunk 切片                  | 文档入库链路          |
| Day 3      | 接入 bge-m3 embedding 和向量检索                              | 基础 RAG 问答         |
| Day 4      | 加入 BM25、Reranker 和引用溯源                                | 增强检索链路          |
| Day 5      | 用 LangGraph 实现 Query Analyzer、Retriever、Answer、Verifier | Agentic RAG 流程      |
| Day 6      | 实现 Knowledge Base MCP Server 和 SQL Query MCP Server        | MCP 技术亮点          |
| Day 7      | 补 README、接口文档、Docker Compose 和项目截图                | 可投递/可面试项目材料 |

# 12. 简历最终推荐项目条目

**面向企业知识库问答与数据分析的 MCP-Agentic RAG 后端系统**

- 基于 FastAPI、LangGraph、MCP 和向量数据库构建企业知识库问答与数据分析系统，支持多格式文档解析、结构化切片、Embedding 向量化、混合检索、Reranker 精排、引用溯源和 WebSocket 流式输出。

- 设计 Query Analyzer、Retriever、MCP Tool Agent、Answer Generator、Verifier 等 Agent 节点，将问题分析、检索、工具调用、答案生成和事实校验解耦。

- 引入 MCP 作为 Agent 工具接入协议，将知识库检索、SQL 查询、文件读取、图表生成和评测计算封装为 MCP Server，并实现 MCP Client、Tool Registry、权限控制、超时控制和调用日志追踪。

- 使用 PostgreSQL 管理用户、知识库、文档、会话和工具日志，使用 Redis 缓存会话状态，封装 vLLM/Ollama/OpenAI-compatible 模型调用层，支持本地和远程模型切换。
