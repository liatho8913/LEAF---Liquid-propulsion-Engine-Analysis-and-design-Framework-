from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_dependency_ownership_graph import (
    build_dependency_ownership_graph,
)

SCHEMA = "LEAF_REPOSITORY_OWNERSHIP_GRAPH_PHASE_17F_V1"

USER_RESOURCE_ROOTS = {
    "LEAF_Designs": "authoritative engineering design storage",
    "LEAF_Projects": "authoritative engineering project storage",
    "LEAF_Reports": "user-facing engineering reports",
    "LEAF_Exports": "user-facing exported files",
}

DEVELOPER_ROOTS = {
    "leaf_qt": "runtime application source",
    "project_maintenance": "developer maintenance and architecture source",
    "verification": "developer verification source",
    "cea_integration": "engineering calculation integration source",
}

GENERATED_ROOTS = {
    "_leaf_artifacts": "generated repository and validation artifacts",
    "artifacts": "generated or historical phase artifacts",
    "project_evidence": "generated evidence and certificates",
}

HISTORY_ROOTS = {
    "_leaf_archive": "archived historical repository material",
    "_external_repository_quarantine": "external or quarantined repository material",
    "_leaf_repository_cleanup_candidates": "non-authoritative cleanup candidate staging",
}


def top_level(path: str) -> str:
    return path.split("/", 1)[0] if path else ""


def classify_audience(path: str) -> str:
    root = top_level(path)
    if root in USER_RESOURCE_ROOTS:
        return "engineer_user"
    if root in DEVELOPER_ROOTS:
        return "developer"
    if root in GENERATED_ROOTS:
        return "generated"
    if root in HISTORY_ROOTS:
        return "repository_history"
    return "shared_or_unclassified"


def classify_visibility(path: str) -> str:
    audience = classify_audience(path)
    if audience == "engineer_user":
        return "user_visible"
    if audience == "developer":
        return "developer_internal"
    if audience == "generated":
        return "generated_internal"
    if audience == "repository_history":
        return "archive_or_quarantine_internal"
    return "unclassified_visibility"


def classify_lifecycle(path: str) -> str:
    audience = classify_audience(path)
    if audience == "engineer_user":
        return "active_user_resource"
    if audience == "developer":
        return "active_developer_infrastructure"
    if audience == "generated":
        return "generated_artifact"
    if audience == "repository_history":
        return "historical_or_recovery_source"
    return "unclassified_lifecycle"


def classify_authority(path: str) -> str:
    audience = classify_audience(path)
    if audience in {"engineer_user", "developer"}:
        return "canonical"
    if audience in {"generated", "repository_history"}:
        return "non_authoritative_reference"
    return "authority_unknown"


def canonical_location(path: str) -> str:
    root = top_level(path)
    if root in USER_RESOURCE_ROOTS:
        return f"{root}/"
    if root in DEVELOPER_ROOTS:
        return path
    if root in GENERATED_ROOTS:
        return "generated_artifacts_not_authoritative"
    if root in HISTORY_ROOTS:
        return "history_recovery_or_migration_source_not_authoritative"
    return "unclassified"


@dataclass(frozen=True)
class ResourceRootRecord:
    root: str
    description: str
    audience: str
    visibility: str
    authority: str
    expected: bool
    present: bool
    file_count: int


def build_resource_root_records(files: dict[str, Any]) -> dict[str, dict[str, Any]]:
    counts: dict[str, int] = {}
    for path in files:
        counts[top_level(path)] = counts.get(top_level(path), 0) + 1

    records: dict[str, ResourceRootRecord] = {}

    for root, description in USER_RESOURCE_ROOTS.items():
        records[root] = ResourceRootRecord(root, description, "engineer_user", "user_visible", "canonical_user_resource_location", True, counts.get(root, 0) > 0, counts.get(root, 0))

    for root, description in DEVELOPER_ROOTS.items():
        records[root] = ResourceRootRecord(root, description, "developer", "developer_internal", "canonical_developer_location", True, counts.get(root, 0) > 0, counts.get(root, 0))

    for root, description in GENERATED_ROOTS.items():
        records[root] = ResourceRootRecord(root, description, "generated", "generated_internal", "non_authoritative_reference", False, counts.get(root, 0) > 0, counts.get(root, 0))

    for root, description in HISTORY_ROOTS.items():
        records[root] = ResourceRootRecord(root, description, "repository_history", "archive_or_quarantine_internal", "non_authoritative_recovery_or_migration_source", False, counts.get(root, 0) > 0, counts.get(root, 0))

    return {key: asdict(value) for key, value in sorted(records.items())}


