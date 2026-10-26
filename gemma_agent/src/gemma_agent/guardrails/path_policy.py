from pathlib import Path

from gemma_agent.guardrails.errors import GuardrailError


class PathPolicy:
    def __init__(
        self,
        workspace: Path,
        *,
        allow_read_extensions: set[str],
        allow_write_extensions: set[str],
        deny_names: set[str],
        max_file_bytes: int,
    ) -> None:
        self.workspace = workspace.resolve()
        self.allow_read_extensions = {ext.lower() for ext in allow_read_extensions}
        self.allow_write_extensions = {ext.lower() for ext in allow_write_extensions}
        self.deny_names = {name.lower() for name in deny_names}
        self.max_file_bytes = max_file_bytes

    def resolve(self, filepath: str) -> Path:
        raw = Path(filepath)
        candidate = raw if raw.is_absolute() else (self.workspace / raw)
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.workspace)
        except ValueError as exc:
            raise GuardrailError(f"Path escapes workspace: {filepath}") from exc
        name = resolved.name.lower()
        if name in self.deny_names or any(
            part.lower() in self.deny_names for part in resolved.parts
        ):
            raise GuardrailError(f"Path is denied: {filepath}")
        return resolved

    def check_read(self, filepath: str) -> Path:
        path = self.resolve(filepath)
        if path.suffix.lower() not in self.allow_read_extensions:
            raise GuardrailError(f"Read blocked for extension {path.suffix}: {filepath}")
        return path

    def check_write(self, filepath: str, content_size: int | None = None) -> Path:
        path = self.resolve(filepath)
        if path.suffix.lower() not in self.allow_write_extensions:
            raise GuardrailError(
                f"Write blocked for extension {path.suffix}: {filepath}"
            )
        if content_size is not None and content_size > self.max_file_bytes:
            raise GuardrailError(
                f"Write exceeds max_file_bytes ({self.max_file_bytes}): {filepath}"
            )
        return path
