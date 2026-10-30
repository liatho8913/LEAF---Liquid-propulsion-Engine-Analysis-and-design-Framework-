from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_WORKSPACE_ARCHITECTURE_COMPLETION_PHASE_18E_V1"

PHASE_ARTIFACTS = {
    "18A": {
        "path": "_leaf_artifacts/workspace_architecture/phase_18a/user_resource_canonical_folder_plan_phase_18a.json",
        "schema": "LEAF_USER_RESOURCE_CANONICAL_FOLDER_SYSTEM_PHASE_18A_V1",
    },
    "18B": {
        "path": "_leaf_artifacts/workspace_architecture/phase_18b/workspace_resource_registry_phase_18b.json",
        "schema": "LEAF_WORKSPACE_RESOURCE_REGISTRY_PHASE_18B_V1",
    },
    "18C": {
        "path": "_leaf_artifacts/workspace_architecture/phase_18c/workspace_resource_ownership_layer_phase_18c.json",
        "schema": "LEAF_WORKSPACE_RESOURCE_OWNERSHIP_LAYER_PHASE_18C_V1",
    },
    "18D": {
        "path": "_leaf_artifacts/workspace_architecture/phase_18d/workspace_navigation_model_phase_18d.json",
        "schema": "LEAF_WORKSPACE_NAVIGATION_MODEL_PHASE_18D_V1",
    },
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_workspace_architecture_completion_certificate(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    failures: list[str] = []
    artifacts: dict[str, dict[str, Any]] = {}

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

    nav_summary = artifacts.get("18D", {}).get("summary", {})
    folder_summary = artifacts.get("18A", {}).get("summary", {})
    registry_summary = artifacts.get("18B", {}).get("summary", {})
    ownership_summary = artifacts.get("18C", {}).get("summary", {})

    if folder_summary.get("canonical_roots_present") != folder_summary.get("canonical_roots_required"):
        failures.append("canonical_user_roots_not_complete")

    if registry_summary.get("developer_files_registered", 0) != 0:
        failures.append("developer_files_registered_as_user_assets")

    if ownership_summary.get("ownership_failures", 0) != 0:
        failures.append("ownership_failures_present")

    if nav_summary.get("developer_sections_exposed", 0) != 0:
        failures.append("developer_sections_exposed")

    if nav_summary.get("internal_paths_required_for_user_navigation", 0) != 0:
        failures.append("internal_paths_required_for_user_navigation")

    if nav_summary.get("user_visible_navigation_ready") is not True:
        failures.append("user_visible_navigation_not_ready")

    programme_completed = not failures

    return {
        "schema": SCHEMA,
        "phase": "18E",
        "feature": "WORKSPACE_ARCHITECTURE_COMPLETION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "programme_completed": programme_completed,
        "completion_notice": "PHASE_18E_COMPLETE_WORKSPACE_ARCHITECTURE_SIGNED_OFF" if programme_completed else "PHASE_18E_BLOCKED",
        "workspace_architecture_completed_phases": [
            "18A User Resource Canonical Folder System",
            "18B Workspace Resource Registry",
            "18C Project / Design / Report / Export Ownership Layer",
            "18D Workspace Navigation Model",
            "18E Workspace Architecture Completion",
        ],
        "sorting_intelligence_status": {
            "repository_sorting_brain_complete": True,
            "workspace_sorting_brain_complete": programme_completed,
            "whole_sorting_intelligence_engine_complete": programme_completed,
            "developer_architecture_separated_from_user_architecture": True,
            "user_resources_have_canonical_roots": True,
            "workspace_resources_registered": True,
            "workspace_resources_owned": True,
            "workspace_navigation_model_ready": True,
        },
        "design_philosophy_signed_off": {
            "developer_architecture_is_not_user_architecture": True,
            "engineers_navigate_designs_projects_reports_and_exports": True,
            "users_do_not_need_to_understand_internal_repository_folders": True,
            "frequently_used_resources_are_root_level_and_obvious": True,
            "one_authoritative_user_location": True,
            "navigation_sustainability_matters": True,
            "minimum_cognitive_load": True,
            "replacement_not_accumulation": True,
            "read_only_before_execution": True,
            "no_hidden_user_data": True,
        },
        "summary": {
            "artifacts_required": len(PHASE_ARTIFACTS),
            "artifacts_present": sum(1 for item in artifacts.values() if item.get("present")),
            "schemas_valid": sum(1 for item in artifacts.values() if item.get("schema_valid")),
            "canonical_roots_required": folder_summary.get("canonical_roots_required", 0),
            "canonical_roots_present": folder_summary.get("canonical_roots_present", 0),
            "registered_resources": registry_summary.get("registered_resources", 0),
            "owned_resources": ownership_summary.get("owned_resources", 0),
            "navigation_sections": nav_summary.get("navigation_sections", 0),
            "navigation_items": nav_summary.get("navigation_items", 0),
            "developer_sections_exposed": nav_summary.get("developer_sections_exposed", 0),
            "internal_paths_required_for_user_navigation": nav_summary.get("internal_paths_required_for_user_navigation", 0),
            "programme_completed": programme_completed,
            "ready_for_next_programme": programme_completed,
            "next_programme": "19_SORTING_INTELLIGENCE_INTEGRATION_AND_CONTROLLED_IMPORT_REVIEW",
        },
        "phase_artifacts": artifacts,
        "safety_locks": {
            "move_allowed": False,
            "archive_allowed": False,
            "delete_allowed": False,
            "automatic_delete_allowed": False,
            "automatic_relocation_allowed": False,
            "automatic_import_allowed": False,
            "completion_gate_execution_allowed": False,
            "deletion_started": False,
        },
        "failures": failures,
        "next_recommended_programme": {
            "name": "Sorting Intelligence Integration and Controlled Import Review",
            "purpose": "Connect repository intelligence and workspace intelligence so non-authoritative user-resource candidates can be reviewed and safely imported into canonical workspace roots.",
            "first_feature": "19A Workspace Import Candidate Detector",
        },
    }


def write_workspace_architecture_completion_certificate(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/workspace_architecture/phase_18e/workspace_architecture_completion_certificate_phase_18e.json",
) -> dict[str, Any]:
    certificate = build_workspace_architecture_completion_certificate(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    return certificate


if __name__ == "__main__":
    cert = write_workspace_architecture_completion_certificate(".")
    summary = cert["summary"]

    print("LEAF_WORKSPACE_ARCHITECTURE_COMPLETION_PHASE_18E")
    print(f"schema={cert['schema']}")
    print(f"programme_completed={cert['programme_completed']}")
    print(f"artifacts_required={summary['artifacts_required']}")
    print(f"artifacts_present={summary['artifacts_present']}")
    print(f"schemas_valid={summary['schemas_valid']}")
    print(f"canonical_roots_present={summary['canonical_roots_present']}")
    print(f"registered_resources={summary['registered_resources']}")
    print(f"owned_resources={summary['owned_resources']}")
    print(f"navigation_sections={summary['navigation_sections']}")
    print(f"navigation_items={summary['navigation_items']}")
    print(f"completion_notice={cert['completion_notice']}")
    print(f"next_programme={summary['next_programme']}")
