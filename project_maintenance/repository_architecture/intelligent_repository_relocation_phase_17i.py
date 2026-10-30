from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_semantic_knowledge_graph_phase_17h import (
    build_repository_semantic_knowledge_graph,
)

SCHEMA = "LEAF_INTELLIGENT_REPOSITORY_RELOCATION_PHASE_17I_V1"

CANONICAL_USER_ROOTS = {
    "LEAF_Designs/",
    "LEAF_Projects/",
    "LEAF_Reports/",
    "LEAF_Exports/",
}

SAFE_DEVELOPER_ROOTS = {
    "leaf_qt",
    "project_maintenance",
    "verification",
    "cea_integration",
}

NON_AUTHORITATIVE_ROOT_MARKERS = (
    "_leaf_repository_cleanup_candidates",
    "_external_repository_quarantine",
    "_leaf_archive",
    "_leaf_artifacts",
    "project_evidence",
)


def _top(path: str) -> str:
    return path.split("/", 1)[0] if path else ""


def _kind_from_path(path: str) -> str:
    suffix = Path(path).suffix.lower()
    name = Path(path).name.lower()

    if suffix == ".json":
        return "json"
    if suffix == ".py":
        return "python"
    if suffix in {".txt", ".md", ".rst"}:
        return "text"
    if "report" in name:
        return "report"
    return "unknown"


def _recommend_user_resource_destination(path: str, entry: dict[str, Any]) -> str | None:
    name = Path(path).name
    lower = name.lower()

    if lower.endswith(".json") and ("design" in lower or entry.get("semantic_domain") == "user_resource_domain"):
        return f"LEAF_Designs/{name}"

    if "project" in lower:
        return f"LEAF_Projects/{name}"

    if "report" in lower:
        return f"LEAF_Reports/{name}"

    if "export" in lower:
        return f"LEAF_Exports/{name}"

    return None


def _recommend_developer_destination(path: str, entry: dict[str, Any]) -> str | None:
    top = _top(path)
    if top in SAFE_DEVELOPER_ROOTS:
        return None

    role = str(entry.get("role") or "").lower()
    subsystem = str(entry.get("subsystem") or "").lower()
    name = Path(path).name

    if "gate" in role or "validation" in role:
        return f"project_maintenance/repository_architecture/{name}"

    if "repository" in subsystem:
        return f"project_maintenance/repository_architecture/{name}"

    if "qt" in subsystem or "ui" in subsystem:
        return f"leaf_qt/{name}"

    return None


