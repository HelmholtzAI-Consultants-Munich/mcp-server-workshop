"""Tests for MCP server discovery.

Participants add a server by creating a file in mcp_servers/. Nothing
registers it, so these tests cover the mechanism that finds it, and the
failure modes a half-written server produces.

Plain pytest, no pytest-asyncio: the async parts run through asyncio.run.
"""
import asyncio
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from textwrap import dedent

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.mcp_client import (
    connect_servers,
    discover_server_modules,
    explain_failure,
    owners_of,
)

SERVERS_DIR = ROOT / "mcp_servers"

WORKING_SERVER = dedent(
    '''
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("temp-server")


    @mcp.tool()
    def temp_echo(text: str, times: int = 1) -> str:
        """Echo the text back."""
        return text * times


    if __name__ == "__main__":
        mcp.run()
    '''
)

EXTENSION_SERVER = dedent(
    '''
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("extension-server")


    @mcp.resource("workshop://example")
    def workshop_resource() -> str:
        """A small static resource for discovery tests."""
        return "example"


    @mcp.prompt()
    def workshop_prompt(question: str) -> str:
        """A small reusable prompt for discovery tests."""
        return f"Answer: {question}"


    if __name__ == "__main__":
        mcp.run()
    '''
)


@pytest.fixture
def temp_server():
    """Write a server file into mcp_servers/, as a participant would."""
    written = []

    def _write(stem: str, source: str) -> str:
        path = SERVERS_DIR / f"{stem}.py"
        assert not path.exists(), f"{path} already exists; pick another name"
        path.write_text(source)
        written.append(path)
        return f"mcp_servers.{stem}"

    yield _write
    for path in written:
        path.unlink(missing_ok=True)


def test_finds_the_shipped_servers():
    modules = discover_server_modules()
    assert "mcp_servers.pdf_server" in modules
    assert "mcp_servers.system_server" in modules


def test_skips_helpers_and_package_init():
    modules = discover_server_modules()
    assert "mcp_servers._paths" not in modules
    assert "mcp_servers.__init__" not in modules


def test_a_new_file_is_found_with_no_registration_step(temp_server):
    module = temp_server("temp_discovery_server", WORKING_SERVER)
    assert module in discover_server_modules()


def test_a_helper_file_is_not_mistaken_for_a_server(temp_server):
    module = temp_server("_temp_helper", "VALUE = 1\n")
    assert module not in discover_server_modules()


def test_list_tools_returns_name_description_and_schema():
    async def scenario():
        async with AsyncExitStack() as stack:
            connected, failures = await connect_servers(
                stack, ["mcp_servers.pdf_server"]
            )
            assert not failures
            _, tools = connected["mcp_servers.pdf_server"]
            by_name = {t.name: t for t in tools}
            assert "list_pdfs" in by_name
            extract = by_name["extract_pdf_text"]
            assert extract.description
            assert extract.inputSchema["required"] == ["filename"]
            # data_dir was removed. It must not reappear in the schema, or
            # the model will start inventing values for it.
            assert "data_dir" not in extract.inputSchema["properties"]

    asyncio.run(scenario())


def test_client_lists_resources_and_prompts(temp_server):
    module = temp_server("temp_extension_server", EXTENSION_SERVER)

    async def scenario():
        async with AsyncExitStack() as stack:
            connected, failures = await connect_servers(stack, [module])
            assert not failures
            client, _ = connected[module]
            resources = await client.list_resources()
            prompts = await client.list_prompts()
            assert [str(resource.uri) for resource in resources] == ["workshop://example"]
            assert [prompt.name for prompt in prompts] == ["workshop_prompt"]
            assert prompts[0].arguments[0].name == "question"

    asyncio.run(scenario())


def test_owners_maps_each_tool_to_its_own_server():
    async def scenario():
        async with AsyncExitStack() as stack:
            connected, _ = await connect_servers(stack)
            owners = owners_of(connected)
            assert owners["list_pdfs"].module == "mcp_servers.pdf_server"
            assert owners["get_current_time"].module == "mcp_servers.system_server"

    asyncio.run(scenario())


def test_a_students_server_is_usable_as_soon_as_the_file_exists(temp_server):
    module = temp_server("temp_usable_server", WORKING_SERVER)

    async def scenario():
        async with AsyncExitStack() as stack:
            connected, failures = await connect_servers(stack)
            assert not failures
            owners = owners_of(connected)
            assert owners["temp_echo"].module == module
            result = await owners["temp_echo"].call_tool(
                "temp_echo", {"text": "ab", "times": 2}
            )
            assert result["text"] == "abab"

    asyncio.run(scenario())


def test_one_broken_server_does_not_hide_the_working_ones(temp_server):
    module = temp_server("temp_broken_server", "import nonexistent_package\n")

    async def scenario():
        async with AsyncExitStack() as stack:
            connected, failures = await connect_servers(stack)
            assert module in failures
            assert "mcp_servers.pdf_server" in connected
            assert "list_pdfs" in owners_of(connected)

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "source, expected",
    [
        ("import nonexistent_package\n", "ModuleNotFoundError"),
        ("def broken(\n", "SyntaxError"),
        ("VALUE = UNDEFINED_THING\n", "NameError"),
    ],
)
def test_failure_is_explained_in_the_servers_own_words(temp_server, source, expected):
    module = temp_server("temp_explain_server", source)
    assert expected in explain_failure(module)
