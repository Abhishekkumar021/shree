from __future__ import annotations

from typing import Any, Protocol


class Tool(Protocol):
    name: str
    description: str
    parameters: dict[str, Any]

    def run(self, **kwargs: Any) -> str: ...


def openai_schema(tool: Tool) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        },
    }