def build_intelligent_relocation_plan(root: str | Path = ".") -> dict[str, Any]:
    semantic = build_repository_semantic_knowledge_graph(root)
    nodes = semantic.get("nodes", {})

    file_nodes = [
        node for node in nodes.values()
        if node.get("kind") == "file"
    ]

    recommendations: list[dict[str, Any]] = []
    protected: list[dict[str, Any]] = []

    for node in file_nodes:
        path = node["label"]
        top = _top(path)
        audience = node.get("audience")
        authority = node.get("authority")
        canonical = node.get("canonical_location")
        semantic_domain = node.get("semantic_domain")

        if top in SAFE_DEVELOPER_ROOTS and audience == "developer":
            protected.append({
                "path": path,
                "reason": "already_in_safe_developer_root",
            })
            continue

        if any(marker in path for marker in NON_AUTHORITATIVE_ROOT_MARKERS):
            destination = None

            if audience == "engineer_user":
                destination = _recommend_user_resource_destination(path, node)

            recommendations.append({
                "path": path,
                "current_root": top,
                "recommended_destination": destination,
                "recommendation_type": "migration_source_review",
                "execution_allowed": False,
                "requires_manual_review": True,
                "asset_kind": _kind_from_path(path),
                "audience": audience,
                "authority": authority,
                "semantic_domain": semantic_domain,
                "reason": "non_authoritative_history_or_artifact_location",
                "policy": "May be used as import, recovery, or migration source only. Do not automatically move.",
            })
            continue

        if audience == "engineer_user":
            destination = _recommend_user_resource_destination(path, node)

            if destination and not path.startswith(tuple(CANONICAL_USER_ROOTS)):
                recommendations.append({
                    "path": path,
                    "current_root": top,
                    "recommended_destination": destination,
                    "recommendation_type": "canonical_user_resource_relocation_candidate",
                    "execution_allowed": False,
                    "requires_manual_review": True,
                    "asset_kind": _kind_from_path(path),
                    "audience": audience,
                    "authority": authority,
                    "semantic_domain": semantic_domain,
                    "reason": "user_resource_outside_obvious_root_level_home",
                    "policy": "User resources should have one authoritative root-level location.",
                })
                continue

        developer_destination = _recommend_developer_destination(path, node)

        if developer_destination:
            recommendations.append({
                "path": path,
                "current_root": top,
                "recommended_destination": developer_destination,
                "recommendation_type": "developer_infrastructure_relocation_candidate",
                "execution_allowed": False,
                "requires_manual_review": True,
                "asset_kind": _kind_from_path(path),
                "audience": audience,
                "authority": authority,
                "semantic_domain": semantic_domain,
                "reason": "developer_file_outside_expected_developer_root",
                "policy": "Developer infrastructure should remain discoverable under developer-facing architecture roots.",
            })

    summary = {
        "semantic_graph_schema": semantic.get("schema"),
        "file_nodes_considered": len(file_nodes),
        "recommendations": len(recommendations),
        "protected_files": len(protected),
        "execution_allowed": False,
        "move_operations_created": 0,
        "delete_operations_created": 0,
        "archive_operations_created": 0,
        "manual_review_required": sum(1 for item in recommendations if item["requires_manual_review"]),
        "user_resource_candidates": sum(1 for item in recommendations if item["recommendation_type"] == "canonical_user_resource_relocation_candidate"),
        "developer_infrastructure_candidates": sum(1 for item in recommendations if item["recommendation_type"] == "developer_infrastructure_relocation_candidate"),
        "migration_source_review_candidates": sum(1 for item in recommendations if item["recommendation_type"] == "migration_source_review"),
    }

    return {
        "schema": SCHEMA,
        "phase": "17I",
        "feature": "INTELLIGENT_REPOSITORY_RELOCATION",
        "source_semantic_graph_schema": semantic.get("schema"),
        "design_principle": "Relocation intelligence must produce safe explainable dry-run plans before any file operation is allowed.",
        "safety_locks": {
            "move_allowed": False,
            "archive_allowed": False,
            "delete_allowed": False,
            "automatic_delete_allowed": False,
            "automatic_relocation_allowed": False,
            "deletion_started": False,
        },
        "summary": summary,
        "recommendations": sorted(recommendations, key=lambda item: (item["recommendation_type"], item["path"])),
        "protected_files_sample": protected[:100],
        "policy": {
            "developer_architecture_is_not_user_architecture": True,
            "one_authoritative_user_location": True,
            "quarantine_archive_and_artifact_locations_are_non_authoritative": True,
            "all_relocation_candidates_require_manual_review": True,
            "phase_17i_is_dry_run_only": True,
        },
    }


def write_intelligent_relocation_plan(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/phase_17i/intelligent_repository_relocation_plan_phase_17i.json",
) -> dict[str, Any]:
    plan = build_intelligent_relocation_plan(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return plan


if __name__ == "__main__":
    plan = write_intelligent_relocation_plan(".")
    summary = plan["summary"]

    print("LEAF_INTELLIGENT_REPOSITORY_RELOCATION_PHASE_17I")
    print(f"schema={plan['schema']}")
    print(f"source_semantic_graph_schema={plan['source_semantic_graph_schema']}")
    print(f"file_nodes_considered={summary['file_nodes_considered']}")
    print(f"recommendations={summary['recommendations']}")
    print(f"manual_review_required={summary['manual_review_required']}")
    print(f"execution_allowed={summary['execution_allowed']}")
    print(f"move_operations_created={summary['move_operations_created']}")
    print(f"delete_operations_created={summary['delete_operations_created']}")
