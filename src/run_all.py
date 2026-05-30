#!/usr/bin/env python3
"""Запуск всех заданий подряд."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run(args: list[str]) -> None:
    print("\n$", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    run([PYTHON, "src/collect_task1.py"])
    run([PYTHON, "src/scan_task2_ghsa.py"])
    run([PYTHON, "src/analyze_task3.py"])
    print("\nГотово. Итоговые файлы находятся в папке results/.")


if __name__ == "__main__":
    main()
