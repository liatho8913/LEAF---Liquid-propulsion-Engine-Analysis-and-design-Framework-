from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.sorting_user_approval_rules_phase_23b import (
    SCHEMA,
    write_sorting_user_approval_rules,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_23b"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_activation_readiness_audit_phase_23a.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_user_approval_rules_phase_23b.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_user_approval_rules_gate_phase_23b.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    written = write_sorting_user_approval_rules(ROOT)
    model = written["model"]
    summary = model["summary"]
    policy = model["execution_policy"]

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if summary.get("approval_rule_count") != 8:
        failures.append("approval_rule_count_invalid")

    if summary.get("required_rules") != 8:
        failures.append("required_rules_invalid")

    if summary.get("blocking_rules") != 8:
        failures.append("blocking_rules_invalid")

    for key in [
        "manual_approval_required",
        "candidate_specific_approval_required",
        "rollback_snapshot_required",
        "small_batch_limit_required",
        "ready_for_23c_safe_execution_sandbox",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true:{key}")

    for key in [
        "delete_operations_allowed",
        "automatic_execution_allowed",
        "continuous_watcher_allowed",
        "approval_grants_execution",
        "imports_files",
        "copies_files",
        "moves_files",
        "deletes_files",
        "archives_files",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false:{key}")

    for key in [
        "manual_approval_required",
        "candidate_specific_approval_required",
        "destination_specific_approval_required",
        "operation_specific_approval_required",
        "rollback_snapshot_required",
        "small_batch_limit_required",
        "approval_prepares_for_later_sandbox",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true:{key}")

    for key in [
        "delete_operations_allowed",
        "automatic_execution_allowed",
        "continuous_watcher_allowed",
        "approval_grants_execution",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false:{key}")

    expected_rules = {
        "approve_source_path",
        "approve_destination_path",
        "approve_operation_type",
        "approve_duplicate_resolution",
        "approve_rollback_snapshot",
        "approve_small_batch_limit",
        "deny_delete_operations",
        "deny_automatic_execution",
    }

    actual_rules = {rule.get("rule_id") for rule in model.get("rules", [])}

    if actual_rules != expected_rules:
        failures.append("approval_rule_set_invalid")

    for rule in model.get("rules", []):
        if rule.get("required") is not True:
            failures.append(f"rule_not_required:{rule.get('rule_id')}")
        if rule.get("blocks_execution_if_missing") is not True:
            failures.append(f"rule_not_blocking:{rule.get('rule_id')}")

    result = {
        "phase": "23B",
        "feature": "SORTING_USER_APPROVAL_RULES",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": summary,
        "approval_rules": sorted(actual_rules),
        "failures": failures,
        "model_json": written["json_path"],
        "model_report": written["txt_path"],
        "completion_notice": "PHASE_23B_COMPLETE_SORTING_USER_APPROVAL_RULES_ESTABLISHED" if not failures else "PHASE_23B_BLOCKED",
        "next_phase": "23C_SAFE_EXECUTION_SANDBOX",
    }

    gate_json = OUT / "sorting_user_approval_rules_gate_phase_23b.json"
    gate_txt = OUT / "sorting_user_approval_rules_gate_phase_23b.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 23B SORTING USER APPROVAL RULES GATE",
        "================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"approval_rule_count={summary.get('approval_rule_count')}",
        f"required_rules={summary.get('required_rules')}",
        f"blocking_rules={summary.get('blocking_rules')}",
        f"manual_approval_required={summary.get('manual_approval_required')}",
        f"candidate_specific_approval_required={summary.get('candidate_specific_approval_required')}",
        f"rollback_snapshot_required={summary.get('rollback_snapshot_required')}",
        f"small_batch_limit_required={summary.get('small_batch_limit_required')}",
        f"delete_operations_allowed={summary.get('delete_operations_allowed')}",
        f"automatic_execution_allowed={summary.get('automatic_execution_allowed')}",
        f"continuous_watcher_allowed={summary.get('continuous_watcher_allowed')}",
        f"approval_grants_execution={summary.get('approval_grants_execution')}",
        f"imports_files={summary.get('imports_files')}",
        f"copies_files={summary.get('copies_files')}",
        f"moves_files={summary.get('moves_files')}",
        f"deletes_files={summary.get('deletes_files')}",
        f"archives_files={summary.get('archives_files')}",
        f"ready_for_23c_safe_execution_sandbox={summary.get('ready_for_23c_safe_execution_sandbox')}",
        f"approval_rules={','.join(result['approval_rules'])}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"model_json={result['model_json']}",
        f"model_report={result['model_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_23B_SORTING_USER_APPROVAL_RULES" if result["passed"] else "FAIL_PHASE_23B_SORTING_USER_APPROVAL_RULES")
    print(f"schema={result['schema']}")
    print(f"approval_rule_count={summary.get('approval_rule_count')}")
    print(f"required_rules={summary.get('required_rules')}")
    print(f"blocking_rules={summary.get('blocking_rules')}")
    print(f"manual_approval_required={summary.get('manual_approval_required')}")
    print(f"candidate_specific_approval_required={summary.get('candidate_specific_approval_required')}")
    print(f"rollback_snapshot_required={summary.get('rollback_snapshot_required')}")
    print(f"small_batch_limit_required={summary.get('small_batch_limit_required')}")
    print(f"delete_operations_allowed={summary.get('delete_operations_allowed')}")
    print(f"automatic_execution_allowed={summary.get('automatic_execution_allowed')}")
    print(f"continuous_watcher_allowed={summary.get('continuous_watcher_allowed')}")
    print(f"approval_grants_execution={summary.get('approval_grants_execution')}")
    print(f"ready_for_23c_safe_execution_sandbox={summary.get('ready_for_23c_safe_execution_sandbox')}")
    print(f"approval_rules={','.join(result['approval_rules'])}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"model_json={result['model_json']}")
    print(f"model_report={result['model_report']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