def enrich_file_nodes(files: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    enriched = {}
    for path, meta in files.items():
        item = dict(meta)
        item.update({
            "top_level_root": top_level(path),
            "audience": classify_audience(path),
            "visibility": classify_visibility(path),
            "lifecycle": classify_lifecycle(path),
            "authority": classify_authority(path),
            "canonical_location": canonical_location(path),
        })
        enriched[path] = item
    return enriched


def build_repository_ownership_graph(root: str | Path = ".") -> dict[str, Any]:
    base = build_dependency_ownership_graph(root)
    files = enrich_file_nodes(base["files"])
    resource_roots = build_resource_root_records(files)

    audience_counts = {}
    visibility_counts = {}
    lifecycle_counts = {}
    authority_counts = {}

    for meta in files.values():
        audience_counts[meta["audience"]] = audience_counts.get(meta["audience"], 0) + 1
        visibility_counts[meta["visibility"]] = visibility_counts.get(meta["visibility"], 0) + 1
        lifecycle_counts[meta["lifecycle"]] = lifecycle_counts.get(meta["lifecycle"], 0) + 1
        authority_counts[meta["authority"]] = authority_counts.get(meta["authority"], 0) + 1

    user_assets = sorted(path for path, meta in files.items() if meta["audience"] == "engineer_user")
    developer_assets = sorted(path for path, meta in files.items() if meta["audience"] == "developer")
    non_authoritative_assets = sorted(path for path, meta in files.items() if meta["authority"] == "non_authoritative_reference")

    return {
        "schema": SCHEMA,
        "base_graph_schema": base["schema"],
        "database_schema": base["database_schema"],
        "metadata_schema": base["metadata_schema"],
        "phase": "17F",
        "feature": "REPOSITORY_OWNERSHIP_GRAPH_WITH_USER_RESOURCE_LAYER",
        "design_principle": "Developer architecture and user architecture are separate ownership domains.",
        "summary": {
            **base["summary"],
            "resource_root_records": len(resource_roots),
            "user_asset_files": len(user_assets),
            "developer_asset_files": len(developer_assets),
            "non_authoritative_reference_files": len(non_authoritative_assets),
            "audience_counts": dict(sorted(audience_counts.items())),
            "visibility_counts": dict(sorted(visibility_counts.items())),
            "lifecycle_counts": dict(sorted(lifecycle_counts.items())),
            "authority_counts": dict(sorted(authority_counts.items())),
        },
        "resource_roots": resource_roots,
        "files": files,
        "owners": base["owners"],
        "subsystems": base["subsystems"],
        "dependency_edges": base["dependency_edges"],
        "unresolved_or_external_import_edges": base["unresolved_or_external_import_edges"],
        "subsystem_dependency_edges": base["subsystem_dependency_edges"],
        "owner_dependency_edges": base["owner_dependency_edges"],
        "user_resource_ownership_layer": {
            "canonical_user_roots": USER_RESOURCE_ROOTS,
            "policy": {
                "one_authoritative_location": True,
                "user_data_must_not_be_hidden_in_internal_folders": True,
                "legacy_and_quarantine_locations_are_import_or_recovery_sources_only": True,
                "developer_internals_must_not_be_required_for_normal_engineer_workflow": True,
            },
            "user_assets": user_assets,
            "developer_assets_sample": developer_assets[:100],
            "non_authoritative_assets_sample": non_authoritative_assets[:100],
        },
    }


def write_repository_ownership_graph(root: str | Path = ".", output_path: str | Path = "_leaf_artifacts/repository_architecture/phase_17f/repository_ownership_graph_phase_17f.json") -> dict[str, Any]:
    graph = build_repository_ownership_graph(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return graph


if __name__ == "__main__":
    graph = write_repository_ownership_graph(".")
    s = graph["summary"]
    print("LEAF_REPOSITORY_OWNERSHIP_GRAPH_PHASE_17F")
    print(f"schema={graph['schema']}")
    print(f"file_nodes={s['file_nodes']}")
    print(f"owner_nodes={s['owner_nodes']}")
    print(f"user_asset_files={s['user_asset_files']}")
    print(f"developer_asset_files={s['developer_asset_files']}")
    print(f"resource_root_records={s['resource_root_records']}")
