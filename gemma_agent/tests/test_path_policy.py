from pathlib import Path

import pytest

from gemma_agent.guardrails.errors import GuardrailError
from gemma_agent.guardrails.path_policy import PathPolicy


def policy(tmp_path: Path) -> PathPolicy:
    return PathPolicy(
        tmp_path,
        allow_read_extensions={".py", ".md"},
        allow_write_extensions={".py"},
        deny_names={".env"},
        max_file_bytes=100,
    )


def test_read_inside_workspace(tmp_path: Path) -> None:
    target = tmp_path / "mod.py"
    target.write_text("x = 1\n", encoding="utf-8")
    assert policy(tmp_path).check_read("mod.py") == target.resolve()


def test_blocks_escape(tmp_path: Path) -> None:
    with pytest.raises(GuardrailError):
        policy(tmp_path).check_read("../secret.py")


def test_blocks_env(tmp_path: Path) -> None:
    with pytest.raises(GuardrailError):
        policy(tmp_path).check_read(".env")
