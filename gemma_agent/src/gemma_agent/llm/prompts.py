from pathlib import Path

from gemma_agent.paths import SUBMISSION_DIR


def load_prompt(name: str) -> str:
    path = SUBMISSION_DIR / "prompts" / name
    return path.read_text(encoding="utf-8")


def default_system_prompt() -> str:
    path = Path(SUBMISSION_DIR / "prompts" / "system.md")
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        "You are a local software-engineering agent. Use tools to inspect the "
        "workspace, edit Python files, and run tests. Do not run arbitrary shell."
    )
