from __future__ import annotations

from typing import Any

from gemma_agent.guardrails.policy import GuardrailPolicy


class ReadFileTool:
    name = "read_file"
    description = "Read a workspace file. Lines are 1-indexed and inclusive."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "filepath": {"type": "string"},
            "start_line": {"type": "integer"},
            "end_line": {"type": "integer"},
        },
        "required": ["filepath"],
    }

    def __init__(self, policy: GuardrailPolicy) -> None:
        self.policy = policy

    def run(
        self,
        filepath: str,
        start_line: int | None = None,
        end_line: int | None = None,
    ) -> str:
        path = self.policy.paths.check_read(filepath)
        if not path.is_file():
            return f"ERROR: file not found: {filepath}"
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        start = 1 if start_line is None else start_line
        end = len(lines) if end_line is None else end_line
        start = max(1, start)
        end = min(len(lines), end)
        sliced = lines[start - 1 : end]
        numbered = [f"{index + start}|{line}" for index, line in enumerate(sliced)]
        return "\n".join(numbered)


class WriteFileTool:
    name = "write_file"
    description = "Create or overwrite a text file inside the workspace."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "filepath": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["filepath", "content"],
    }

    def __init__(self, policy: GuardrailPolicy) -> None:
        self.policy = policy

    def run(self, filepath: str, content: str) -> str:
        self.policy.budget.consume_write()
        path = self.policy.paths.check_write(filepath, len(content.encode("utf-8")))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {filepath} ({len(content)} chars)"


class EditFileTool:
    name = "edit_file"
    description = "Replace old_string with new_string in an existing workspace file."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "filepath": {"type": "string"},
            "old_string": {"type": "string"},
            "new_string": {"type": "string"},
            "allow_multiple": {"type": "boolean"},
        },
        "required": ["filepath", "old_string", "new_string"],
    }

    def __init__(self, policy: GuardrailPolicy) -> None:
        self.policy = policy

    def run(
        self,
        filepath: str,
        old_string: str,
        new_string: str,
        allow_multiple: bool = False,
    ) -> str:
        path = self.policy.paths.check_read(filepath)
        if not path.is_file():
            return f"ERROR: file not found: {filepath}"
        original = path.read_text(encoding="utf-8")
        count = original.count(old_string)
        if count == 0:
            return "ERROR: old_string not found"
        if count > 1 and not allow_multiple:
            return f"ERROR: old_string found {count} times; set allow_multiple=true"
        updated = original.replace(old_string, new_string)
        self.policy.budget.consume_write()
        self.policy.paths.check_write(filepath, len(updated.encode("utf-8")))
        path.write_text(updated, encoding="utf-8")
        return f"Edited {filepath} ({count} replacement(s))"
