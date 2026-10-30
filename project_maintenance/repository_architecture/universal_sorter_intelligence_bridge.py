from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_intelligence_api import (
    RepositoryIntelligenceAPI,
)

SCHEMA = "LEAF_UNIVERSAL_SORTER_INTELLIGENCE_BRIDGE_V1"


from project_maintenance.repository_architecture.universal_repository_sorter_engine import classify_repository

def semantic_destination_hint(file_info: dict[str, Any]) -> str:
    path = file_info["path"]
    semantic = file_info.get("semantic") or {}
    metadata = file_info.get("metadata") or {}

    layer = metadata.get("layer") or "unclassified"
    subsystem = semantic.get("semantic_subsystem") or metadata.get("subsystem") or "unclassified"
    role = semantic.get("semantic_role") or metadata.get("role") or "module"
    filename = Path(path).name

    if layer == "runtime":
        return f"leaf_qt/{subsystem}/{role}/{filename}"

    if layer == "development":
        return f"project_maintenance/{subsystem}/{role}/{filename}"

    if layer == "documentation":
        return f"docs/{subsystem}/{filename}"

    return path


def _build_sorter_intelligence_bridge_evidence(root: str | Path = ".") -> dict[str, Any]:
    api = RepositoryIntelligenceAPI(root)
    summary = api.summary()

    bridge_rows: dict[str, dict[str, Any]] = {}

    for path in api.database()["files"]:
        info = api.file(path)
        if not info:
            continue

        semantic = info.get("semantic") or {}
        metadata = info.get("metadata") or {}
        graph = info.get("graph") or {}

        destination = semantic_destination_hint({
            "path": path,
            "semantic": semantic,
            "metadata": metadata,
            "graph": graph,
        })

        bridge_rows[path] = {
            "path": path,
            "current_layer": metadata.get("layer"),
            "metadata_subsystem": metadata.get("subsystem"),
            "metadata_role": metadata.get("role"),
            "semantic_subsystem": semantic.get("semantic_subsystem"),
            "semantic_role": semantic.get("semantic_role"),
            "semantic_owner": semantic.get("semantic_owner"),
            "graph_owner": graph.get("owner"),
            "semantic_confidence": semantic.get("semantic_confidence", metadata.get("confidence", 0)),
            "dominant_signal": semantic.get("dominant_signal"),
            "classification_reason": semantic.get("classification_reason"),
            "proposed_destination": destination,
            "already_in_proposed_destination": path == destination,
            "sorter_input_ready": bool(semantic.get("semantic_subsystem") and semantic.get("semantic_role")),
        }

    planned_moves = [
        row for row in bridge_rows.values()
        if row["sorter_input_ready"] and not row["already_in_proposed_destination"]
    ]

    return {
        "schema": SCHEMA,
        "api_schema": summary["schema"],
        "summary": {
            "files_considered": len(bridge_rows),
            "sorter_ready_files": sum(1 for row in bridge_rows.values() if row["sorter_input_ready"]),
            "already_aligned_files": sum(1 for row in bridge_rows.values() if row["already_in_proposed_destination"]),
            "candidate_move_count": len(planned_moves),
            "architecture_errors": summary["architecture_errors"],
            "semantic_enriched_files": summary["semantic_enriched_files"],
        },
        "files": bridge_rows,
        "candidate_moves": planned_moves[:250],
    }


