from __future__ import annotations

from typing import Any

from gemma_agent.guardrails.errors import GuardrailError
from gemma_agent.guardrails.policy import GuardrailPolicy
from gemma_agent.tools.base import Tool, openai_schema
from gemma_agent.tools.filesystem import EditFileTool, ReadFileTool, WriteFileTool
from gemma_agent.tools.graph import (
    GetCodeNeighborsTool,
    GetCodeSubgraphTool,
    SearchSimilarCodeTool,
)
from gemma_agent.tools.patch import GetStatusTool, SubmitPatchTool
from gemma_agent.tools.search import GrepWorkspaceTool
from gemma_agent.tools.shell import RunCodeTool


class ToolRegistry:
    def __init__(self, tools: list[Tool]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def schemas(self) -> list[dict[str, Any]]:
        return [openai_schema(tool) for tool in self._tools.values()]

    def call(self, name: str, arguments: dict[str, Any]) -> str:
        tool = self._tools.get(name)
        if tool is None:
            raise GuardrailError(f"Unknown tool: {name}")
        return tool.run(**arguments)


def build_default_registry(policy: GuardrailPolicy) -> ToolRegistry:
    return ToolRegistry(
        [
            ReadFileTool(policy),
            WriteFileTool(policy),
            EditFileTool(policy),
            GrepWorkspaceTool(policy),
            RunCodeTool(policy),
            SubmitPatchTool(policy),
            GetStatusTool(policy),
            GetCodeNeighborsTool(),
            SearchSimilarCodeTool(),
            GetCodeSubgraphTool(),
        ]
    )
