from __future__ import annotations

import subprocess
from typing import Any

from gemma_agent.guardrails.errors import GuardrailError
from gemma_agent.guardrails.policy import GuardrailPolicy


class RunCodeTool:
    name = "run_code"
    description = (
        "Run Python or pytest inside the workspace jail. Arbitrary shell is blocked."
    )
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Example: python -m pytest tests/test_mod.py",
            }
        },
        "required": ["command"],
    }

    def __init__(self, policy: GuardrailPolicy) -> None:
        self.policy = policy

    def run(self, command: str) -> str:
        self.policy.budget.consume_shell()
        approved = self.policy.shell.approve(command)
        try:
            completed = subprocess.run(
                list(approved.argv),
                cwd=approved.cwd,
                capture_output=True,
                text=True,
                timeout=approved.timeout_seconds,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise GuardrailError(
                f"Command timed out after {approved.timeout_seconds}s"
            ) from exc
        output = (completed.stdout or "") + (completed.stderr or "")
        limit = self.policy.shell.max_output_bytes
        if len(output.encode("utf-8")) > limit:
            output = output.encode("utf-8")[:limit].decode("utf-8", errors="replace")
            output += "\n[truncated]"
        return (
            f"exit={completed.returncode} kind={approved.kind}\n{output}".strip()
        )
