#!/usr/bin/env python3
"""Задача 1: сбор зависимостей TensorFlow v2.7.0 в result_task_1.json.

Скрипт поддерживает два режима:
1) offline/snapshot: использует подготовленный снимок зависимостей для TensorFlow v2.7.0;
2) repo: при наличии локально скачанного репозитория TensorFlow пытается найти файлы
   с зависимостями и извлечь Python-зависимости из setup.py/requirements*.txt.

Для учебной работы снимок сохранён в data/tensorflow_v2_7_dependencies.json,
чтобы итоговые результаты можно было воспроизвести без сетевого доступа.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT = PROJECT_ROOT / "data" / "tensorflow_v2_7_dependencies.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "result_task_1.json"

DEPENDENCY_FILES = [
    "tensorflow/tools/pip_package/setup.py",
    "requirements.txt",
    "requirements_lock_3_9.txt",
    "requirements_lock_3_10.txt",
]


def pypi_url(name: str, version: str) -> str:
    return f"https://pypi.org/project/{name}/{version}/"


def purl(name: str, version: str, ecosystem: str = "pypi") -> str:
    return f"pkg:{ecosystem}/{name.lower()}@{version}"


def normalize_package_name(name: str) -> str:
    return name.strip().replace("_", "-").lower()


def parse_requirement_line(line: str) -> tuple[str, str] | None:
    """Извлекает name/version из строки requirements вида name==1.2.3."""
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("-"):
        return None
    line = re.split(r"\s+#", line)[0].strip()
    match = re.match(r"([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(==|~=|>=|<=|>|<)\s*([A-Za-z0-9_.!+*-]+)", line)
    if not match:
        return None
    name, _op, version = match.groups()
    # Для нижней границы берём минимально зафиксированную версию как воспроизводимый снимок.
    return normalize_package_name(name), version.replace("*", "0")


def parse_setup_py(setup_py: Path) -> list[dict]:
    """Пытается вытащить REQUIRED_PACKAGES из setup.py без выполнения файла."""
    if not setup_py.exists():
        return []
    text = setup_py.read_text(encoding="utf-8", errors="ignore")
    deps: list[dict] = []

    # В разных версиях TensorFlow список может называться REQUIRED_PACKAGES или REQUIRED_PACKAGES + setup(... install_requires=...).
    list_match = re.search(r"REQUIRED_PACKAGES\s*=\s*(\[[\s\S]*?\])", text)
    if not list_match:
        list_match = re.search(r"install_requires\s*=\s*(\[[\s\S]*?\])", text)
    if list_match:
        try:
            raw_items = ast.literal_eval(list_match.group(1))
        except Exception:
            raw_items = []
        for item in raw_items:
            parsed = parse_requirement_line(str(item))
            if parsed:
                name, version = parsed
                deps.append({
                    "name": name,
                    "version": version,
                    "ecosystem": "pypi",
                    "url": pypi_url(name, version),
                    "purl": purl(name, version),
                    "source_file": str(setup_py),
                    "component_type": "direct_dependency",
                })
    return deps


def parse_requirement_files(repo: Path) -> list[dict]:
    deps: list[dict] = []
    for file in repo.rglob("requirements*.txt"):
        # Не берём test/dev requirements, чтобы не смешивать runtime и dev-зависимости.
        lowered = file.name.lower()
        if any(marker in lowered for marker in ["dev", "test", "ci"]):
            continue
        for line in file.read_text(encoding="utf-8", errors="ignore").splitlines():
            parsed = parse_requirement_line(line)
            if parsed:
                name, version = parsed
                deps.append({
                    "name": name,
                    "version": version,
                    "ecosystem": "pypi",
                    "url": pypi_url(name, version),
                    "purl": purl(name, version),
                    "source_file": str(file),
                    "component_type": "direct_dependency",
                })
    return deps


def unique_dependencies(items: Iterable[dict]) -> list[dict]:
    seen: dict[tuple[str, str, str], dict] = {}
    for item in items:
        key = (item["ecosystem"].lower(), normalize_package_name(item["name"]), item["version"])
        if key not in seen:
            item["name"] = normalize_package_name(item["name"])
            seen[key] = item
    return sorted(seen.values(), key=lambda x: (x["ecosystem"], x["name"]))


def collect_from_snapshot(snapshot: Path) -> list[dict]:
    with snapshot.open("r", encoding="utf-8") as f:
        return json.load(f)


def collect_from_repo(repo: Path) -> list[dict]:
    items: list[dict] = []
    setup_py = repo / "tensorflow" / "tools" / "pip_package" / "setup.py"
    items.extend(parse_setup_py(setup_py))
    items.extend(parse_requirement_files(repo))
    if not items:
        raise SystemExit("Не удалось найти зависимости в репозитории. Используйте --snapshot.")
    return unique_dependencies(items)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect dependencies for task 1")
    parser.add_argument("--repo", type=Path, help="Путь к локальному репозиторию tensorflow v2.7.0")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT, help="Файл со снимком зависимостей")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Куда сохранить result_task_1.json")
    args = parser.parse_args()

    if args.repo:
        dependencies = collect_from_repo(args.repo)
    else:
        dependencies = collect_from_snapshot(args.snapshot)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dependencies, ensure_ascii=False, indent=2), encoding="utf-8")
    ecosystems: dict[str, int] = {}
    for dep in dependencies:
        ecosystems[dep["ecosystem"]] = ecosystems.get(dep["ecosystem"], 0) + 1
    print(f"Saved {len(dependencies)} components to {args.output}")
    print("Ecosystems:", ecosystems)


if __name__ == "__main__":
    main()
