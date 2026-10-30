from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_SORTING_USER_APPROVAL_RULES_PHASE_23B_V1"


@dataclass(frozen=True)
class SortingApprovalRule:
    rule_id: str
    label: str
    required: bool
    applies_to: str
    approval_type: str
    blocks_execution_if_missing: bool


def build_sorting_user_approval_rules(project_root: str | Path = ".") -> dict[str, Any]:
    rules = [
        SortingApprovalRule(
            "approve_source_path",
            "Approve Source Path",
            True,
            "each_candidate",
            "explicit_user_confirmation",
            True,
        ),
        SortingApprovalRule(
            "approve_destination_path",
            "Approve Destination Path",
            True,
            "each_candidate",
            "explicit_user_confirmation",
            True,
        ),
        SortingApprovalRule(
            "approve_operation_type",
            "Approve Operation Type",
            True,
            "each_candidate",
            "explicit_user_confirmation",
            True,
        ),
        SortingApprovalRule(
            "approve_duplicate_resolution",
            "Approve Duplicate Resolution",
            True,
            "duplicate_candidates",
            "explicit_user_confirmation",
            True,
        ),
        SortingApprovalRule(
            "approve_rollback_snapshot",
            "Approve Rollback Snapshot",
            True,
            "execution_batch",
            "explicit_user_confirmation",
            True,
        ),
        SortingApprovalRule(
            "approve_small_batch_limit",
            "Approve Small Batch Limit",
            True,
            "execution_batch",
            "explicit_user_confirmation",
            True,
        ),
        SortingApprovalRule(
            "deny_delete_operations",
            "Deny Delete Operations",
            True,
            "all_candidates",
            "hard_policy",
            True,
        ),
        SortingApprovalRule(
            "deny_automatic_execution",
            "Deny Automatic Execution",
            True,
            "all_candidates",
            "hard_policy",
            True,
        ),
    ]

    return {
        "schema": SCHEMA,
        "phase": "23B",
        "feature": "SORTING_USER_APPROVAL_RULES",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "approval_rule": "No sorting execution may occur unless required approvals are present, explicit, candidate-specific, and rollback-protected.",
        "rules": [asdict(rule) for rule in rules],
        "execution_policy": {
            "manual_approval_required": True,
            "candidate_specific_approval_required": True,
            "destination_specific_approval_required": True,
            "operation_specific_approval_required": True,
            "rollback_snapshot_required": True,
            "small_batch_limit_required": True,
            "delete_operations_allowed": False,
            "automatic_execution_allowed": False,
            "continuous_watcher_allowed": False,
            "approval_grants_execution": False,
            "approval_prepares_for_later_sandbox": True,
        },
        "summary": {
            "approval_rule_count": len(rules),
            "required_rules": sum(1 for rule in rules if rule.required),
            "blocking_rules": sum(1 for rule in rules if rule.blocks_execution_if_missing),
            "manual_approval_required": True,
            "candidate_specific_approval_required": True,
            "rollback_snapshot_required": True,
            "small_batch_limit_required": True,
            "delete_operations_allowed": False,
            "automatic_execution_allowed": False,
            "continuous_watcher_allowed": False,
            "approval_grants_execution": False,
            "imports_files": False,
            "copies_files": False,
            "moves_files": False,
            "deletes_files": False,
            "archives_files": False,
            "ready_for_23c_safe_execution_sandbox": True,
        },
    }


def write_sorting_user_approval_rules(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_23b"
    out_dir.mkdir(parents=True, exist_ok=True)

    model = build_sorting_user_approval_rules(root)

    json_path = out_dir / "sorting_user_approval_rules_phase_23b.json"
    txt_path = out_dir / "sorting_user_approval_rules_phase_23b.txt"

    json_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    txt_path.write_text("\n".join([
        "LEAF PHASE 23B SORTING USER APPROVAL RULES",
        "==========================================",
        f"schema={model['schema']}",
        f"phase={model['phase']}",
        f"feature={model['feature']}",
        f"approval_rule_count={model['summary']['approval_rule_count']}",
        f"required_rules={model['summary']['required_rules']}",
        f"blocking_rules={model['summary']['blocking_rules']}",
        f"manual_approval_required={model['summary']['manual_approval_required']}",
        f"candidate_specific_approval_required={model['summary']['candidate_specific_approval_required']}",
        f"rollback_snapshot_required={model['summary']['rollback_snapshot_required']}",
        f"small_batch_limit_required={model['summary']['small_batch_limit_required']}",
        f"delete_operations_allowed={model['summary']['delete_operations_allowed']}",
        f"automatic_execution_allowed={model['summary']['automatic_execution_allowed']}",
        f"continuous_watcher_allowed={model['summary']['continuous_watcher_allowed']}",
        f"approval_grants_execution={model['summary']['approval_grants_execution']}",
        f"ready_for_23c_safe_execution_sandbox={model['summary']['ready_for_23c_safe_execution_sandbox']}",
        "",
        "Rules:",
        *[
            f"{rule['rule_id']} — required={rule['required']} — blocks={rule['blocks_execution_if_missing']}"
            for rule in model["rules"]
        ],
    ]), encoding="utf-8")

    return {
        "model": model,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_sorting_user_approval_rules(Path.cwd())
    print("PASS_PHASE_23B_SORTING_USER_APPROVAL_RULES_WRITTEN")
    print(f"schema={result['model']['schema']}")
    print(f"approval_rule_count={result['model']['summary']['approval_rule_count']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
