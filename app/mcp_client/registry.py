"""MCP Server 注册表 —— 管理 MCP Server 的连接与生命周期。"""

from dataclasses import dataclass, field

from mcp import ClientSession, StdioServerParameters, stdio_client


@dataclass
class MCPServerInfo:
    name: str
    transport: str  # "stdio" | "http"
    endpoint: str   # command for stdio, URL for http
    enabled: bool = True
    timeout_seconds: int = 30
    session: ClientSession | None = field(default=None, repr=False)
    _read = None
    _write = None


class MCPRegistry:
    def __init__(self) -> None:
        self._servers: dict[str, MCPServerInfo] = {}

    def register(self, name: str, transport: str, endpoint: str, timeout: int = 30) -> None:
        self._servers[name] = MCPServerInfo(
            name=name, transport=transport, endpoint=endpoint, timeout_seconds=timeout,
        )

    def remove(self, name: str) -> None:
        self._servers.pop(name, None)

    def get(self, name: str) -> MCPServerInfo | None:
        return self._servers.get(name)

    def list_servers(self) -> list[MCPServerInfo]:
        return list(self._servers.values())

    async def connect(self, name: str) -> ClientSession | None:
        info = self._servers.get(name)
        if not info or not info.enabled:
            return None

        if info.session:
            return info.session

        if info.transport == "stdio":
            server_params = StdioServerParameters(command=info.endpoint.split()[0], args=info.endpoint.split()[1:])
            read, write = await stdio_client(server_params).__aenter__()
            session = await ClientSession(read, write).__aenter__()
            await session.initialize()
            info._read = read
            info._write = write
            info.session = session
            return session

        # HTTP transport 暂不实现
        return None

    async def disconnect(self, name: str) -> None:
        info = self._servers.get(name)
        if info and info.session:
            await info.session.__aexit__(None, None, None)
            info.session = None


registry = MCPRegistry()
