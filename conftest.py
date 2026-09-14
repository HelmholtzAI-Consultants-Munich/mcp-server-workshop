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


@pytest.fixture
def adapter_impl(request):
    path = request.config.getoption("--adapter-reference")
    if not path:
        from agent import adapter
        return adapter
    spec = importlib.util.spec_from_file_location("reference_adapter", Path(path).resolve())
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
