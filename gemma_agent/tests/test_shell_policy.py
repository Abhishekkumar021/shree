from pathlib import Path

import pytest

from gemma_agent.guardrails.errors import GuardrailError
from gemma_agent.guardrails.shell_policy import ShellPolicy


def policy(tmp_path: Path) -> ShellPolicy:
    return ShellPolicy(
        tmp_path,
        allowed_binaries={"python", "python.exe", "pytest", "pytest.exe"},
        deny_substrings=["curl", "pip install", "rm -rf"],
        timeout_seconds=5,
        test_timeout_seconds=10,
        max_output_bytes=1024,
    )


def test_allows_pytest(tmp_path: Path) -> None:
    approved = policy(tmp_path).approve("pytest tests/test_mod.py")
    assert approved.kind == "test"
    assert approved.cwd == tmp_path.resolve()


def test_allows_python_file(tmp_path: Path) -> None:
    script = tmp_path / "run.py"
    script.write_text("print(1)\n", encoding="utf-8")
    approved = policy(tmp_path).approve("python run.py")
    assert approved.kind == "code"


def test_blocks_curl(tmp_path: Path) -> None:
    with pytest.raises(GuardrailError):
        policy(tmp_path).approve("curl https://example.com")


def test_blocks_python_dash_c(tmp_path: Path) -> None:
    with pytest.raises(GuardrailError):
        policy(tmp_path).approve("python -c print(1)")


def test_blocks_chaining(tmp_path: Path) -> None:
    with pytest.raises(GuardrailError):
        policy(tmp_path).approve("pytest tests && rm -rf /")
