#!/usr/bin/env python3
"""Задача 3: таблица по уязвимым зависимостям."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "results" / "result_task_2.json"
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "results" / "result_task_3.json"
DEFAULT_OUTPUT_MD = PROJECT_ROOT / "results" / "result_task_3_table.md"

SEVERITIES = ["CRITICAL", "HIGH", "MODERATE", "LOW", "UNKNOWN"]


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def strategy_for(item: dict) -> str:
    count = len(item["vulnerabilities"])
    secure = item.get("secure_version")
    if not count:
        return "Действия не требуются."
    if secure:
        return f"Обновить до >= {secure}; затем тесты и фиксация lock-файла."
    return "Проверить GHSA вручную и заменить/обновить пакет до ближайшей безопасной версии."


def build_rows(items: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for item in items:
        vulnerabilities = item.get("vulnerabilities", [])
        if not vulnerabilities:
            continue
        severity_counter = Counter(v.get("severity", "UNKNOWN").upper() for v in vulnerabilities)
        row = {
            "name": item["name"],
            "version": item["version"],
            "ecosystem": item["ecosystem"],
            "total_vulnerabilities": len(vulnerabilities),
            "critical": severity_counter.get("CRITICAL", 0),
            "high": severity_counter.get("HIGH", 0),
            "moderate": severity_counter.get("MODERATE", 0),
            "low": severity_counter.get("LOW", 0),
            "unknown": severity_counter.get("UNKNOWN", 0),
            "secure_version": item.get("secure_version"),
            "recommended_strategy": strategy_for(item),
        }
        rows.append(row)
    rows.sort(key=lambda x: (x["total_vulnerabilities"], x["critical"], x["high"]), reverse=True)
    return rows


def write_markdown(path: Path, rows: list[dict]) -> None:
    lines = [
        "| Зависимость | Версия | Экосистема | Всего | Critical | High | Moderate | Low | Unknown | Безопасная версия | Рекомендуемая стратегия |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | {row['version']} | {row['ecosystem']} | {row['total_vulnerabilities']} | "
            f"{row['critical']} | {row['high']} | {row['moderate']} | {row['low']} | {row['unknown']} | "
            f"{row['secure_version']} | {row['recommended_strategy']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze vulnerabilities for task 3")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    args = parser.parse_args()

    items = read_json(args.input)
    rows = build_rows(items)
    write_json(args.output_json, rows)
    write_markdown(args.output_md, rows)
    print(f"Saved {len(rows)} vulnerable dependency rows")


if __name__ == "__main__":
    main()
