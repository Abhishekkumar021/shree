# from pathlib import Path
# import subprocess
# from dotenv import load_dotenv
# import os
# import logging
# import time
# import urllib
# from fastapi import FastAPI

# load_dotenv()

# LLAMA_SERVER = Path(os.getenv("LLAMA_SERVER", r"C:\llama\llama-server.exe"))

# MODEL_PATH = Path(os.getenv("MODEL_PATH", r"C:\llama\models\gemma-4-E4B_q4_0-it.gguf"))

# HOST = os.getenv("HOST", "127.0.0.1")
# PORT = int(os.getenv("PORT", 8080))
# LOG_FILE = Path(os.getenv("LOG_FILE", "/logs/llama-server.log"))


# llama_process = None


# def start_llama_server(app: FastAPI):
#     global llama_process

#     if not LLAMA_SERVER.is_file():
#         logging.error(f"Llama server executable not found at {LLAMA_SERVER}")
#         raise FileNotFoundError(f"Llama server executable not found at {LLAMA_SERVER}")

#     if not MODEL_PATH.is_file():
#         logging.error(f"Model file not found at {MODEL_PATH}")
#         raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

#     LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

#     command = [
#         str(LLAMA_SERVER),
#         "-m",
#         str(MODEL_PATH),
#         "-c",
#         "4096",
#         "-t",
#         "6",
#         "--jinja",
#         "--host",
#         HOST,
#         "--port",
#         str(PORT),
#     ]

#     log_handle = open(LOG_FILE, "a", encoding="utf-8")
#     try:
#         llama_process = subprocess.Popen(
#             command,
#             stdout=log_handle,
#             stderr=log_handle,
#             cwd=LLAMA_SERVER.parent,
#             text=True,
#         )
#     except Exception as e:
#         logging.error(f"Failed to start Llama server: {e}")
#         log_handle.close()
#         raise e

#     # The child process retains the log handle.
#     # Keep a reference so it can be closed during shutdown.

#     app.state.llama_log_handle = log_handle

#     print("Starting Llama server...")

#     deadline = time.monotonic() + 300  # Wait up to 5 minutes

#     while time.monotonic() < deadline:
#         if llama_process.poll() is not None:
#             raise RuntimeError(f"llama-server exited. Check {LOG_FILE}")

#         try:
#             with urllib.request.urlopen(
#                 f"http://{HOST}:{PORT}/health",
#                 timeout=2,
#             ) as response:
#                 if response.status == 200:
#                     print("Llama server is ready!")
#                     return
#         except (urllib.error.URLError, TimeoutError, OSError):
#             pass

#         time.sleep(1)

#     raise TimeoutError(
#         f"Llama server did not become ready within 5 minutes. " f"Check {LOG_FILE}"
#     )


# def stop_llama_server(app: FastAPI):
#     global llama_process

#     if llama_process and llama_process.poll() is None:
#         print("Stopping Llama server...")
#         llama_process.terminate()

#         try:
#             llama_process.wait(timeout=15)
#         except subprocess.TimeoutExpired:
#             print("Llama server did not terminate in time. Killing...")
#             llama_process.kill()
#             llama_process.wait()

#     llama_process = None

#     log_handle = getattr(app.state, "llama_log_handle", None)

#     if log_handle:
#         log_handle.close()
#         app.state.llama_log_handle = None


import logging
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

logger = logging.getLogger("bugloc.llama")
server_logger = logging.getLogger("llama-server")  # lines coming from the child process

LLAMA_SERVER = Path(os.getenv("LLAMA_SERVER", r"C:\llama\llama-server.exe"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", r"C:\llama\models\gemma-4-E4B_q4_0-it.gguf"))

HOST = os.getenv("LLAMA_HOST", "127.0.0.1")
PORT = int(os.getenv("LLAMA_PORT", 8080))

llama_process: subprocess.Popen | None = None


def _pump_output(stream) -> None:
    """Forward llama-server stdout/stderr lines into the central logger."""
    for line in iter(stream.readline, ""):
        line = line.rstrip()
        if line:
            server_logger.info(line)
    stream.close()


def start_llama_server(app: FastAPI) -> None:
    global llama_process

    for label, path in (("executable", LLAMA_SERVER), ("model", MODEL_PATH)):
        if not path.is_file():
            logger.error("Llama server %s not found at %s", label, path)
            raise FileNotFoundError(f"Llama server {label} not found at {path}")

    command = [
        str(LLAMA_SERVER),
        "-m",
        str(MODEL_PATH),
        "-c",
        "4096",
        "-t",
        "6",
        "--jinja",
        "--host",
        HOST,
        "--port",
        str(PORT),
    ]
    logger.info("Starting llama-server: %s", " ".join(command))

    try:
        llama_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # merge stderr into stdout
            cwd=LLAMA_SERVER.parent,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except Exception:
        logger.exception("Failed to start llama-server")
        raise

    threading.Thread(
        target=_pump_output, args=(llama_process.stdout,), daemon=True
    ).start()
    app.state.llama_process = llama_process

    deadline = time.monotonic() + 300  # model load can be slow
    while time.monotonic() < deadline:
        if llama_process.poll() is not None:
            raise RuntimeError("llama-server exited during startup, see logs/app.log")
        try:
            with urllib.request.urlopen(f"http://{HOST}:{PORT}/health", timeout=2) as r:
                if r.status == 200:
                    logger.info("llama-server is ready on %s:%s", HOST, PORT)
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            pass  # a 503 while the model loads also lands here
        time.sleep(1)

    raise TimeoutError("llama-server was not ready within 5 minutes, see logs/app.log")


def stop_llama_server(app: FastAPI) -> None:
    global llama_process

    if llama_process and llama_process.poll() is None:
        logger.info("Stopping llama-server")
        llama_process.terminate()
        try:
            llama_process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            logger.warning("llama-server did not stop in time, killing")
            llama_process.kill()
            llama_process.wait()

    llama_process = None
    app.state.llama_process = None
