import json
import subprocess
import sys
from contextlib import AsyncExitStack, suppress
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent, Tool

ROOT = Path(__file__).resolve().parent.parent
SERVERS_DIR = ROOT / "mcp_servers"


def discover_server_modules() -> list[str]:
    """Every MCP server in mcp_servers/, as importable module paths.

    Files starting with an underscore are helpers, not servers, so they are
    skipped. That is also the rule for your own server: name it without a
    leading underscore and it is picked up with no registration step.
    """
    return [
        f"{SERVERS_DIR.name}.{path.stem}"
        for path in sorted(SERVERS_DIR.glob("*.py"))
        if not path.stem.startswith("_")
    ]


class MCPToolError(RuntimeError):
    """The server reported a tool execution error (MCP isError)."""


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
        try:
            transport = await self._stack.enter_async_context(stdio_client(params))
            read, write = transport
            self.session = await self._stack.enter_async_context(
                ClientSession(read, write)
            )
            await self.session.initialize()
        except BaseException:
            # A server that dies on startup leaves a subprocess and a task group
            # behind. Close them here, in the task that opened them, or the
            # caller's teardown fails with an unrelated anyio cancel-scope error.
            with suppress(Exception):
                await self._stack.aclose()
            raise
        return self

    async def __aexit__(self, *_) -> None:
        await self._stack.aclose()

    async def list_tools(self) -> list[Tool]:
        """Ask the server which tools it has.

        Each tool carries .name, .description (from your docstring) and
        .inputSchema (generated from your type hints).
        """
        if not self.session:
            raise RuntimeError("MCP client not connected")
        return (await self.session.list_tools()).tools

    async def list_resources(self):
        """Ask the server for its static MCP resources."""
        if not self.session:
            raise RuntimeError("MCP client not connected")
        return (await self.session.list_resources()).resources

    async def list_resource_templates(self):
        """Ask the server for parameterized MCP resource templates."""
        if not self.session:
            raise RuntimeError("MCP client not connected")
        return (await self.session.list_resource_templates()).resourceTemplates

    async def list_prompts(self):
        """Ask the server for its reusable MCP prompt templates."""
        if not self.session:
            raise RuntimeError("MCP client not connected")
        return (await self.session.list_prompts()).prompts

    async def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        if not self.session:
            raise RuntimeError("MCP client not connected")
        result = await self.session.call_tool(name, arguments or {})
        text = "".join(
            c.text for c in result.content if isinstance(c, TextContent)
        )
        if result.isError:
            raise MCPToolError(text or f"Tool {name} failed without an explanation")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"text": text}


def explain_failure(module: str) -> str:
    """Why a server would not start, in the server's own words.

    The MCP layer only reports "Connection closed" when a server dies on
    startup, which says nothing about the cause. Importing the module runs
    everything above `if __name__ == "__main__"` without starting the server,
    so a syntax error or a bad import surfaces with its real traceback.
    """
    try:
        proc = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "importing the module timed out"
    err = (proc.stderr or "").strip()
    if proc.returncode == 0:
        return "the module imports fine, so it fails once the server starts"
    return err.splitlines()[-1] if err else f"exited with code {proc.returncode}"


async def connect_servers(
    stack: AsyncExitStack,
    modules: list[str] | None = None,
) -> tuple[dict[str, tuple[MCPClient, list[Tool]]], dict[str, Exception]]:
    """Start every discovered server and ask each one for its tools.

    Returns ({module: (client, tools)}, {module: error}). A server that fails
    to start lands in the second dict instead of taking down the rest, so one
    broken file does not hide every working tool.
    """
    connected: dict[str, tuple[MCPClient, list[Tool]]] = {}
    failures: dict[str, Exception] = {}
    for module in modules if modules is not None else discover_server_modules():
        try:
            client = await stack.enter_async_context(MCPClient(module))
            connected[module] = (client, await client.list_tools())
        except Exception as exc:
            failures[module] = exc
    return connected, failures


def owners_of(
    connected: dict[str, tuple[MCPClient, list[Tool]]],
) -> dict[str, MCPClient]:
    """Map each tool name to the client that serves it."""
    return {tool.name: client for client, tools in connected.values() for tool in tools}
