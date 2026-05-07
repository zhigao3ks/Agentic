"""测试 MCP Server 注册表。"""

from app.mcp_client.registry import MCPRegistry, registry


class TestMCPRegistry:
    def test_register_server(self):
        reg = MCPRegistry()
        reg.register("test-srv", "stdio", "python -m test")
        assert reg.get("test-srv") is not None

    def test_register_duplicate_overwrites(self):
        reg = MCPRegistry()
        reg.register("srv", "stdio", "cmd1")
        reg.register("srv", "stdio", "cmd2")
        assert reg.get("srv").endpoint == "cmd2"

    def test_remove_server(self):
        reg = MCPRegistry()
        reg.register("srv", "stdio", "cmd")
        reg.remove("srv")
        assert reg.get("srv") is None

    def test_list_servers(self):
        reg = MCPRegistry()
        reg.register("a", "stdio", "a")
        reg.register("b", "http", "http://b")
        assert len(reg.list_servers()) == 2

    def test_global_registry(self):
        registry.register("global-test", "stdio", "echo")
        assert registry.get("global-test") is not None
        registry.remove("global-test")
