from __future__ import annotations

import json
from typing import Any, Sequence

from openai import OpenAI

from gemma_agent.config.settings import Settings

SYSTEM_PROMPT_PATH = "submission/prompts/system.md"


class LlamaChatClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = OpenAI(
            base_url=settings.llama_openai_url,
            api_key=settings.llm_api_key,
        )

    def chat(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.settings.llm_model,
            "messages": list(messages),
            "temperature": (
                self.settings.llm_temperature if temperature is None else temperature
            ),
            "max_tokens": self.settings.llm_max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        response = self._client.chat.completions.create(**kwargs)
        message = response.choices[0].message
        tool_calls = []
        if message.tool_calls:
            for call in message.tool_calls:
                arguments = call.function.arguments or "{}"
                try:
                    parsed = json.loads(arguments)
                except json.JSONDecodeError:
                    parsed = {"_raw": arguments}
                tool_calls.append(
                    {
                        "id": call.id,
                        "name": call.function.name,
                        "arguments": parsed,
                    }
                )
        return {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": tool_calls,
        }
