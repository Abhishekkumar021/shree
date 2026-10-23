import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)  # logging_config.py -> bugloc -> src -> Gemma-4
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "app.log"

_configured = False


def setup_logging(level=logging.INFO):
    global _configured
    if _configured:
        return
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    file_h = RotatingFileHandler(
        LOG_FILE, maxBytes=10_000_000, backupCount=5, encoding="utf-8"
    )
    file_h.setFormatter(fmt)
    console_h = logging.StreamHandler()
    console_h.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [file_h, console_h]

    # make uvicorn use the same handlers instead of its own
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers.clear()
        lg.propagate = True

    _configured = True
