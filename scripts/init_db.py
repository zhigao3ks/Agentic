"""初始化数据库：创建表结构并插入演示数据。

当前使用 SQLite（零安装），后续切换 MySQL 只需修改 DATABASE_URL。
运行方式：python3 scripts/init_db.py
"""

import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = "storage/agentic_rag.db"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def uid() -> str:
    return str(uuid.uuid4())


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'admin', 'developer')),
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS knowledge_bases (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            visibility TEXT NOT NULL DEFAULT 'private' CHECK(visibility IN ('private', 'team', 'public')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            kb_id TEXT NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'uploaded' CHECK(status IN ('uploaded','parsing','chunking','embedding','ready','error')),
            chunk_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            kb_id TEXT NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            page INTEGER DEFAULT NULL,
            section_title TEXT DEFAULT '',
            chunk_index INTEGER NOT NULL DEFAULT 0,
            metadata TEXT DEFAULT '{}',
            embedding_id TEXT DEFAULT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            kb_id TEXT DEFAULT NULL REFERENCES knowledge_bases(id) ON DELETE SET NULL,
            title TEXT DEFAULT 'New Chat',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            citations TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_runs (
            id TEXT PRIMARY KEY,
            session_id TEXT DEFAULT NULL REFERENCES chat_sessions(id) ON DELETE SET NULL,
            user_query TEXT NOT NULL,
            final_answer TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','running','completed','failed')),
            steps TEXT DEFAULT '[]',
            latency_ms INTEGER DEFAULT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS mcp_servers (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            transport TEXT NOT NULL DEFAULT 'stdio' CHECK(transport IN ('stdio', 'http')),
            endpoint TEXT DEFAULT '',
            enabled INTEGER NOT NULL DEFAULT 1,
            timeout_seconds INTEGER NOT NULL DEFAULT 30,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS mcp_tools (
            id TEXT PRIMARY KEY,
            server_id TEXT NOT NULL REFERENCES mcp_servers(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            input_schema TEXT DEFAULT '{}',
            permission_level TEXT NOT NULL DEFAULT 'user' CHECK(permission_level IN ('public', 'user', 'admin')),
            UNIQUE(server_id, name)
        );

        CREATE TABLE IF NOT EXISTS mcp_tool_calls (
            id TEXT PRIMARY KEY,
            session_id TEXT DEFAULT NULL REFERENCES chat_sessions(id) ON DELETE SET NULL,
            tool_name TEXT NOT NULL,
            tool_input TEXT DEFAULT '{}',
            tool_output TEXT DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','success','error','timeout')),
            latency_ms INTEGER DEFAULT NULL,
            created_at TEXT NOT NULL
        );
    """
    )
    conn.commit()


def insert_demo_data(conn: sqlite3.Connection) -> None:
    now = utcnow()

    # ── 3 个用户 ──
    u1, u2, u3 = uid(), uid(), uid()
    conn.execute(
        "INSERT INTO users VALUES (?,?,?,?,?,?,?,?)",
        (u1, "admin", "admin@example.com", "$2b$12$dummy_hash_admin", "admin", 1, now, now),
    )
    conn.execute(
        "INSERT INTO users VALUES (?,?,?,?,?,?,?,?)",
        (u2, "zhangsan", "zhangsan@example.com", "$2b$12$dummy_hash_user1", "user", 1, now, now),
    )
    conn.execute(
        "INSERT INTO users VALUES (?,?,?,?,?,?,?,?)",
        (u3, "lisi", "lisi@example.com", "$2b$12$dummy_hash_dev", "developer", 1, now, now),
    )

    # ── 2 个知识库 ──
    kb1, kb2 = uid(), uid()
    conn.execute(
        "INSERT INTO knowledge_bases VALUES (?,?,?,?,?,?,?)",
        (kb1, "公司制度与规范", "包含考勤、报销、安全等内部制度文档", u1, "team", now, now),
    )
    conn.execute(
        "INSERT INTO knowledge_bases VALUES (?,?,?,?,?,?,?)",
        (kb2, "产品技术文档", "产品需求、架构设计、API 文档等技术资料", u1, "team", now, now),
    )

    # ── 5 个文档 ──
    d1, d2, d3, d4, d5 = uid(), uid(), uid(), uid(), uid()
    conn.execute(
        "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?)",
        (d1, kb1, "考勤管理制度.pdf", "pdf", "storage/uploads/kb1/kq_gl.pdf", 245760, "ready", 6, now, now),
    )
    conn.execute(
        "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?)",
        (d2, kb1, "费用报销流程.docx", "docx", "storage/uploads/kb1/bx_lc.docx", 102400, "ready", 4, now, now),
    )
    conn.execute(
        "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?)",
        (d3, kb1, "信息安全管理制度.md", "md", "storage/uploads/kb1/xx_aq.md", 51200, "ready", 5, now, now),
    )
    conn.execute(
        "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?)",
        (d4, kb2, "MCP-Agentic-RAG-后端架构设计.pdf", "pdf", "storage/uploads/kb2/arch_design.pdf", 512000, "ready", 8, now, now),
    )
    conn.execute(
        "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?,?,?)",
        (d5, kb2, "API 接口文档.md", "md", "storage/uploads/kb2/api_doc.md", 86000, "ready", 5, now, now),
    )

    # ── 28 个 chunk ──
    chunks_data = [
        # 考勤管理制度 (6 chunks)
        (d1, kb1, "第一条 为规范公司考勤管理，保障正常的工作秩序，特制定本制度。适用范围：公司全体员工。", 1, "总则", 0),
        (d1, kb1, "第二条 工作时间：标准工作制为周一至周五，9:00-18:00，午休12:00-13:00。弹性工作制允许在8:00-10:00到岗。", 1, "工作时间", 1),
        (d1, kb1, "第三条 打卡要求：员工须在到岗和离岗时通过门禁系统或企业微信进行打卡。漏打卡需在24小时内提交补卡申请。", 2, "打卡规定", 2),
        (d1, kb1, "第四条 迟到与早退：月累计迟到3次以内不扣薪；超过3次每次扣50元。早退按旷工半天处理。", 2, "迟到与早退", 3),
        (d1, kb1, "第五条 请假类型包括：年假、事假、病假、婚假、产假/陪产假、丧假。各类假期需提前在OA系统提交申请。", 3, "请假管理", 4),
        (d1, kb1, "年假天数：入职满1年享5天，满3年享10天，满5年享15天。事假按日扣除工资，病假需提供医院证明。", 3, "假期标准", 5),
        # 费用报销流程 (4 chunks)
        (d2, kb1, "报销流程总览：提交申请→部门经理审批→财务审核→出纳付款。单笔金额5000元以下由部门经理终审。", 1, "流程概览", 0),
        (d2, kb1, "差旅费报销：需提供交通票据、住宿发票及出差审批单。住宿标准：一线城市不超过500元/晚，其他不超过350元/晚。", 2, "差旅费标准", 1),
        (d2, kb1, "招待费报销：需提前填写招待申请单，注明招待对象、事由、参与人员。人均不超过200元。", 3, "招待费规定", 2),
        (d2, kb1, "报销时效：费用发生后30日内提交报销，逾期不予受理。每月25日为报销截止日。", 4, "时效规定", 3),
        # 信息安全管理制度 (5 chunks)
        (d3, kb1, "信息安全管理制度适用于公司所有员工、外包人员和访客。信息安全遵循CIA三原则：保密性、完整性、可用性。", 1, "总则与适用范围", 0),
        (d3, kb1, "密码策略：系统密码长度不少于12位，须包含大小写字母、数字和特殊字符，每90天更换一次。禁止使用生日、手机号等弱密码。", 1, "密码管理", 1),
        (d3, kb1, "数据分级：公开数据、内部数据、机密数据、绝密数据四个等级。机密及以上数据须加密存储和传输。", 2, "数据分级", 2),
        (d3, kb1, "安全事件响应：发现安全事件后1小时内上报信息安全部门，4小时内启动应急响应，24小时内完成初步调查报告。", 3, "安全事件响应", 3),
        (d3, kb1, "违规处罚：泄露机密数据首次警告并罚款2000元，再次发生予以辞退并追究法律责任。", 4, "违规处罚", 4),
        # MCP-Agentic-RAG-后端架构设计 (8 chunks)
        (d4, kb2, "系统总体架构分为四层：API 接入层（FastAPI）、Agent 编排层（LangGraph）、工具协议层（MCP）、模型服务层（vLLM/Ollama）。", 1, "总体架构", 0),
        (d4, kb2, "RAG 检索链路：文档上传→PDF/DOCX/MD解析→结构化切片→bge-m3 Embedding→Chroma向量库→混合检索→Reranker精排→上下文构造。", 2, "RAG检索链路", 1),
        (d4, kb2, "混合检索策略：向量检索 TopK=20 + BM25 关键词检索 TopK=20 → RRF 融合 → bge-reranker-base 精排 → 最终取 TopK=5~8 送入 LLM。", 3, "混合检索策略", 2),
        (d4, kb2, "Agent 工作流：Query Analyzer → 条件路由（知识问答走 Retriever，数据分析走 Tool Planner）→ MCP Tool Agent → Answer Generator → Verifier。", 4, "Agent工作流", 3),
        (d4, kb2, "MCP Server 清单：Knowledge Base MCP Server（3个工具）、SQL Query MCP Server（3个工具）、File System MCP Server（4个工具）、Chart Generation MCP Server（3个工具）、Evaluation MCP Server（3个工具）。", 5, "MCP Server清单", 4),
        (d4, kb2, "数据库采用 PostgreSQL 存储业务数据，Redis 缓存会话状态和任务进度，Chroma 管理向量索引。核心业务表包括 users、knowledge_bases、documents、chunks、chat_sessions、chat_messages、agent_runs、mcp_servers、mcp_tools、mcp_tool_calls。", 6, "数据层设计", 5),
        (d4, kb2, "WebSocket 流式输出事件类型：query_analyzed、retrieval_started、mcp_tool_call、mcp_tool_result、answer_delta、citation、done、error。", 7, "流式输出", 6),
        (d4, kb2, "部署方案使用 Docker Compose 编排 5 个服务：backend、postgres、redis、chroma、ollama。通过 Nginx 反向代理对外暴露 8000 端口。", 8, "部署方案", 7),
        # API 接口文档 (5 chunks)
        (d5, kb2, "认证接口：POST /api/auth/register（注册）、POST /api/auth/login（登录返回JWT）、GET /api/auth/me（获取当前用户）。所有非认证接口需在 Header 中携带 Authorization: Bearer <token>。", 1, "认证接口", 0),
        (d5, kb2, "知识库管理接口：POST /api/kbs（创建）、GET /api/kbs（列表）、GET /api/kbs/{id}（详情）、PUT /api/kbs/{id}（更新）、DELETE /api/kbs/{id}（删除）。", 2, "知识库接口", 1),
        (d5, kb2, "文档接口：POST /api/kbs/{kb_id}/documents/upload（上传文件，支持 multipart/form-data）、GET /api/kbs/{kb_id}/documents（列表）、GET /api/documents/{id}/chunks（查看切片）。", 3, "文档接口", 2),
        (d5, kb2, "检索与问答接口：POST /api/retrieval/search（检索，返回chunk及分数）、POST /api/chat（同步问答）、WS /api/chat/stream（流式问答，WebSocket）。", 4, "检索问答接口", 3),
        (d5, kb2, "MCP 管理接口：GET /api/mcp/servers（Server列表）、GET /api/mcp/tools（工具列表）、POST /api/mcp/tools/refresh（刷新工具）、POST /api/mcp/tools/call（调用工具）。", 5, "MCP接口", 4),
    ]
    for doc_id, kb_id, content, page, section_title, chunk_idx in chunks_data:
        conn.execute(
            "INSERT INTO chunks VALUES (?,?,?,?,?,?,?,?,?,?)",
            (uid(), doc_id, kb_id, content, page, section_title, chunk_idx, "{}", None, now),
        )

    # ── 2 个会话 + 消息 ──
    s1, s2 = uid(), uid()
    conn.execute(
        "INSERT INTO chat_sessions VALUES (?,?,?,?,?,?)",
        (s1, u2, kb1, "考勤制度咨询", now, now),
    )
    conn.execute(
        "INSERT INTO chat_sessions VALUES (?,?,?,?,?,?)",
        (s2, u3, kb2, "系统架构调研", now, now),
    )
    conn.execute(
        "INSERT INTO chat_messages VALUES (?,?,?,?,?,?)",
        (uid(), s1, "user", "请问公司的考勤制度中，迟到怎么处罚？", "[]", now),
    )
    conn.execute(
        "INSERT INTO chat_messages VALUES (?,?,?,?,?,?)",
        (uid(), s1, "assistant",
         "根据《考勤管理制度》第四条规定：月累计迟到3次以内不扣薪；超过3次每次扣50元。[1]",
         '[{"doc_id":"' + d1 + '","chunk_id":"chunk_004","filename":"考勤管理制度.pdf","page":2,"section":"迟到与早退","score":0.95,"content_preview":"月累计迟到3次以内不扣薪..."}]',
         now),
    )
    conn.execute(
        "INSERT INTO chat_messages VALUES (?,?,?,?,?,?)",
        (uid(), s2, "user", "这个系统的 RAG 检索链路是怎么设计的？", "[]", now),
    )
    conn.execute(
        "INSERT INTO chat_messages VALUES (?,?,?,?,?,?)",
        (uid(), s2, "assistant",
         "系统 RAG 检索链路包括：文档上传→解析→结构化切片→bge-m3 Embedding→Chroma向量库→混合检索→Reranker精排→上下文构造。[2]",
         '[{"doc_id":"' + d4 + '","chunk_id":"chunk_010","filename":"MCP-Agentic-RAG-后端架构设计.pdf","page":2,"section":"RAG检索链路","score":0.92,"content_preview":"文档上传→PDF/DOCX/MD解析→..."}]',
         now),
    )

    # ── 2 个 Agent 执行记录 ──
    conn.execute(
        "INSERT INTO agent_runs VALUES (?,?,?,?,?,?,?,?)",
        (uid(), s1, "请问公司的考勤制度中，迟到怎么处罚？",
         "根据《考勤管理制度》第四条规定：月累计迟到3次以内不扣薪；超过3次每次扣50元。",
         "completed",
         '[{"node":"query_analyzer","status":"completed"},{"node":"retriever","status":"completed","chunks":6},{"node":"answer_generator","status":"completed"},{"node":"verifier","status":"completed","result":"pass"}]',
         2340, now),
    )
    conn.execute(
        "INSERT INTO agent_runs VALUES (?,?,?,?,?,?,?,?)",
        (uid(), s2, "这个系统的 RAG 检索链路是怎么设计的？",
         "系统 RAG 检索链路包括：文档上传→解析→结构化切片→bge-m3 Embedding→Chroma向量库→混合检索→Reranker精排→上下文构造。",
         "completed",
         '[{"node":"query_analyzer","status":"completed"},{"node":"retriever","status":"completed","chunks":8},{"node":"answer_generator","status":"completed"},{"node":"verifier","status":"completed","result":"pass"}]',
         3120, now),
    )

    # ── 3 个 MCP Server ──
    ms1, ms2, ms3 = uid(), uid(), uid()
    conn.execute(
        "INSERT INTO mcp_servers VALUES (?,?,?,?,?,?,?)",
        (ms1, "knowledge-base-mcp", "stdio", "python -m app.mcp_servers.knowledge_base.server", 1, 30, now),
    )
    conn.execute(
        "INSERT INTO mcp_servers VALUES (?,?,?,?,?,?,?)",
        (ms2, "sql-query-mcp", "stdio", "python -m app.mcp_servers.sql_query.server", 1, 30, now),
    )
    conn.execute(
        "INSERT INTO mcp_servers VALUES (?,?,?,?,?,?,?)",
        (ms3, "file-system-mcp", "stdio", "python -m app.mcp_servers.file_system.server", 1, 15, now),
    )

    # ── MCP Tools ──
    tools = [
        (ms1, "search_knowledge_base", "在指定知识库中检索相关文档片段", '{"type":"object","properties":{"query":{"type":"string"},"kb_id":{"type":"string"},"top_k":{"type":"integer","default":10}}}', "public"),
        (ms1, "get_document_detail", "获取文档元数据详情", '{"type":"object","properties":{"document_id":{"type":"string"}}}', "user"),
        (ms1, "get_chunk_context", "获取指定chunk的上下文片段", '{"type":"object","properties":{"chunk_id":{"type":"string"},"context_size":{"type":"integer","default":2}}}', "user"),
        (ms2, "list_tables", "列出数据库中所有表名", '{"type":"object","properties":{}}', "public"),
        (ms2, "describe_table", "获取指定表的结构信息", '{"type":"object","properties":{"table_name":{"type":"string"}}}', "user"),
        (ms2, "execute_readonly_sql", "安全执行只读SQL查询", '{"type":"object","properties":{"sql_query":{"type":"string"},"limit":{"type":"integer","default":100}}}', "admin"),
        (ms3, "list_files", "列出指定目录文件", '{"type":"object","properties":{"path":{"type":"string"}}}', "user"),
        (ms3, "read_file", "读取文件内容", '{"type":"object","properties":{"file_path":{"type":"string"}}}', "user"),
    ]
    for server_id, name, desc, schema, perm in tools:
        conn.execute(
            "INSERT INTO mcp_tools VALUES (?,?,?,?,?,?)",
            (uid(), server_id, name, desc, schema, perm),
        )

    # ── MCP 工具调用日志 ──
    conn.execute(
        "INSERT INTO mcp_tool_calls VALUES (?,?,?,?,?,?,?,?)",
        (uid(), s1, "search_knowledge_base",
         '{"query":"迟到处罚","kb_id":"' + kb1 + '","top_k":10}',
         '{"chunks":[{"content":"月累计迟到3次以内不扣薪...","score":0.95,"document_id":"' + d1 + '"}]}',
         "success", 120, now),
    )
    conn.execute(
        "INSERT INTO mcp_tool_calls VALUES (?,?,?,?,?,?,?,?)",
        (uid(), s2, "search_knowledge_base",
         '{"query":"RAG检索链路","kb_id":"' + kb2 + '","top_k":10}',
         '{"chunks":[{"content":"RAG检索链路：文档上传→解析→...","score":0.92,"document_id":"' + d4 + '"}]}',
         "success", 150, now),
    )

    conn.commit()


def main() -> None:
    import os
    os.makedirs("storage", exist_ok=True)

    conn = get_db()
    try:
        create_tables(conn)
        print("[OK] 10 张表创建完成")
        insert_demo_data(conn)
        print("[OK] 演示数据插入完成")
    finally:
        conn.close()

    # 统计
    conn2 = get_db()
    try:
        tables = ["users", "knowledge_bases", "documents", "chunks", "chat_sessions",
                  "chat_messages", "agent_runs", "mcp_servers", "mcp_tools", "mcp_tool_calls"]
        for t in tables:
            count = conn2.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t}: {count} 行")
    finally:
        conn2.close()

    print(f"\n数据库文件: {os.path.abspath(DB_PATH)}")


if __name__ == "__main__":
    main()
