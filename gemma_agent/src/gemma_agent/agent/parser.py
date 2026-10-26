from __future__ import annotations

import json
from typing import Any


def extract_actions(content: str) -> list[dict[str, Any]]:
    """Parse tool calls from a small local model that may not emit native tools."""
    actions: list[dict[str, Any]] = []
    for payload in _json_objects(content or ""):
        name = payload.get("tool") or payload.get("name")
        arguments = payload.get("arguments") or payload.get("args") or {}
        if isinstance(name, str) and isinstance(arguments, dict):
            actions.append({"name": name, "arguments": arguments})
    return actions


def _json_objects(text: str) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    decoder = json.JSONDecoder()
    index = 0
    length = len(text)
    while index < length:
        start = text.find("{", index)
        if start < 0:
            break
        try:
            payload, end = decoder.raw_decode(text, start)
        except json.JSONDecodeError:
            index = start + 1
            continue
        if isinstance(payload, dict):
            objects.append(payload)
        index = start + max(end - start, 1)
    return objects
