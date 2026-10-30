from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_dependency_ownership_graph import (
    build_dependency_ownership_graph,
)

SCHEMA = "LEAF_REPOSITORY_ARCHITECTURE_VALIDATION_V1"


PROTECTED_EXCLUDED_PREFIXES = (
    "_leaf_archive/",
    "_leaf_artifacts/",
    "_external_repository_quarantine/",
)


def is_historical_or_generated(path: str) -> bool:
    return path.startswith(PROTECTED_EXCLUDED_PREFIXES)


def validate_no_generated_runtime_files(graph: dict[str, Any]) -> list[dict[str, str]]:
    issues = []

    for path, meta in graph["files"].items():
        if is_historical_or_generated(path) and meta.get("status") == "production_candidate":
            issues.append({
                "severity": "ERROR",
                "rule": "generated_or_historical_file_marked_runtime",
                "path": path,
                "message": "Generated, archived, or quarantined paths must not be treated as production runtime files.",
            })

    return issues


def validate_layer_path_alignment(graph: dict[str, Any]) -> list[dict[str, str]]:
    issues = []

    for path, meta in graph["files"].items():
        layer = meta.get("layer")

        if path.startswith("leaf_qt/") and layer != "runtime":
            issues.append({
                "severity": "ERROR",
                "rule": "leaf_qt_file_not_runtime_layer",
                "path": path,
                "message": "Files under leaf_qt should be classified as runtime.",
            })

        if path.startswith("project_maintenance/") and layer != "development":
            issues.append({
                "severity": "ERROR",
                "rule": "project_maintenance_file_not_development_layer",
                "path": path,
                "message": "Files under project_maintenance should be classified as development.",
            })

    return issues


def validate_owner_presence(graph: dict[str, Any]) -> list[dict[str, str]]:
    issues = []

    for path, meta in graph["files"].items():
        owner = meta.get("owner")
        if not owner or owner == "unclassified":
            issues.append({
                "severity": "WARN",
                "rule": "file_owner_unclassified",
                "path": path,
                "message": "File has no confident architectural owner yet.",
            })

    return issues


def validate_subsystem_presence(graph: dict[str, Any]) -> list[dict[str, str]]:
    issues = []

    for path, meta in graph["files"].items():
        subsystem = meta.get("subsystem")
        if not subsystem or subsystem == "unclassified":
            issues.append({
                "severity": "WARN",
                "rule": "file_subsystem_unclassified",
                "path": path,
                "message": "File has no confident subsystem classification yet.",
            })

    return issues


def validate_runtime_to_development_dependencies(graph: dict[str, Any]) -> list[dict[str, str]]:
    issues = []
    files = graph["files"]

    for edge in graph["dependency_edges"]:
        source = files.get(edge["from"], {})
        target = files.get(edge["to"], {})

        if source.get("layer") == "runtime" and target.get("layer") == "development":
            issues.append({
                "severity": "ERROR",
                "rule": "runtime_imports_development_tooling",
                "path": edge["from"],
                "target": edge["to"],
                "message": "Runtime code must not depend on project maintenance tooling.",
            })

    return issues


def validate_test_files_not_production_candidates(graph: dict[str, Any]) -> list[dict[str, str]]:
    issues = []

    for path, meta in graph["files"].items():
        name = Path(path).name.lower()
        if name.startswith("test_") and meta.get("status") == "production_candidate":
            issues.append({
                "severity": "ERROR",
                "rule": "test_file_marked_production_candidate",
                "path": path,
                "message": "Test files must not be treated as production candidates.",
            })

    return issues


def validate_architecture(graph: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []

    checks = [
        validate_no_generated_runtime_files,
        validate_layer_path_alignment,
        validate_owner_presence,
        validate_subsystem_presence,
        validate_runtime_to_development_dependencies,
        validate_test_files_not_production_candidates,
    ]

    for check in checks:
        issues.extend(check(graph))

    error_count = sum(1 for issue in issues if issue["severity"] == "ERROR")
    warning_count = sum(1 for issue in issues if issue["severity"] == "WARN")

    return {
        "schema": SCHEMA,
        "graph_schema": graph["schema"],
        "database_schema": graph["database_schema"],
        "metadata_schema": graph["metadata_schema"],
        "passed": error_count == 0,
        "summary": {
            "file_nodes": graph["summary"]["file_nodes"],
            "owner_nodes": graph["summary"]["owner_nodes"],
            "subsystem_nodes": graph["summary"]["subsystem_nodes"],
            "resolved_dependency_edges": graph["summary"]["resolved_dependency_edges"],
            "error_count": error_count,
            "warning_count": warning_count,
            "issue_count": len(issues),
        },
        "issues": issues,
    }


def build_architecture_validation(root: str | Path = ".") -> dict[str, Any]:
    graph = build_dependency_ownership_graph(root)
    return validate_architecture(graph)


def write_architecture_validation(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/repository_architecture_validation_v1.json",
) -> dict[str, Any]:
    validation = build_architecture_validation(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    return validation


if __name__ == "__main__":
    validation = write_architecture_validation(".")
    summary = validation["summary"]

    print("LEAF_REPOSITORY_ARCHITECTURE_VALIDATION")
    print(f"schema={validation['schema']}")
    print(f"passed={validation['passed']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"resolved_dependency_edges={summary['resolved_dependency_edges']}")
    print(f"errors={summary['error_count']}")
    print(f"warnings={summary['warning_count']}")

    if not validation["passed"]:
        raise SystemExit(1)
