from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from core.architecture.io import write_json_artifact
from core.architecture.repository_metadata import (
    build_repository_metadata,
)

SCHEMA = "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1"

IGNORED_PARTS = {
    "LEAF_Minimal_Source", "LEAF_Regen_Only", "LEAF_Source", "LEAF_UPLOAD",
    "artifacts", "exports", "backups", "_external_repository_quarantine",
}

SUBSYSTEM_RULES = (
    ("regen", "REGEN"), ("material", "MATERIALS"), ("coating", "COATINGS"),
    ("coolant", "COOLANT"), ("benchmark", "BENCHMARKING"),
    ("validation", "VALIDATION"), ("report", "REPORTING"),
    ("history", "HISTORY"), ("optimisation", "OPTIMISATION"),
    ("optimization", "OPTIMISATION"), ("candidate", "CANDIDATE_SELECTION"),
    ("viewer", "UI_VIEWER"), ("window", "UI"), ("panel", "UI"),
    ("graph", "UI_GRAPHING"), ("solver", "SOLVER"), ("registry", "REGISTRY"),
    ("gate", "GATE"), ("audit", "AUDIT"), ("test_", "TESTS"),
)

ROLE_RULES = (
    ("test_", "TEST_CODE"), ("_test", "TEST_CODE"),
    ("audit", "AUDIT_OWNER"), ("gate", "MASTER_GATE"),
    ("owner", "OWNER"), ("registry", "REGISTRY"),
    ("report", "REPORT_OWNER"), ("validation", "VALIDATION_OWNER"),
    ("solver", "SOLVER"), ("controller", "CONTROLLER"),
    ("panel", "UI_PANEL"), ("window", "UI_WINDOW"),
    ("viewer", "UI_VIEWER"), ("database", "DATABASE"),
    ("backup", "BACKUP_OR_LEGACY"), ("phase", "PHASE_ARTIFACT"),
)


def _classify(path: str, rules, default: str) -> str:
    lowered = path.lower()
    return next((value for token, value in rules if token in lowered), default)


def _entry(item: dict[str, Any]) -> dict[str, Any]:
    path = item["path"]
    return {
        "path": path,
        "subsystem": _classify(path, SUBSYSTEM_RULES, "UNCLASSIFIED"),
        "role": (
            "TEST_CODE"
            if Path(path).name.lower().startswith("test_")
            else _classify(path, ROLE_RULES, "MODULE_CODE")
        ),
        "classes": list(item.get("classes", [])),
        "functions": list(item.get("functions", [])),
        "imports": list(item.get("imports", [])),
        "from_imports": [],
        "line_count": int(item.get("line_count", 0)),
        "ast_parse_status": item.get("ast_parse_status", "NOT_PYTHON"),
        "ast_error": item.get("ast_error"),
    }


def _duplicates(entries: list[dict[str, Any]], key: str) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for entry in entries:
        for name in entry[key]:
            seen.setdefault(name, []).append(entry["path"])
    return {name: paths for name, paths in sorted(seen.items()) if len(paths) > 1}


def build_repository_architecture_index(root: str | Path = ".") -> dict[str, Any]:
    root_path = Path(root).resolve()
    metadata = build_repository_metadata(root_path)

    entries = [
        _entry(item)
        for item in metadata["files"]
        if item.get("suffix") == ".py"
        and not set(Path(item["path"]).parts).intersection(IGNORED_PARTS)
    ]

    subsystems = Counter(item["subsystem"] for item in entries)
    roles = Counter(item["role"] for item in entries)
    failures = [item for item in entries if item["ast_parse_status"] != "PASS"]

    return {
        "schema": SCHEMA,
        "root": str(root_path),
        "summary": {
            "python_files": len(entries),
            "classes": sum(len(item["classes"]) for item in entries),
            "functions": sum(len(item["functions"]) for item in entries),
            "imports": sum(len(item["imports"]) for item in entries),
            "ast_parse_failures": len(failures),
            "subsystem_counts": dict(sorted(subsystems.items())),
            "role_counts": dict(sorted(roles.items())),
        },
        "files": entries,
        "duplicate_class_names": _duplicates(entries, "classes"),
        "duplicate_function_names": _duplicates(entries, "functions"),
        "ast_parse_failures": failures,
    }


def write_repository_architecture_index(
    root: str | Path = ".",
    output_path: str | Path = "artifacts/repository_architecture_index.json",
) -> dict[str, Any]:
    index = build_repository_architecture_index(root)
    write_json_artifact(index, Path(output_path))
    return index


def build_repository_architecture_report(index: dict[str, Any]) -> str:
    summary = index["summary"]
    lines = [
        "LEAF REPOSITORY ARCHITECTURE INDEX",
        "=================================",
        f"schema={index['schema']}",
        f"python_files={summary['python_files']}",
        f"classes={summary['classes']}",
        f"functions={summary['functions']}",
        f"imports={summary['imports']}",
        f"ast_parse_failures={summary['ast_parse_failures']}",
        "",
        "SUBSYSTEM COUNTS",
        "----------------",
        *(f"{name}: {count}" for name, count in summary["subsystem_counts"].items()),
        "",
        "ROLE COUNTS",
        "-----------",
        *(f"{name}: {count}" for name, count in summary["role_counts"].items()),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    result = write_repository_architecture_index(".")
    print(build_repository_architecture_report(result))
    if result["summary"]["ast_parse_failures"]:
        raise SystemExit(1)
