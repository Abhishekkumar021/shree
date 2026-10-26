from __future__ import annotations

import logging
import subprocess
import threading
import time
import urllib.error
import urllib.request
from types import SimpleNamespace

from gemma_agent.config.settings import Settings

logger = logging.getLogger("gemma_agent.llama")
server_logger = logging.getLogger("llama-server")

_llama_process: subprocess.Popen[str] | None = None


def _pump_output(stream) -> None:
    for line in iter(stream.readline, ""):
        line = line.rstrip()
        if line:
            server_logger.info(line)
    stream.close()


def start_llama_server(settings: Settings, state: SimpleNamespace | None = None) -> None:
    global _llama_process
    if _llama_process is not None and _llama_process.poll() is None:
        logger.info("llama-server already running")
        return

    for label, path in (
        ("executable", settings.llama_server),
        ("model", settings.model_path),
    ):
        if not path.is_file():
            raise FileNotFoundError(f"Llama server {label} not found at {path}")

    command = [
        str(settings.llama_server),
        "-m",
        str(settings.model_path),
        "-c",
        str(settings.llama_context),
        "-t",
        str(settings.llama_threads),
        "--jinja",
        "--host",
        settings.llama_host,
        "--port",
        str(settings.llama_port),
    ]
    logger.info("Starting llama-server: %s", " ".join(command))
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=settings.llama_server.parent,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    _llama_process = process
    if process.stdout is not None:
        threading.Thread(target=_pump_output, args=(process.stdout,), daemon=True).start()
    if state is not None:
        state.llama_process = process

    deadline = time.monotonic() + settings.llama_startup_timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError("llama-server exited during startup; see logs/agent.log")
        try:
            with urllib.request.urlopen(settings.llama_health_url, timeout=2) as response:
                if response.status == 200:
                    logger.info(
                        "llama-server is ready on %s:%s",
                        settings.llama_host,
                        settings.llama_port,
                    )
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(1)
    raise TimeoutError("llama-server was not ready in time; see logs/agent.log")


def stop_llama_server(state: SimpleNamespace | None = None) -> None:
    global _llama_process
    process = _llama_process
    if process is not None and process.poll() is None:
        logger.info("Stopping llama-server")
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            logger.warning("llama-server did not stop in time, killing")
            process.kill()
            process.wait()
    _llama_process = None
    if state is not None:
        state.llama_process = None
