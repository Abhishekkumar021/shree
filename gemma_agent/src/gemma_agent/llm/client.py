from __future__ import annotations

from typing import Any, Sequence

from openai import OpenAI

from gemma_agent.config.settings import Settings
from gemma_agent.llm.messages import flatten_tool_calls, for_llama_server


class LlamaChatClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = OpenAI(
            base_url=settings.llama_openai_url,
            api_key=settings.llm_api_key,
            max_retries=0,
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
            "messages": for_llama_server(list(messages)),
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
        raw_calls = []
        if message.tool_calls:
            raw_calls = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments or "{}",
                    },
                }
                for call in message.tool_calls
            ]
        return {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": flatten_tool_calls(raw_calls),
        }