def build_sorter_intelligence_bridge(root: str | Path = ".") -> dict:
    """
    Build Organisation Intelligence using one canonical placement authority.

    Repository Intelligence and the original bridge provide semantic evidence.
    Universal Repository Sorter owns the final destination decision.
    """
    root_path = Path(root).resolve()

    result = _build_sorter_intelligence_bridge_evidence(root_path)

    files = result["files"]

    canonical_sorter = {
        str(item["path"]): item
        for item in classify_repository(root_path)
    }

    for path, item in files.items():
        sorter_item = canonical_sorter.get(str(path))

        if sorter_item is None:
            continue

        canonical_destination = str(
            sorter_item.get("proposed_destination")
        )

        item.setdefault(
            "semantic_proposed_destination",
            item.get("proposed_destination"),
        )

        item["proposed_destination"] = canonical_destination
        item["canonical_destination"] = canonical_destination
        item["placement_authority"] = sorter_item.get(
            "placement_authority"
        )
        item["canonical_domain"] = sorter_item.get(
            "canonical_domain"
        )
        item["organisation_action"] = sorter_item.get(
            "organisation_action"
        )
        item["movement_authorised"] = bool(
            sorter_item.get(
                "movement_authorised"
            )
        )
        item["placement_reason"] = sorter_item.get(
            "placement_reason"
        )
        item["placement_evidence"] = sorter_item.get(
            "placement_evidence",
            [],
        )
        item["existing_structure"] = sorter_item.get(
            "existing_structure"
        )
        item["sorter_semantic_destination"] = (
            sorter_item.get(
                "semantic_proposed_destination"
            )
        )
        item["already_in_proposed_destination"] = (
            str(path) == canonical_destination
        )

    values = list(files.values())

    summary = result.setdefault(
        "summary",
        {},
    )

    summary["files_considered"] = len(values)

    summary["sorter_ready_files"] = sum(
        bool(item.get("sorter_input_ready"))
        for item in values
    )

    aligned = [
        item
        for item in values
        if item.get("organisation_action")
        == "ALIGNED"
    ]

    protected = [
        item
        for item in values
        if item.get("organisation_action")
        == "PROTECTED"
    ]

    manual_review = [
        item
        for item in values
        if item.get("organisation_action")
        == "MANUAL_REVIEW_REQUIRED"
    ]

    trusted_moves = [
        item
        for item in values
        if (
            item.get("organisation_action")
            == "MOVE_CANDIDATE"
            and item.get("movement_authorised")
            is True
        )
    ]

    summary["already_aligned_files"] = len(
        aligned
    )

    summary["protected_files"] = len(
        protected
    )

    summary[
        "manual_review_required_count"
    ] = len(
        manual_review
    )

    summary["candidate_move_count"] = len(
        trusted_moves
    )

    summary[
        "trusted_move_candidate_count"
    ] = len(
        trusted_moves
    )

    summary[
        "protected_or_aligned_count"
    ] = (
        len(aligned)
        + len(protected)
    )

    summary[
        "repository_intelligence_semantic_move_hints"
    ] = sum(
        bool(item.get("sorter_input_ready"))
        and str(
            item.get(
                "semantic_proposed_destination",
                item.get("path"),
            )
        )
        != str(item.get("path"))
        for item in values
    )

    summary[
        "sorter_semantic_move_hints"
    ] = sum(
        str(
            item.get(
                "sorter_semantic_destination",
                item.get("path"),
            )
        )
        != str(item.get("path"))
        for item in values
    )

    result["candidate_moves"] = (
        trusted_moves[:250]
    )

    result["manual_review_preview"] = (
        manual_review[:250]
    )

    return result


def write_sorter_intelligence_bridge(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/universal_sorter_intelligence_bridge_v1.json",
) -> dict[str, Any]:
    result = build_sorter_intelligence_bridge(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = write_sorter_intelligence_bridge(".")
    summary = result["summary"]

    print("LEAF_UNIVERSAL_SORTER_INTELLIGENCE_BRIDGE")
    print(f"schema={result['schema']}")
    print(f"files_considered={summary['files_considered']}")
    print(f"sorter_ready_files={summary['sorter_ready_files']}")
    print(f"already_aligned_files={summary['already_aligned_files']}")
    print(f"candidate_move_count={summary['candidate_move_count']}")
    print(
        "trusted_move_candidate_count="
        f"{summary['trusted_move_candidate_count']}"
    )
    print(
        "manual_review_required_count="
        f"{summary['manual_review_required_count']}"
    )
    print(
        "protected_files="
        f"{summary['protected_files']}"
    )
    print(
        "already_aligned_files="
        f"{summary['already_aligned_files']}"
    )
    print(
        "sorter_semantic_move_hints="
        f"{summary['sorter_semantic_move_hints']}"
    )
    print(f"architecture_errors={summary['architecture_errors']}")
