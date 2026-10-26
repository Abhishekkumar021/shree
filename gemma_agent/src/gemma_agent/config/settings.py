from __future__ import annotations

import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from gemma_agent.paths import CONFIG_DIR, DEFAULT_WORKSPACE, PACKAGE_ROOT

load_dotenv(PACKAGE_ROOT / ".env")


class Settings:
    def __init__(self, **overrides: Any) -> None:
        workspace = Path(
            overrides.get(
                "gemma_agent_workspace",
                os.getenv("GEMMA_AGENT_WORKSPACE", str(DEFAULT_WORKSPACE)),
            )
        )
        if not workspace.is_absolute():
            workspace = (PACKAGE_ROOT / workspace).resolve()

        self.llama_server = Path(
            os.getenv("LLAMA_SERVER", r"C:\llama\llama-server.exe")
        )
        self.model_path = Path(
            os.getenv("MODEL_PATH", r"C:\llama\models\gemma-4-E4B_q4_0-it.gguf")
        )
        self.llama_host = os.getenv("LLAMA_HOST", "127.0.0.1")
        self.llama_port = int(os.getenv("LLAMA_PORT", "8080"))
        self.llama_context = int(os.getenv("LLAMA_CONTEXT", "4096"))
        self.llama_threads = int(os.getenv("LLAMA_THREADS", "6"))
        self.llama_startup_timeout = int(os.getenv("LLAMA_STARTUP_TIMEOUT", "300"))
        self.gemma_agent_manage_llama = _as_bool(
            os.getenv("GEMMA_AGENT_MANAGE_LLAMA", "true")
        )

        self.llm_base_url = os.getenv("LLM_BASE_URL", "http://127.0.0.1:8080/v1")
        self.llm_api_key = os.getenv("LLM_API_KEY", "local")
        self.llm_model = os.getenv("LLM_MODEL", "gemma-4-e4b-it")
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.llm_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2048"))

        self.gemma_agent_workspace = workspace
        self.gemma_agent_max_steps = int(os.getenv("GEMMA_AGENT_MAX_STEPS", "24"))
        self.gemma_agent_task_timeout = int(os.getenv("GEMMA_AGENT_TASK_TIMEOUT", "600"))
        self.shell_timeout_seconds = int(os.getenv("SHELL_TIMEOUT_SECONDS", "30"))
        self.test_timeout_seconds = int(os.getenv("TEST_TIMEOUT_SECONDS", "120"))
        self.max_output_bytes = int(os.getenv("MAX_OUTPUT_BYTES", "200000"))

        for key, value in overrides.items():
            setattr(self, key, value)
        if not Path(self.gemma_agent_workspace).is_absolute():
            self.gemma_agent_workspace = (
                PACKAGE_ROOT / self.gemma_agent_workspace
            ).resolve()
        else:
            self.gemma_agent_workspace = Path(self.gemma_agent_workspace).resolve()

    @property
    def llama_health_url(self) -> str:
        return f"http://{self.llama_host}:{self.llama_port}/health"

    @property
    def llama_openai_url(self) -> str:
        return self.llm_base_url.rstrip("/")


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_toml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Missing config: {path}")
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Config {path} must be a mapping")
    return data


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
