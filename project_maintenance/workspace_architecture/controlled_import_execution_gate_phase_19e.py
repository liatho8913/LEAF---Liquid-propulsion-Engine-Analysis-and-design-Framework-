from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.controlled_import_execution_phase_19e import (
    SCHEMA,
    build_controlled_import_execution_plan,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_19e"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "manual_import_approval_gate_phase_19d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "controlled_import_execution_phase_19e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "controlled_import_execution_gate_phase_19e.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    result_plan = build_controlled_import_execution_plan(ROOT, execute=False)
    summary = result_plan["summary"]
    policy = result_plan["execution_policy"]

    if result_plan.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if result_plan.get("source_approval_schema") != "LEAF_MANUAL_IMPORT_APPROVAL_GATE_PHASE_19D_V1":
        failures.append("source_approval_schema_invalid")

    if result_plan.get("execution_mode") != "DRY_RUN_VALIDATION":
        failures.append("gate_must_use_dry_run_validation")

    for key in [
        "manual_approval_required",
        "copy_only",
        "preserve_source",
        "hash_verification_required",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "overwrite_allowed",
        "delete_source_allowed",
        "archive_source_allowed",
        "move_source_allowed",
        "execute_requested",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    for key in [
        "executed_records",
        "copy_operations_executed",
        "move_operations_executed",
        "delete_operations_executed",
        "archive_operations_executed",
        "overwrite_operations_executed",
        "failures",
    ]:
        if summary.get(key) != 0:
            failures.append(f"unsafe_or_failure_summary_nonzero={key}")

    if summary.get("approved_records_detected") != 0:
        failures.append("approved_records_detected_before_manual_approval")

    for review_id, item in result_plan.get("blocked_records", {}).items():
        if item.get("execution_allowed") is not False:
            failures.append(f"blocked_record_execution_allowed={review_id}")
        if item.get("executed") is not False:
            failures.append(f"blocked_record_executed={review_id}")

    for review_id, item in result_plan.get("prepared_records", {}).items():
        if item.get("execution_allowed") is not False:
            failures.append(f"prepared_record_execution_allowed_in_dry_run={review_id}")
        if item.get("executed") is not False:
            failures.append(f"prepared_record_executed_in_dry_run={review_id}")

    execution_path = OUT / "controlled_import_execution_phase_19e.json"
    gate_json = OUT / "controlled_import_execution_gate_phase_19e.json"
    gate_txt = OUT / "controlled_import_execution_gate_phase_19e.txt"

    execution_path.write_text(json.dumps(result_plan, indent=2), encoding="utf-8")

    result = {
        "phase": "19E",
        "feature": "CONTROLLED_IMPORT_EXECUTION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": result_plan.get("schema"),
        "source_approval_schema": result_plan.get("source_approval_schema"),
        "execution_mode": result_plan.get("execution_mode"),
        "summary": summary,
        "failures": failures,
        "execution_json": execution_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_19E_COMPLETE_CONTROLLED_IMPORT_EXECUTION_ENGINE_ESTABLISHED" if not failures else "PHASE_19E_BLOCKED",
        "next_phase": "19F_IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 19E CONTROLLED IMPORT EXECUTION",
        "===========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_approval_schema={result['source_approval_schema']}",
        f"execution_mode={result['execution_mode']}",
        f"approval_records={summary.get('approval_records')}",
        f"approved_records_detected={summary.get('approved_records_detected')}",
        f"prepared_records={summary.get('prepared_records')}",
        f"blocked_records={summary.get('blocked_records')}",
        f"executed_records={summary.get('executed_records')}",
        f"copy_operations_executed={summary.get('copy_operations_executed')}",
        f"move_operations_executed={summary.get('move_operations_executed')}",
        f"delete_operations_executed={summary.get('delete_operations_executed')}",
        f"archive_operations_executed={summary.get('archive_operations_executed')}",
        f"overwrite_operations_executed={summary.get('overwrite_operations_executed')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"execution_json={result['execution_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_19E_CONTROLLED_IMPORT_EXECUTION" if result["passed"] else "FAIL_PHASE_19E_CONTROLLED_IMPORT_EXECUTION")
    print(f"schema={result['schema']}")
    print(f"source_approval_schema={result['source_approval_schema']}")
    print(f"execution_mode={result['execution_mode']}")
    print(f"approval_records={summary.get('approval_records')}")
    print(f"approved_records_detected={summary.get('approved_records_detected')}")
    print(f"prepared_records={summary.get('prepared_records')}")
    print(f"blocked_records={summary.get('blocked_records')}")
    print(f"executed_records={summary.get('executed_records')}")
    print(f"copy_operations_executed={summary.get('copy_operations_executed')}")
    print(f"move_operations_executed={summary.get('move_operations_executed')}")
    print(f"delete_operations_executed={summary.get('delete_operations_executed')}")
    print(f"archive_operations_executed={summary.get('archive_operations_executed')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"execution_json={result['execution_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
