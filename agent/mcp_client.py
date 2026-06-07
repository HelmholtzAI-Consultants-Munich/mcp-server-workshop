import json
import sys
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

ROOT = Path(__file__).resolve().parent.parent


class MCPClient:
    def __init__(self, module: str):
        self.module = module
        self._stack = AsyncExitStack()
        self.session: ClientSession | None = None

    async def __aenter__(self) -> "MCPClient":
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", self.module],
            cwd=str(ROOT),
        )
        transport = await self._stack.enter_async_context(stdio_client(params))
        read, write = transport
        self.session = await self._stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        return self

    async def __aexit__(self, *_) -> None:
        await self._stack.aclose()

    async def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        if not self.session:
            raise RuntimeError("MCP client not connected")
        result = await self.session.call_tool(name, arguments or {})
        text = "".join(
            c.text for c in result.content if isinstance(c, TextContent)
        )
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"text": text}
