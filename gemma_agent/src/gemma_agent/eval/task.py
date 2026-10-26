from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IssueTask:
    task_id: str
    statement: str
    repo_path: Path | None = None
    tests: tuple[str, ...] = ()
