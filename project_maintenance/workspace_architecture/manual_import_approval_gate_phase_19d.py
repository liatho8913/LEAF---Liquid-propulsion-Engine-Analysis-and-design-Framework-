from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from leaf_qt.workspace_runtime_core import build_safe_import_plan

SCHEMA = "LEAF_MANUAL_IMPORT_APPROVAL_GATE_PHASE_19D_V1"


def build_manual_import_approval_gate(root: str | Path = ".") -> dict[str, Any]:
    plan = build_safe_import_plan(root)
    ready_plans = plan.get("ready_plans", {})
    blocked_plans = plan.get("blocked_plans", {})

    approval_records: dict[str, dict[str, Any]] = {}

    for review_id, item in ready_plans.items():
        approval_records[review_id] = {
            "review_id": review_id,
            "plan_id": item.get("plan_id"),
            "source_path": item.get("source_path"),
            "recommended_destination": item.get("recommended_destination"),
            "status": "AWAITING_MANUAL_APPROVAL",
            "approval_state": "UNAPPROVED",
            "approval_required": True,
            "approved": False,
            "rejected": False,
            "execution_unlocked": False,
            "copy_import_unlocked": False,
            "manual_approver": "",
            "approval_timestamp": "",
            "approval_notes": "",
            "source_sha256": item.get("sha256"),
            "candidate_type": item.get("candidate_type"),
            "priority": item.get("priority"),
        }

    return {
        "schema": SCHEMA,
        "phase": "19D",
        "feature": "MANUAL_IMPORT_APPROVAL_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_safe_import_plan_schema": plan.get("schema"),
        "design_principle": "Import execution must remain locked until a specific ready plan receives explicit manual approval.",
        "execution_policy": {
            "approval_gate_is_read_only": True,
            "creates_approval_records_only": True,
            "automatically_approves": False,
            "imports_files": False,
            "copies_files": False,
            "moves_existing_files": False,
            "deletes_files": False,
            "archives_files": False,
            "overwrites_files": False,
        },
        "summary": {
            "ready_plans": len(ready_plans),
            "blocked_plans": len(blocked_plans),
            "approval_records": len(approval_records),
            "awaiting_manual_approval": len(approval_records),
            "approved_records": 0,
            "rejected_records": 0,
            "execution_unlocked_records": 0,
            "copy_import_unlocked_records": 0,
            "automatic_approvals_created": 0,
        },
        "approval_records": dict(sorted(approval_records.items())),
        "blocked_plan_count": len(blocked_plans),
    }


def write_manual_import_approval_gate(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/workspace_architecture/phase_19d/manual_import_approval_gate_phase_19d.json",
) -> dict[str, Any]:
    gate = build_manual_import_approval_gate(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    return gate


if __name__ == "__main__":
    gate = write_manual_import_approval_gate(".")
    summary = gate["summary"]

    print("LEAF_MANUAL_IMPORT_APPROVAL_GATE_PHASE_19D")
    print(f"schema={gate['schema']}")
    print(f"source_safe_import_plan_schema={gate['source_safe_import_plan_schema']}")
    print(f"ready_plans={summary['ready_plans']}")
    print(f"approval_records={summary['approval_records']}")
    print(f"approved_records={summary['approved_records']}")
    print(f"execution_unlocked_records={summary['execution_unlocked_records']}")
