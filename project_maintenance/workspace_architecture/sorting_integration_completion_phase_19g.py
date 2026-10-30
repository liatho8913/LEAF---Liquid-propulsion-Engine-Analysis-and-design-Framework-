from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_SORTING_INTEGRATION_COMPLETION_PHASE_19G_V1"

PHASE_ARTIFACTS = {
    "19A": {
        "path": "_leaf_artifacts/workspace_architecture/phase_19a/workspace_import_candidate_detector_phase_19a.json",
        "schema": "LEAF_WORKSPACE_IMPORT_CANDIDATE_DETECTOR_PHASE_19A_V1",
    },
    "19B": {
        "path": "_leaf_artifacts/workspace_architecture/phase_19b/import_review_registry_phase_19b.json",
        "schema": "LEAF_IMPORT_REVIEW_REGISTRY_PHASE_19B_V1",
    },
    "19C": {
        "path": "_leaf_artifacts/workspace_architecture/phase_19c/safe_import_plan_phase_19c.json",
        "schema": "LEAF_SAFE_IMPORT_PLAN_GENERATOR_PHASE_19C_V1",
    },
    "19D": {
        "path": "_leaf_artifacts/workspace_architecture/phase_19d/manual_import_approval_gate_phase_19d.json",
        "schema": "LEAF_MANUAL_IMPORT_APPROVAL_GATE_PHASE_19D_V1",
    },
    "19E": {
        "path": "_leaf_artifacts/workspace_architecture/phase_19e/controlled_import_execution_phase_19e.json",
        "schema": "LEAF_CONTROLLED_IMPORT_EXECUTION_PHASE_19E_V1",
    },
    "19F": {
        "path": "_leaf_artifacts/workspace_architecture/phase_19f/import_verification_rollback_snapshot_phase_19f.json",
        "schema": "LEAF_IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT_PHASE_19F_V1",
    },
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_sorting_integration_completion_certificate(root: str | Path = ".") -> dict[str, Any]:
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
            "execution_policy": data.get("execution_policy", {}),
        }

    detector_summary = artifacts.get("19A", {}).get("summary", {})
    registry_summary = artifacts.get("19B", {}).get("summary", {})
    plan_summary = artifacts.get("19C", {}).get("summary", {})
    approval_summary = artifacts.get("19D", {}).get("summary", {})
    execution_summary = artifacts.get("19E", {}).get("summary", {})
    rollback_summary = artifacts.get("19F", {}).get("summary", {})

    if detector_summary.get("automatic_actions_created", 0) != 0:
        failures.append("19A_automatic_actions_created")

    if registry_summary.get("automatic_actions_created", 0) != 0:
        failures.append("19B_automatic_actions_created")

    if plan_summary.get("automatic_actions_created", 0) != 0:
        failures.append("19C_automatic_actions_created")

    if plan_summary.get("execution_allowed_plans", 0) != 0:
        failures.append("19C_execution_allowed_plans_nonzero")

    if approval_summary.get("automatic_approvals_created", 0) != 0:
        failures.append("19D_automatic_approvals_created")

    if approval_summary.get("execution_unlocked_records", 0) != 0:
        failures.append("19D_execution_unlocked_records_nonzero")

    if execution_summary.get("executed_records", 0) != 0:
        failures.append("19E_executed_records_nonzero_without_manual_approval")

    if execution_summary.get("copy_operations_executed", 0) != 0:
        failures.append("19E_copy_operations_executed_nonzero_without_manual_approval")

    if rollback_summary.get("verification_failures", 0) != 0:
        failures.append("19F_verification_failures_nonzero")

    if execution_summary.get("executed_records", 0) == 0 and rollback_summary.get("safe_no_op_state") is not True:
        failures.append("19F_safe_no_op_state_missing")

    programme_completed = not failures

    return {
        "schema": SCHEMA,
        "phase": "19G",
        "feature": "SORTING_INTEGRATION_COMPLETION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "programme_completed": programme_completed,
        "completion_notice": "PHASE_19G_COMPLETE_SORTING_INTEGRATION_SIGNED_OFF" if programme_completed else "PHASE_19G_BLOCKED",
        "sorting_integration_completed_phases": [
            "19A Workspace Import Candidate Detector",
            "19B Import Review Registry",
            "19C Safe Import Plan Generator",
            "19D Manual Approval Gate",
            "19E Controlled Import Execution",
            "19F Import Verification / Rollback Snapshot",
            "19G Sorting Integration Completion",
        ],
        "activation_status": {
            "repository_sorting_brain_complete": True,
            "workspace_sorting_brain_complete": True,
            "controlled_detection_active": True,
            "review_registry_active": True,
            "safe_import_planning_active": True,
            "manual_approval_gate_active": True,
            "controlled_execution_engine_available": True,
            "rollback_verification_available": True,
            "automatic_import_active": False,
            "gui_activation_active": False,
            "ready_for_gui_activation": programme_completed,
        },
        "design_philosophy_signed_off": {
            "developer_architecture_is_not_user_architecture": True,
            "user_assets_are_first_class": True,
            "non_authoritative_sources_are_review_sources_only": True,
            "manual_review_before_import": True,
            "copy_not_move": True,
            "preserve_source": True,
            "hash_verification_required": True,
            "rollback_awareness_required": True,
            "no_automatic_delete_archive_or_move": True,
            "sustainability_means_reuse_and_navigation_clarity": True,
        },
        "summary": {
            "artifacts_required": len(PHASE_ARTIFACTS),
            "artifacts_present": sum(1 for item in artifacts.values() if item.get("present")),
            "schemas_valid": sum(1 for item in artifacts.values() if item.get("schema_valid")),
            "import_candidates": detector_summary.get("import_candidates", 0),
            "review_records": registry_summary.get("review_records", 0),
            "plans_ready": plan_summary.get("plans_ready", 0),
            "plans_blocked": plan_summary.get("plans_blocked", 0),
            "approval_records": approval_summary.get("approval_records", 0),
            "approved_records": approval_summary.get("approved_records", 0),
            "executed_records": execution_summary.get("executed_records", 0),
            "safe_no_op_state": rollback_summary.get("safe_no_op_state"),
            "programme_completed": programme_completed,
            "ready_for_next_programme": programme_completed,
            "next_programme": "20_GUI_WORKSPACE_ACTIVATION",
        },
        "phase_artifacts": artifacts,
        "safety_locks": {
            "move_allowed": False,
            "archive_allowed": False,
            "delete_allowed": False,
            "automatic_delete_allowed": False,
            "automatic_relocation_allowed": False,
            "automatic_import_allowed": False,
            "gui_execution_allowed": False,
            "completion_gate_execution_allowed": False,
            "deletion_started": False,
        },
        "failures": failures,
        "next_recommended_programme": {
            "name": "GUI / Workspace Activation",
            "purpose": "Expose the completed workspace sorting intelligence through practical LEAF interface panels and controlled user workflows.",
            "first_feature": "20A Workspace Sidebar Model",
        },
    }


def write_sorting_integration_completion_certificate(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/workspace_architecture/phase_19g/sorting_integration_completion_certificate_phase_19g.json",
) -> dict[str, Any]:
    certificate = build_sorting_integration_completion_certificate(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    return certificate


if __name__ == "__main__":
    cert = write_sorting_integration_completion_certificate(".")
    summary = cert["summary"]

    print("LEAF_SORTING_INTEGRATION_COMPLETION_PHASE_19G")
    print(f"schema={cert['schema']}")
    print(f"programme_completed={cert['programme_completed']}")
    print(f"artifacts_required={summary['artifacts_required']}")
    print(f"artifacts_present={summary['artifacts_present']}")
    print(f"schemas_valid={summary['schemas_valid']}")
    print(f"import_candidates={summary['import_candidates']}")
    print(f"review_records={summary['review_records']}")
    print(f"plans_ready={summary['plans_ready']}")
    print(f"approval_records={summary['approval_records']}")
    print(f"executed_records={summary['executed_records']}")
    print(f"safe_no_op_state={summary['safe_no_op_state']}")
    print(f"completion_notice={cert['completion_notice']}")
    print(f"next_programme={summary['next_programme']}")
