from __future__ import annotations

import json
import logging
from typing import Any

from gemma_agent.agent.parser import extract_actions
from gemma_agent.agent.state import AgentResult, AgentState
from gemma_agent.config.settings import Settings
from gemma_agent.guardrails.errors import GuardrailError
from gemma_agent.guardrails.policy import GuardrailPolicy
from gemma_agent.llm.client import LlamaChatClient
from gemma_agent.llm.messages import expand_tool_calls
from gemma_agent.llm.prompts import default_system_prompt
from gemma_agent.tools.registry import ToolRegistry, build_default_registry

logger = logging.getLogger("gemma_agent.loop")


class AgentLoop:
    def __init__(
        self,
        settings: Settings,
        policy: GuardrailPolicy | None = None,
        client: LlamaChatClient | None = None,
        tools: ToolRegistry | None = None,
    ) -> None:
        self.settings = settings
        self.policy = policy or GuardrailPolicy(settings)
        self.client = client or LlamaChatClient(settings)
        self.tools = tools or build_default_registry(self.policy)

    def run(self, issue: str) -> AgentResult:
        state = AgentState(
            issue=issue,
            messages=[
                {"role": "system", "content": default_system_prompt()},
                {
                    "role": "user",
                    "content": (
                        "Work on the following request in the workspace. "
                        "If the workspace is empty, create the project with write_file. "
                        "Use list_dir before read_file. Run tests with run_code. "
                        "Call submit_patch when done.\n\n"
                        f"{issue}"
                    ),
                },
            ],
        )
        error: str | None = None
        try:
            for _ in range(self.policy.budget.max_steps):
                self.policy.budget.consume_step()
                reply = self.client.chat(state.messages, tools=self.tools.schemas())
                actions = list(reply.get("tool_calls") or [])
                if not actions:
                    actions = extract_actions(reply.get("content") or "")
                assistant_message: dict[str, Any] = {
                    "role": "assistant",
                    "content": reply.get("content") or None,
                }
                if actions:
                    assistant_message["tool_calls"] = expand_tool_calls(actions)
                else:
                    assistant_message["content"] = reply.get("content") or ""
                state.messages.append(assistant_message)
                if not actions:
                    if "submit_patch" in (reply.get("content") or ""):
                        state.patch = self.tools.call("submit_patch", {})
                        state.done = True
                        break
                    logger.info("Model produced no tool call; stopping")
                    break
                for action in actions:
                    name = action["name"]
                    arguments = action.get("arguments") or {}
                    try:
                        result = self.tools.call(name, arguments)
                    except GuardrailError as exc:
                        result = f"GUARDRAIL: {exc}"
                        state.last_error = str(exc)
                    except TypeError as exc:
                        result = f"ERROR: bad tool arguments: {exc}"
                    state.messages.append(
                        {
                            "role": "tool",
                            "content": result,
                            "tool_call_id": action.get("id") or name,
                        }
                    )
                    if name == "submit_patch" and not result.startswith("ERROR"):
                        state.patch = result
                        state.done = True
                        break
                if state.done:
                    break
        except GuardrailError as exc:
            error = str(exc)
            logger.warning("Agent stopped by guardrail: %s", exc)
        return AgentResult(
            issue=issue,
            patch=state.patch,
            steps=self.policy.budget.steps,
            done=state.done,
            transcript=state.messages,
            error=error or state.last_error,
        )


def result_to_json(result: AgentResult) -> str:
    return json.dumps(
        {
            "issue": result.issue,
            "done": result.done,
            "steps": result.steps,
            "patch": result.patch,
            "error": result.error,
        },
        indent=2,
    )
