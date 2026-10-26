from __future__ import annotations

import subprocess
from typing import Any

from gemma_agent.guardrails.policy import GuardrailPolicy


class SubmitPatchTool:
    name = "submit_patch"
    description = "Capture git diff HEAD from the workspace as the candidate patch."
    parameters: dict[str, Any] = {"type": "object", "properties": {}}

    def __init__(self, policy: GuardrailPolicy) -> None:
        self.policy = policy

    def run(self) -> str:
        subprocess.run(
            ["git", "add", "-N", "."],
            cwd=self.policy.workspace,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
        diff = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=self.policy.workspace,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
        patch = diff.stdout or ""
        if len(patch.encode("utf-8")) > self.policy.budget.max_patch_bytes:
            return "ERROR: patch exceeds max_patch_bytes"
        if not patch.strip():
            return "No changes to submit."
        return patch


class GetStatusTool:
    name = "get_status"
    description = "Return live budget consumption."
    parameters: dict[str, Any] = {"type": "object", "properties": {}}

    def __init__(self, policy: GuardrailPolicy) -> None:
        self.policy = policy

    def run(self) -> str:
        return str(self.policy.budget.snapshot())
