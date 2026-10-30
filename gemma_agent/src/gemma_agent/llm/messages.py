from __future__ import annotations

import json
from typing import Any


def flatten_tool_calls(tool_calls: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for index, call in enumerate(tool_calls or []):
        if "function" in call:
            raw_args = call["function"].get("arguments") or "{}"
            name = call["function"].get("name")
            call_id = call.get("id") or f"call_{index}"
        else:
            raw_args = call.get("arguments") or {}
            name = call.get("name")
            call_id = call.get("id") or f"call_{index}"
        if isinstance(raw_args, str):
            try:
                arguments = json.loads(raw_args)
            except json.JSONDecodeError:
                arguments = {"_raw": raw_args}
        elif isinstance(raw_args, dict):
            arguments = raw_args
        else:
            arguments = {}
        if not isinstance(name, str):
            continue
        actions.append({"id": call_id, "name": name, "arguments": arguments})
    return actions


def expand_tool_calls(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for index, action in enumerate(actions):
        if action.get("type") == "function" and isinstance(action.get("function"), dict):
            function = dict(action["function"])
            arguments = function.get("arguments", "{}")
            if not isinstance(arguments, str):
                function["arguments"] = json.dumps(arguments)
            expanded.append(
                {
                    "id": action.get("id") or f"call_{index}",
                    "type": "function",
                    "function": function,
                }
            )
            continue
        arguments = action.get("arguments") or {}
        if not isinstance(arguments, str):
            arguments = json.dumps(arguments)
        expanded.append(
            {
                "id": action.get("id") or f"call_{index}",
                "type": "function",
                "function": {
                    "name": action["name"],
                    "arguments": arguments,
                },
            }
        )
    return expanded


def for_llama_server(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """llama.cpp requires OpenAI tool-call shape, including type=function."""
    normalized: list[dict[str, Any]] = []
    for message in messages:
        role = message.get("role")
        if role == "assistant":
            tool_calls = message.get("tool_calls") or []
            item: dict[str, Any] = {"role": "assistant"}
            content = message.get("content")
            if tool_calls:
                item["tool_calls"] = expand_tool_calls(list(tool_calls))
                item["content"] = content if content else None
            else:
                item["content"] = content or ""
            normalized.append(item)
            continue
        if role == "tool":
            normalized.append(
                {
                    "role": "tool",
                    "tool_call_id": message.get("tool_call_id")
                    or message.get("id")
                    or "call_0",
                    "content": message.get("content") or "",
                }
            )
            continue
        normalized.append(dict(message))
    return normalized
