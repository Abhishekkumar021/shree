from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from gemma_agent.agent.loop import AgentLoop
from gemma_agent.config.settings import get_settings
from gemma_agent.llm.llama_server import start_llama_server, stop_llama_server
from gemma_agent.logsetup import setup_logging
from gemma_agent.runtime.workspace import prepare_workspace


class RunRequest(BaseModel):
    issue: str = Field(min_length=1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    settings = get_settings()
    prepare_workspace(settings)
    if settings.gemma_agent_manage_llama:
        start_llama_server(settings, app.state)
    try:
        yield
    finally:
        if settings.gemma_agent_manage_llama:
            stop_llama_server(app.state)


app = FastAPI(title="Gemma 4 Developer Agent", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    process = getattr(app.state, "llama_process", None)
    llama = "running" if process is not None and process.poll() is None else "stopped"
    return {"backend": "running", "llama": llama}


@app.post("/v1/agent/run")
def run_agent(payload: RunRequest) -> dict[str, object]:
    settings = get_settings()
    try:
        result = AgentLoop(settings).run(payload.issue)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "done": result.done,
        "steps": result.steps,
        "patch": result.patch,
        "error": result.error,
    }
