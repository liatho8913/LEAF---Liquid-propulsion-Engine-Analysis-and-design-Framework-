from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.sorting_controlled_execution_gate_phase_23f import (
    SCHEMA,
    run_controlled_execution_gate,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_23f"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_safe_execution_sandbox_phase_23c.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_small_batch_execution_phase_23d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_rollback_validation_phase_23e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_controlled_execution_gate_phase_23f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_controlled_execution_master_gate_phase_23f.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    run = run_controlled_execution_gate(ROOT)
    result = run["result"]

    if run.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    for key in [
        "phase_23c_passed",
        "phase_23d_passed",
        "phase_23e_passed",
        "controlled_execution_available",
        "rollback_required",
        "manual_approval_required",
        "small_batch_required",
        "execution_lab_validation_required",
    ]:
        if result.get(key) is not True:
            failures.append(f"required_true_failed:{key}")

    for key in [
        "automatic_execution_enabled",
        "continuous_watcher_enabled",
        "delete_operations_enabled",
        "archive_operations_enabled",
        "active_repository_mutation_default",
    ]:
        if result.get(key) is not False:
            failures.append(f"required_false_failed:{key}")

    if result.get("blocker_count") != 0:
        failures.append("blockers_detected")

    if not result.get("deterministic_gate_hash"):
        failures.append("deterministic_gate_hash_missing")

    gate_json = OUT / "sorting_controlled_execution_master_gate_phase_23f.json"
    gate_txt = OUT / "sorting_controlled_execution_master_gate_phase_23f.txt"

    gate = {
        "phase": "23F",
        "feature": "CONTROLLED_EXECUTION_MASTER_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "result": result,
        "failures": failures,
        "completion_notice": "PHASE_23F_COMPLETE_CONTROLLED_EXECUTION_GATE_ESTABLISHED" if not failures else "PHASE_23F_BLOCKED",
        "next_phase": "23G_CONTINUOUS_WATCH_READINESS",
        "result_json": run["paths"]["json"],
        "result_report": run["paths"]["report"],
    }

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 23F CONTROLLED EXECUTION MASTER GATE",
        "==============================================",
        f"passed={gate['passed']}",
        f"schema={gate['schema']}",
        f"phase_23c_passed={result.get('phase_23c_passed')}",
        f"phase_23d_passed={result.get('phase_23d_passed')}",
        f"phase_23e_passed={result.get('phase_23e_passed')}",
        f"controlled_execution_available={result.get('controlled_execution_available')}",
        f"automatic_execution_enabled={result.get('automatic_execution_enabled')}",
        f"continuous_watcher_enabled={result.get('continuous_watcher_enabled')}",
        f"delete_operations_enabled={result.get('delete_operations_enabled')}",
        f"archive_operations_enabled={result.get('archive_operations_enabled')}",
        f"rollback_required={result.get('rollback_required')}",
        f"manual_approval_required={result.get('manual_approval_required')}",
        f"small_batch_required={result.get('small_batch_required')}",
        f"active_repository_mutation_default={result.get('active_repository_mutation_default')}",
        f"execution_lab_validation_required={result.get('execution_lab_validation_required')}",
        f"blocker_count={result.get('blocker_count')}",
        f"completion_notice={gate['completion_notice']}",
        f"next_phase={gate['next_phase']}",
        f"result_json={gate['result_json']}",
        f"result_report={gate['result_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_23F_CONTROLLED_EXECUTION_GATE" if gate["passed"] else "FAIL_PHASE_23F_CONTROLLED_EXECUTION_GATE")
    print(f"schema={gate['schema']}")
    print(f"phase_23c_passed={result.get('phase_23c_passed')}")
    print(f"phase_23d_passed={result.get('phase_23d_passed')}")
    print(f"phase_23e_passed={result.get('phase_23e_passed')}")
    print(f"controlled_execution_available={result.get('controlled_execution_available')}")
    print(f"automatic_execution_enabled={result.get('automatic_execution_enabled')}")
    print(f"continuous_watcher_enabled={result.get('continuous_watcher_enabled')}")
    print(f"delete_operations_enabled={result.get('delete_operations_enabled')}")
    print(f"archive_operations_enabled={result.get('archive_operations_enabled')}")
    print(f"rollback_required={result.get('rollback_required')}")
    print(f"manual_approval_required={result.get('manual_approval_required')}")
    print(f"small_batch_required={result.get('small_batch_required')}")
    print(f"active_repository_mutation_default={result.get('active_repository_mutation_default')}")
    print(f"execution_lab_validation_required={result.get('execution_lab_validation_required')}")
    print(f"blocker_count={result.get('blocker_count')}")
    print(f"completion_notice={gate['completion_notice']}")
    print(f"result_json={gate['result_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
