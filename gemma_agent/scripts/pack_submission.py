"""Zip the ADK-style submission tree for Kaggle."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"


def pack(output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in SUBMISSION.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(SUBMISSION))
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=ROOT / "dist" / "submission.zip",
    )
    args = parser.parse_args()
    packed = pack(args.output)
    print(packed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
