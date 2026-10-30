from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.manual_import_approval_gate_phase_19d import (
    SCHEMA,
    build_manual_import_approval_gate,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_19d"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "manual_import_approval_gate_phase_19d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "manual_import_approval_gate_gate_phase_19d.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    approval_gate = build_manual_import_approval_gate(ROOT)
    summary = approval_gate["summary"]
    policy = approval_gate["execution_policy"]

    if approval_gate.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if approval_gate.get("source_safe_import_plan_schema") != "LEAF_SAFE_IMPORT_PLAN_GENERATOR_PHASE_19C_V1":
        failures.append("source_safe_import_plan_schema_invalid")

    if summary.get("ready_plans") != summary.get("approval_records"):
        failures.append("ready_plan_approval_record_mismatch")

    for key in [
        "approval_gate_is_read_only",
        "creates_approval_records_only",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "automatically_approves",
        "imports_files",
        "copies_files",
        "moves_existing_files",
        "deletes_files",
        "archives_files",
        "overwrites_files",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    for key in [
        "approved_records",
        "rejected_records",
        "execution_unlocked_records",
        "copy_import_unlocked_records",
        "automatic_approvals_created",
    ]:
        if summary.get(key) != 0:
            failures.append(f"unsafe_summary_nonzero={key}")

    for review_id, record in approval_gate.get("approval_records", {}).items():
        if record.get("approval_state") != "UNAPPROVED":
            failures.append(f"record_not_unapproved={review_id}")
        if record.get("approval_required") is not True:
            failures.append(f"record_approval_required_missing={review_id}")
        for key in [
            "approved",
            "rejected",
            "execution_unlocked",
            "copy_import_unlocked",
        ]:
            if record.get(key) is not False:
                failures.append(f"record_unsafe_flag_not_false={review_id}:{key}")

    approval_path = OUT / "manual_import_approval_gate_phase_19d.json"
    gate_json = OUT / "manual_import_approval_gate_gate_phase_19d.json"
    gate_txt = OUT / "manual_import_approval_gate_gate_phase_19d.txt"

    approval_path.write_text(json.dumps(approval_gate, indent=2), encoding="utf-8")

    result = {
        "phase": "19D",
        "feature": "MANUAL_IMPORT_APPROVAL_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": approval_gate.get("schema"),
        "source_safe_import_plan_schema": approval_gate.get("source_safe_import_plan_schema"),
        "summary": summary,
        "failures": failures,
        "approval_json": approval_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_19D_COMPLETE_MANUAL_IMPORT_APPROVAL_GATE_ESTABLISHED" if not failures else "PHASE_19D_BLOCKED",
        "next_phase": "19E_CONTROLLED_IMPORT_EXECUTION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 19D MANUAL IMPORT APPROVAL GATE",
        "===========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_safe_import_plan_schema={result['source_safe_import_plan_schema']}",
        f"ready_plans={summary.get('ready_plans')}",
        f"blocked_plans={summary.get('blocked_plans')}",
        f"approval_records={summary.get('approval_records')}",
        f"awaiting_manual_approval={summary.get('awaiting_manual_approval')}",
        f"approved_records={summary.get('approved_records')}",
        f"execution_unlocked_records={summary.get('execution_unlocked_records')}",
        f"copy_import_unlocked_records={summary.get('copy_import_unlocked_records')}",
        f"automatic_approvals_created={summary.get('automatic_approvals_created')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"approval_json={result['approval_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_19D_MANUAL_IMPORT_APPROVAL_GATE" if result["passed"] else "FAIL_PHASE_19D_MANUAL_IMPORT_APPROVAL_GATE")
    print(f"schema={result['schema']}")
    print(f"source_safe_import_plan_schema={result['source_safe_import_plan_schema']}")
    print(f"ready_plans={summary.get('ready_plans')}")
    print(f"blocked_plans={summary.get('blocked_plans')}")
    print(f"approval_records={summary.get('approval_records')}")
    print(f"awaiting_manual_approval={summary.get('awaiting_manual_approval')}")
    print(f"approved_records={summary.get('approved_records')}")
    print(f"execution_unlocked_records={summary.get('execution_unlocked_records')}")
    print(f"copy_import_unlocked_records={summary.get('copy_import_unlocked_records')}")
    print(f"automatic_approvals_created={summary.get('automatic_approvals_created')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"approval_json={result['approval_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
