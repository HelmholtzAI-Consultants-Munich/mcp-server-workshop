"""Select a facilitator adapter explicitly; ordinary runs use student code."""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def pytest_addoption(parser):
    parser.addoption("--adapter-reference", metavar="PATH",
                     help="Run the exercise and integration checks against a local reference adapter")
    parser.addoption("--server-reference", metavar="PATH",
                     help="Run the starter-server checks against a local reference server")


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "exercise: fails until the participant implements it; deselect with -m 'not exercise'",
    )


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, Path(path).resolve())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def adapter_impl(request):
    path = request.config.getoption("--adapter-reference")
    if not path:
        from agent import adapter
        return adapter
    return _load(path, "reference_adapter")


@pytest.fixture
def research_server_impl(request):
    """The starter server: the participant's, or a reference for facilitators."""
    path = request.config.getoption("--server-reference")
    if not path:
        from mcp_servers import research_server
        return research_server
    return _load(path, "reference_research_server")
