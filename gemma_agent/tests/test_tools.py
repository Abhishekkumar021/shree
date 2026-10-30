from pathlib import Path

import pytest

from gemma_agent.config.settings import Settings
from gemma_agent.guardrails.errors import GuardrailError
from gemma_agent.guardrails.policy import GuardrailPolicy
from gemma_agent.tools.registry import build_default_registry


def make_registry(tmp_path: Path):
    settings = Settings(gemma_agent_workspace=tmp_path)
    policy = GuardrailPolicy(settings)
    return build_default_registry(policy), policy


def test_list_dir_empty(tmp_path: Path) -> None:
    registry, _ = make_registry(tmp_path)
    text = registry.call("list_dir", {"path": "."})
    assert "EMPTY_WORKSPACE" in text


def test_write_and_read(tmp_path: Path) -> None:
    registry, _ = make_registry(tmp_path)
    registry.call("write_file", {"filepath": "hello.py", "content": "print('hi')\n"})
    text = registry.call("read_file", {"filepath": "hello.py"})
    assert "print('hi')" in text


def test_run_code_blocks_shell(tmp_path: Path) -> None:
    registry, _ = make_registry(tmp_path)
    with pytest.raises(GuardrailError):
        registry.call("run_code", {"command": "ls -la"})
