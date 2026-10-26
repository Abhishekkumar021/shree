from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    issue: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    patch: str | None = None
    done: bool = False
    last_error: str | None = None


@dataclass
class AgentResult:
    issue: str
    patch: str | None
    steps: int
    done: bool
    transcript: list[dict[str, Any]]
    error: str | None = None
