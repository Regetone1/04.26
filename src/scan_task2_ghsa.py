#!/usr/bin/env python3
"""Задача 2: проверка зависимостей через GitHub Security Advisory GraphQL API.

По умолчанию используется офлайн-снимок для воспроизводимого результата.
Для реального запроса к GHSA задайте переменную окружения GITHUB_TOKEN и флаг --online.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import requests
from packaging.version import Version, InvalidVersion

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "results" / "result_task_1.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "results" / "result_task_2.json"
DEFAULT_OFFLINE = PROJECT_ROOT / "data" / "offline_ghsa_tensorflow_v2_7.json"

GHSA_ECOSYSTEM = {
    "pypi": "PIP",
    "npm": "NPM",
    "maven": "MAVEN",
    "nuget": "NUGET",
    "go": "GO",
    "rubygems": "RUBYGEMS",
}

QUERY = """
query($ecosystem: SecurityAdvisoryEcosystem!, $package: String!, $first: Int!) {
  securityAdvisories(first: $first, ecosystem: $ecosystem, package: $package) {
    nodes {
      ghsaId
      summary
      severity
      permalink
      vulnerabilities(first: 30) {
        nodes {
          package { name ecosystem }
          vulnerableVersionRange
          firstPatchedVersion { identifier }
        }
      }
    }
  }
}
"""


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_version(value: str) -> Version:
    try:
        return Version(value)
    except InvalidVersion:
        # Упрощение для rc/dev версий: оставляем только числовую часть.
        cleaned = "".join(ch if ch.isdigit() or ch == "." else "" for ch in value).strip(".") or "0"
        return Version(cleaned)


def is_in_range(version: str, vulnerable_range: str) -> bool:
    """Минимальная проверка semver-диапазонов вида '<2.7.2' или '>=2.7.0, <2.7.1'."""
    v = safe_version(version)
    checks = [part.strip() for part in vulnerable_range.split(",") if part.strip()]
    if not checks:
        return False
    for part in checks:
        if part.startswith(">="):
            if not (v >= safe_version(part[2:].strip())):
                return False
        elif part.startswith("<="):
            if not (v <= safe_version(part[2:].strip())):
                return False
        elif part.startswith(">"):
            if not (v > safe_version(part[1:].strip())):
                return False
        elif part.startswith("<"):
            if not (v < safe_version(part[1:].strip())):
                return False
        elif part.startswith("="):
            if not (v == safe_version(part[1:].strip())):
                return False
    return True


def max_version(versions: list[str]) -> str | None:
    versions = [v for v in versions if v]
    if not versions:
        return None
    return str(max((safe_version(v) for v in versions)))


def query_ghsa(ecosystem: str, package: str, token: str, first: int = 100) -> list[dict]:
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"ecosystem": ecosystem, "package": package, "first": first}},
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        timeout=40,
    )
    response.raise_for_status()
    payload = response.json()
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["securityAdvisories"]["nodes"]


def online_vulnerabilities(dep: dict, token: str) -> list[dict]:
    ecosystem = GHSA_ECOSYSTEM.get(dep["ecosystem"].lower())
    if not ecosystem:
        return []
    nodes = query_ghsa(ecosystem, dep["name"], token)
    vulnerabilities: list[dict] = []
    for node in nodes:
        for vuln in node.get("vulnerabilities", {}).get("nodes", []):
            package = vuln.get("package") or {}
            if package.get("name", "").lower() != dep["name"].lower():
                continue
            vulnerable_range = vuln.get("vulnerableVersionRange") or ""
            patched = (vuln.get("firstPatchedVersion") or {}).get("identifier")
            if is_in_range(dep["version"], vulnerable_range):
                vulnerabilities.append({
                    "name": node["ghsaId"],
                    "title": node.get("summary") or "",
                    "severity": node.get("severity", "UNKNOWN"),
                    "vulnerable_range": vulnerable_range,
                    "first_patched_version": patched,
                    "url": node.get("permalink"),
                })
    return vulnerabilities


def offline_vulnerabilities(dep: dict, offline_db: dict) -> list[dict]:
    advisories = offline_db.get(dep["name"].lower(), [])
    return [adv for adv in advisories if is_in_range(dep["version"], adv["vulnerable_range"])]


def enrich_dependency(dep: dict, vulnerabilities: list[dict]) -> dict:
    result = {k: dep[k] for k in ["name", "version", "ecosystem", "url", "purl"]}
    result["vulnerabilities"] = vulnerabilities
    result["secure_version"] = max_version([v.get("first_patched_version") for v in vulnerabilities])
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan result_task_1.json with GHSA")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--offline-db", type=Path, default=DEFAULT_OFFLINE)
    parser.add_argument("--online", action="store_true", help="Запросить GitHub GraphQL API вместо offline-снимка")
    args = parser.parse_args()

    deps = read_json(args.input)
    offline_db = read_json(args.offline_db)
    token = os.environ.get("GITHUB_TOKEN")
    if args.online and not token:
        raise SystemExit("Для режима --online нужна переменная GITHUB_TOKEN")

    result = []
    for dep in deps:
        if args.online:
            vulns = online_vulnerabilities(dep, token)  # type: ignore[arg-type]
        else:
            vulns = offline_vulnerabilities(dep, offline_db)
        result.append(enrich_dependency(dep, vulns))

    write_json(args.output, result)
    vulnerable = sum(1 for item in result if item["vulnerabilities"])
    total_vulns = sum(len(item["vulnerabilities"]) for item in result)
    print(f"Saved {len(result)} components to {args.output}")
    print(f"Vulnerable components: {vulnerable}; vulnerabilities: {total_vulns}")


if __name__ == "__main__":
    main()
