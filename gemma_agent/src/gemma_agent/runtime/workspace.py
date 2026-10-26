from pathlib import Path

from gemma_agent.config.settings import Settings


def prepare_workspace(settings: Settings) -> Path:
    workspace = settings.gemma_agent_workspace
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace.resolve()
