from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
from bugloc.llm_server_config.llama import (
    start_llama_server,
    stop_llama_server,
    HOST,
    PORT,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        start_llama_server(app)
        yield
    finally:
        stop_llama_server(app)


app = FastAPI(
    title="Gemma AI Backend",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {
        "backend": "running",
        "gemma": (
            # "running" if llama_process and llama_process.poll() is None else "stopped"
            "running"
            if getattr(app.state, "llama_log_handle", None)
            else "stopped"
        ),
    }

