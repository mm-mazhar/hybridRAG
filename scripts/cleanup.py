"""Remove local LanceDB and SQLite demo data (not source code)."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.settings import get_settings  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Delete local vector and memory data directories.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args()
    settings = get_settings()
    targets = [settings.vector_db_path, settings.memory_db_path]
    if not args.yes:
        print("Would remove:")
        for target in targets:
            print(f"  {target}")
        print("Re-run with --yes to delete.")
        return
    for target in targets:
        if target.is_file():
            target.unlink()
        elif target.is_dir():
            shutil.rmtree(target)
        print(f"Removed {target}")


if __name__ == "__main__":
    main()
