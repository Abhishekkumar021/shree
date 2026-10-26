from __future__ import annotations

from typing import Any

from gemma_agent.guardrails.policy import GuardrailPolicy


class GrepWorkspaceTool:
    name = "search_text"
    description = "Search workspace text files for a literal or simple pattern."
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "glob": {"type": "string"},
            "max_hits": {"type": "integer"},
        },
        "required": ["query"],
    }

    def __init__(self, policy: GuardrailPolicy) -> None:
        self.policy = policy

    def run(self, query: str, glob: str = "*.py", max_hits: int = 50) -> str:
        if not query:
            return "ERROR: empty query"
        hits: list[str] = []
        for path in self.policy.workspace.rglob(glob):
            if not path.is_file():
                continue
            try:
                self.policy.paths.check_read(str(path.relative_to(self.policy.workspace)))
            except Exception:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for number, line in enumerate(text.splitlines(), start=1):
                if query in line:
                    rel = path.relative_to(self.policy.workspace)
                    hits.append(f"{rel}:{number}:{line.strip()}")
                    if len(hits) >= max_hits:
                        return "\n".join(hits)
        return "\n".join(hits) if hits else "No matches."
