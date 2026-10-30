from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_REPOSITORY_ARCHITECTURE_COMPLETION_PHASE_17K_V1"

PHASE_ARTIFACTS = {
    "17F": {
        "path": "_leaf_artifacts/repository_architecture/phase_17f/repository_ownership_graph_phase_17f.json",
        "schema": "LEAF_REPOSITORY_OWNERSHIP_GRAPH_PHASE_17F_V1",
    },
    "17G": {
        "path": "_leaf_artifacts/repository_architecture/phase_17g/universal_repository_index_phase_17g.json",
        "schema": "LEAF_UNIVERSAL_REPOSITORY_INDEX_PHASE_17G_V1",
    },
    "17H": {
        "path": "_leaf_artifacts/repository_architecture/phase_17h/repository_semantic_knowledge_graph_phase_17h.json",
        "schema": "LEAF_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH_PHASE_17H_V1",
    },
    "17I": {
        "path": "_leaf_artifacts/repository_architecture/phase_17i/intelligent_repository_relocation_plan_phase_17i.json",
        "schema": "LEAF_INTELLIGENT_REPOSITORY_RELOCATION_PHASE_17I_V1",
    },
    "17J": {
        "path": "_leaf_artifacts/repository_architecture/phase_17j/repository_health_report_phase_17j.json",
        "schema": "LEAF_REPOSITORY_HEALTH_MONITOR_PHASE_17J_V1",
    },
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_repository_architecture_completion_certificate(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)

    artifacts: dict[str, dict[str, Any]] = {}
    failures: list[str] = []

    for phase, spec in PHASE_ARTIFACTS.items():
        path = root / spec["path"]
        data = _load_json(path)

        if data is None:
            failures.append(f"missing_artifact:{phase}:{spec['path']}")
            artifacts[phase] = {
                "path": spec["path"],
                "present": False,
                "schema_valid": False,
            }
            continue

        schema_valid = data.get("schema") == spec["schema"]
        if not schema_valid:
            failures.append(f"schema_invalid:{phase}:{data.get('schema')}")

        artifacts[phase] = {
            "path": spec["path"],
            "present": True,
            "schema": data.get("schema"),
            "schema_valid": schema_valid,
            "summary": data.get("summary", {}),
        }

    health = artifacts.get("17J", {}).get("summary", {})
    health_status = health.get("overall_status")
    health_score = health.get("overall_score")

    if health_status != "PASS":
        failures.append(f"health_status_not_pass:{health_status}")

    safety_locks = {
        "move_allowed": False,
        "archive_allowed": False,
        "delete_allowed": False,
        "automatic_delete_allowed": False,
        "automatic_relocation_allowed": False,
        "completion_gate_execution_allowed": False,
        "deletion_started": False,
    }

    programme_completed = not failures

    return {
        "schema": SCHEMA,
        "phase": "17K",
        "feature": "REPOSITORY_ARCHITECTURE_COMPLETION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "programme_completed": programme_completed,
        "completion_notice": "PHASE_17K_COMPLETE_REPOSITORY_ARCHITECTURE_PROGRAMME_SIGNED_OFF" if programme_completed else "PHASE_17K_BLOCKED",
        "repository_architecture_completed_phases": [
            "17A Repository Discovery",
            "17B Repository Classification",
            "17C Shared Snapshot Architecture",
            "17D Repository Intelligence Consolidation",
            "17E Repository Roadmap Visibility System",
            "17F Repository Ownership Graph",
            "17G Universal Repository Index",
            "17H Repository Semantic Knowledge Graph",
            "17I Intelligent Repository Relocation",
            "17J Repository Health Monitor",
            "17K Repository Architecture Completion",
        ],
        "design_philosophy_signed_off": {
            "foundations_first": True,
            "replacement_not_accumulation": True,
            "shared_snapshot_not_duplicate_scanning": True,
            "developer_architecture_is_not_user_architecture": True,
            "user_facing_assets_require_obvious_canonical_locations": True,
            "one_authoritative_location_for_user_assets": True,
            "navigation_sustainability_matters_as_much_as_code_sustainability": True,
            "read_only_before_execution": True,
            "no_automatic_delete_archive_or_move": True,
        },
        "summary": {
            "artifacts_required": len(PHASE_ARTIFACTS),
            "artifacts_present": sum(1 for item in artifacts.values() if item.get("present")),
            "schemas_valid": sum(1 for item in artifacts.values() if item.get("schema_valid")),
            "health_score": health_score,
            "health_status": health_status,
            "programme_completed": programme_completed,
            "ready_for_next_programme": programme_completed,
            "next_programme": "WORKSPACE_ARCHITECTURE_AND_USER_RESOURCE_SYSTEM",
        },
        "phase_artifacts": artifacts,
        "safety_locks": safety_locks,
        "failures": failures,
        "next_recommended_programme": {
            "name": "Workspace Architecture and User Resource System",
            "purpose": "Turn the repository architecture into a professional user-facing engineering workspace with canonical Designs, Projects, Reports, and Exports.",
            "first_feature": "18A User Resource Canonical Folder System",
        },
    }


def write_repository_architecture_completion_certificate(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/phase_17k/repository_architecture_completion_certificate_phase_17k.json",
) -> dict[str, Any]:
    certificate = build_repository_architecture_completion_certificate(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    return certificate


if __name__ == "__main__":
    cert = write_repository_architecture_completion_certificate(".")
    summary = cert["summary"]

    print("LEAF_REPOSITORY_ARCHITECTURE_COMPLETION_PHASE_17K")
    print(f"schema={cert['schema']}")
    print(f"programme_completed={cert['programme_completed']}")
    print(f"artifacts_required={summary['artifacts_required']}")
    print(f"artifacts_present={summary['artifacts_present']}")
    print(f"schemas_valid={summary['schemas_valid']}")
    print(f"health_score={summary['health_score']}")
    print(f"health_status={summary['health_status']}")
    print(f"completion_notice={cert['completion_notice']}")
    print(f"next_programme={summary['next_programme']}")
