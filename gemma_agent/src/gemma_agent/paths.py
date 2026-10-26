from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PACKAGE_ROOT / "configs"
SUBMISSION_DIR = PACKAGE_ROOT / "submission"
DEFAULT_WORKSPACE = PACKAGE_ROOT / "workspace"
LOG_DIR = PACKAGE_ROOT / "logs"
