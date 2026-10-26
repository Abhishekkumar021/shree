from pathlib import Path
from typing import Any

from gemma_agent.config.settings import Settings, load_toml
from gemma_agent.guardrails.budget import Budget
from gemma_agent.guardrails.path_policy import PathPolicy
from gemma_agent.guardrails.shell_policy import ShellPolicy


class GuardrailPolicy:
    def __init__(self, settings: Settings, raw: dict[str, Any] | None = None) -> None:
        data = raw or load_toml("guardrails.toml")
        shell = data.get("shell", {})
        paths = data.get("paths", {})
        budget = data.get("budget", {})
        workspace = settings.gemma_agent_workspace
        workspace.mkdir(parents=True, exist_ok=True)

        self.shell = ShellPolicy(
            workspace,
            allowed_binaries=set(shell.get("allowed_binaries", [])),
            deny_substrings=list(shell.get("deny_substrings", [])),
            timeout_seconds=int(
                shell.get("timeout_seconds", settings.shell_timeout_seconds)
            ),
            test_timeout_seconds=int(
                shell.get("test_timeout_seconds", settings.test_timeout_seconds)
            ),
            max_output_bytes=int(
                shell.get("max_output_bytes", settings.max_output_bytes)
            ),
            allow_python_dash_c=bool(shell.get("allow_python_dash_c", False)),
        )
        self.paths = PathPolicy(
            workspace,
            allow_read_extensions=set(paths.get("allow_read_extensions", [".py"])),
            allow_write_extensions=set(paths.get("allow_write_extensions", [".py"])),
            deny_names=set(paths.get("deny_names", [])),
            max_file_bytes=int(paths.get("max_file_bytes", 1_048_576)),
        )
        self.budget = Budget(
            max_steps=int(budget.get("max_steps", settings.gemma_agent_max_steps)),
            max_shell_calls=int(budget.get("max_shell_calls", 12)),
            max_file_writes=int(budget.get("max_file_writes", 40)),
            max_patch_bytes=int(budget.get("max_patch_bytes", 200_000)),
        )
        self.workspace = workspace.resolve()

    @property
    def workspace_root(self) -> Path:
        return self.workspace
