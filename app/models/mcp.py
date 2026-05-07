"""MCP Server、MCP Tool 与 MCP Tool Call 模型。"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MCPTransport(str, enum.Enum):
    STDIO = "stdio"
    HTTP = "http"


class MCPPermissionLevel(str, enum.Enum):
    PUBLIC = "public"
    USER = "user"
    ADMIN = "admin"


class MCPToolCallStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    transport: Mapped[MCPTransport] = mapped_column(Enum(MCPTransport), default=MCPTransport.STDIO, nullable=False)
    endpoint: Mapped[str | None] = mapped_column(String(1000), default="")
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tools: Mapped[list["MCPTool"]] = relationship("MCPTool", back_populates="server", lazy="selectin")

    def __repr__(self) -> str:
        return f"<MCPServer {self.name} ({self.transport.value})>"


class MCPTool(Base):
    __tablename__ = "mcp_tools"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    server_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mcp_servers.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default="")
    input_schema: Mapped[dict | None] = mapped_column(JSON, default=dict)
    permission_level: Mapped[MCPPermissionLevel] = mapped_column(Enum(MCPPermissionLevel), default=MCPPermissionLevel.USER, nullable=False)

    server: Mapped["MCPServer"] = relationship("MCPServer", back_populates="tools")

    def __repr__(self) -> str:
        return f"<MCPTool {self.name} (perm={self.permission_level.value})>"


class MCPToolCall(Base):
    __tablename__ = "mcp_tool_calls"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("chat_sessions.id", ondelete="SET NULL"), default=None, index=True)
    tool_name: Mapped[str] = mapped_column(String(200), nullable=False)
    tool_input: Mapped[dict | None] = mapped_column(JSON, default=dict)
    tool_output: Mapped[dict | None] = mapped_column(JSON, default=dict)
    status: Mapped[MCPToolCallStatus] = mapped_column(Enum(MCPToolCallStatus), default=MCPToolCallStatus.PENDING, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("status", MCPToolCallStatus.PENDING)
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<MCPToolCall {self.tool_name} ({self.status.value})>"
