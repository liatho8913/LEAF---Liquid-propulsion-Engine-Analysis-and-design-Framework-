from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.sorting_activation_readiness_audit_phase_23a import (
    SCHEMA,
    write_sorting_activation_readiness_audit,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_23a"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_activation_readiness_audit_phase_23a.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_activation_readiness_audit_gate_phase_23a.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    written = write_sorting_activation_readiness_audit(ROOT)
    audit = written["audit"]
    summary = audit["summary"]

    if audit.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if summary.get("required_gates_checked") != 4:
        failures.append("required_gates_checked_invalid")

    if summary.get("required_gates_passed") < 2:
        failures.append("critical_recent_programme_gates_not_passed")

    for key in [
        "audit_only",
        "manual_approval_required_before_execution",
        "rollback_required_before_execution",
        "small_batch_required_before_bulk",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true:{key}")

    for key in [
        "ready_for_direct_execution",
        "ready_for_automatic_sorting",
        "ready_for_continuous_watcher",
        "imports_files",
        "copies_files",
        "moves_files",
        "deletes_files",
        "archives_files",
        "automatic_sorting_activation",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false:{key}")

    # 23A may pass with blockers. The purpose is to record readiness honestly.
    # 23B should only proceed if ready_for_23b_user_approval_rules is True.
    if summary.get("ready_for_23b_user_approval_rules") is not True:
        failures.append("not_ready_for_23b_user_approval_rules")

    result = {
        "phase": "23A",
        "feature": "SORTING_ACTIVATION_READINESS_AUDIT",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": summary,
        "blockers": audit.get("blockers", []),
        "audit_json": written["json_path"],
        "audit_report": written["txt_path"],
        "failures": failures,
        "completion_notice": "PHASE_23A_COMPLETE_SORTING_ACTIVATION_READINESS_AUDIT_ESTABLISHED" if not failures else "PHASE_23A_BLOCKED",
        "next_phase": "23B_USER_APPROVAL_RULES",
    }

    gate_json = OUT / "sorting_activation_readiness_audit_gate_phase_23a.json"
    gate_txt = OUT / "sorting_activation_readiness_audit_gate_phase_23a.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 23A SORTING ACTIVATION READINESS AUDIT GATE",
        "======================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"required_gates_checked={summary.get('required_gates_checked')}",
        f"required_gates_passed={summary.get('required_gates_passed')}",
        f"blocker_count={summary.get('blocker_count')}",
        f"audit_only={summary.get('audit_only')}",
        f"manual_approval_required_before_execution={summary.get('manual_approval_required_before_execution')}",
        f"rollback_required_before_execution={summary.get('rollback_required_before_execution')}",
        f"small_batch_required_before_bulk={summary.get('small_batch_required_before_bulk')}",
        f"ready_for_direct_execution={summary.get('ready_for_direct_execution')}",
        f"ready_for_automatic_sorting={summary.get('ready_for_automatic_sorting')}",
        f"ready_for_continuous_watcher={summary.get('ready_for_continuous_watcher')}",
        f"ready_for_23b_user_approval_rules={summary.get('ready_for_23b_user_approval_rules')}",
        f"imports_files={summary.get('imports_files')}",
        f"copies_files={summary.get('copies_files')}",
        f"moves_files={summary.get('moves_files')}",
        f"deletes_files={summary.get('deletes_files')}",
        f"archives_files={summary.get('archives_files')}",
        f"automatic_sorting_activation={summary.get('automatic_sorting_activation')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"audit_json={result['audit_json']}",
        f"audit_report={result['audit_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_23A_SORTING_ACTIVATION_READINESS_AUDIT" if result["passed"] else "FAIL_PHASE_23A_SORTING_ACTIVATION_READINESS_AUDIT")
    print(f"schema={result['schema']}")
    print(f"required_gates_checked={summary.get('required_gates_checked')}")
    print(f"required_gates_passed={summary.get('required_gates_passed')}")
    print(f"blocker_count={summary.get('blocker_count')}")
    print(f"audit_only={summary.get('audit_only')}")
    print(f"manual_approval_required_before_execution={summary.get('manual_approval_required_before_execution')}")
    print(f"rollback_required_before_execution={summary.get('rollback_required_before_execution')}")
    print(f"small_batch_required_before_bulk={summary.get('small_batch_required_before_bulk')}")
    print(f"ready_for_direct_execution={summary.get('ready_for_direct_execution')}")
    print(f"ready_for_automatic_sorting={summary.get('ready_for_automatic_sorting')}")
    print(f"ready_for_continuous_watcher={summary.get('ready_for_continuous_watcher')}")
    print(f"ready_for_23b_user_approval_rules={summary.get('ready_for_23b_user_approval_rules')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"audit_json={result['audit_json']}")
    print(f"audit_report={result['audit_report']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
