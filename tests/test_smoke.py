"""Smoke tests: verify the toolchain and environment work.

These deliberately do not import `agent.*` yet: importing it creates
Supabase/Gemini clients at import time and requires credentials.
Replace with real unit tests after the DI refactor (#TBD)
"""

import importlib
import sys
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def test_python_version_matches_projects() -> None:
    assert sys.version_info >= (3, 13)

@pytest.mark.parametrize("module", ["langgraph", "langchain_core", "fastapi", "pydantic"])
def test_core_dependencies_are_importable(module: str) -> None:
    importlib.import_module(module)

def test_pyproject_has_real_description() -> None:
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        project = tomllib.load(f)["project"]
    assert project["description"] != "Add your description here"
