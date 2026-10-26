from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path

from gemma_agent.guardrails.errors import GuardrailError

_TEST_HINTS = ("pytest", "unittest", "-m pytest", "-m unittest")


@dataclass(frozen=True)
class ApprovedCommand:
    argv: tuple[str, ...]
    timeout_seconds: int
    cwd: Path
    kind: str


class ShellPolicy:
    """Allow running code/tests only. Never a free terminal."""

    def __init__(
        self,
        workspace: Path,
        *,
        allowed_binaries: set[str],
        deny_substrings: list[str],
        timeout_seconds: int,
        test_timeout_seconds: int,
        max_output_bytes: int,
        allow_python_dash_c: bool = False,
    ) -> None:
        self.workspace = workspace.resolve()
        self.allowed_binaries = {item.lower() for item in allowed_binaries}
        self.deny_substrings = [item.lower() for item in deny_substrings]
        self.timeout_seconds = timeout_seconds
        self.test_timeout_seconds = test_timeout_seconds
        self.max_output_bytes = max_output_bytes
        self.allow_python_dash_c = allow_python_dash_c

    def approve(self, command: str) -> ApprovedCommand:
        raw = command.strip()
        if not raw:
            raise GuardrailError("Empty command")
        lowered = raw.lower()
        for banned in self.deny_substrings:
            if banned in lowered:
                raise GuardrailError(f"Command denied by policy: {banned}")
        if any(token in raw for token in ("&&", "||", ";", "|", "`", "$(", "\n")):
            raise GuardrailError("Shell chaining and substitution are blocked")

        try:
            argv = tuple(shlex.split(raw, posix=os.name != "nt"))
        except ValueError as exc:
            raise GuardrailError(f"Could not parse command: {exc}") from exc
        if not argv:
            raise GuardrailError("Empty command")

        binary = Path(argv[0]).name.lower()
        if binary not in self.allowed_binaries:
            raise GuardrailError(
                f"Binary '{binary}' is not allowed. Code/tests only: "
                f"{sorted(self.allowed_binaries)}"
            )

        if binary.startswith("python") or binary in {"py", "py.exe"}:
            self._validate_python(argv)
        self._jail_path_args(argv)

        kind = "test" if self._is_test(argv, lowered) else "code"
        timeout = self.test_timeout_seconds if kind == "test" else self.timeout_seconds
        return ApprovedCommand(
            argv=argv,
            timeout_seconds=timeout,
            cwd=self.workspace,
            kind=kind,
        )

    def _validate_python(self, argv: tuple[str, ...]) -> None:
        flags = {arg for arg in argv[1:] if arg.startswith("-")}
        if "-c" in flags and not self.allow_python_dash_c:
            raise GuardrailError("python -c is blocked; run a workspace file instead")
        if any(flag.startswith("-c") and flag != "-c" for flag in flags):
            raise GuardrailError("python -c is blocked")

        module_idx = None
        for index, arg in enumerate(argv[1:], start=1):
            if arg == "-m":
                module_idx = index
                break
        if module_idx is not None:
            if module_idx + 1 >= len(argv):
                raise GuardrailError("python -m requires a module name")
            module = argv[module_idx + 1]
            if module not in {"pytest", "unittest", "ruff"}:
                raise GuardrailError(f"python -m {module} is not allowed")
            return

        script_args = [arg for arg in argv[1:] if not arg.startswith("-")]
        if not script_args:
            raise GuardrailError("Python must be given a workspace script path")
        script = Path(script_args[0])
        if script.suffix.lower() not in {".py"}:
            raise GuardrailError("Python may only run .py files")
        candidate = script if script.is_absolute() else (self.workspace / script)
        try:
            candidate.resolve().relative_to(self.workspace)
        except ValueError as exc:
            raise GuardrailError("Python script must stay inside the workspace") from exc

    def _jail_path_args(self, argv: tuple[str, ...]) -> None:
        for arg in argv[1:]:
            if arg.startswith("-") or arg in {"pytest", "unittest", "ruff"}:
                continue
            looks_like_path = (
                "/" in arg
                or "\\" in arg
                or arg.endswith((".py", ".pyi"))
                or Path(arg).suffix
            )
            if not looks_like_path:
                continue
            candidate = Path(arg)
            resolved = candidate if candidate.is_absolute() else (self.workspace / candidate)
            try:
                resolved.resolve().relative_to(self.workspace)
            except ValueError as exc:
                raise GuardrailError("Command path must stay inside the workspace") from exc

    def _is_test(self, argv: tuple[str, ...], lowered: str) -> bool:
        binary = Path(argv[0]).name.lower()
        if binary.startswith("pytest"):
            return True
        return any(hint in lowered for hint in _TEST_HINTS)
