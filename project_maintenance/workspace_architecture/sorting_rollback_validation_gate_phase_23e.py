from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.sorting_rollback_validation_phase_23e import (
    SCHEMA,
    SortingRollbackValidationEngine,
    run_sorting_rollback_validation,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_23e"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_small_batch_execution_phase_23d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_rollback_validation_phase_23e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_rollback_validation_gate_phase_23e.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    run = run_sorting_rollback_validation(ROOT)
    result = run["result"]

    if run.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if run.get("source_execution_schema") != "LEAF_SORTING_SMALL_BATCH_EXECUTION_PHASE_23D_V1":
        failures.append("source_execution_schema_invalid")

    for key in [
        "execution_passed",
        "rollback_performed",
        "repository_restored",
        "execution_lab_only",
        "passed",
    ]:
        if result.get(key) is not True:
            failures.append(f"required_true_failed:{key}")

    for key in [
        "active_repository_mutated",
        "delete_operations_performed",
        "archive_operations_performed",
        "automatic_execution",
        "continuous_watcher",
    ]:
        if result.get(key) is not False:
            failures.append(f"required_false_failed:{key}")

    if result.get("rollback_operation_count") != 3:
        failures.append("rollback_operation_count_invalid")

    if result.get("blocker_count") != 0:
        failures.append("blockers_detected")

    if result.get("before_state_hash") != result.get("after_rollback_state_hash"):
        failures.append("rollback_hash_mismatch")

    if result.get("before_state_hash") == result.get("after_execution_state_hash"):
        failures.append("execution_did_not_change_state")

    if not result.get("deterministic_result_hash"):
        failures.append("deterministic_result_hash_missing")

    engine = SortingRollbackValidationEngine(ROOT)
    plan = engine.execution_engine.build_small_batch_plan()
    execution_result = engine.execution_engine.execute_plan(plan)
    engine.execution_engine.write_result(execution_result)

    manifests = sorted(engine.execution_engine.rollback_root.glob("*_rollback_manifest.json"))
    if manifests:
        manifests[0].unlink()

    missing_manifest_blockers = engine.restore_from_rollback_manifests()
    if not missing_manifest_blockers:
        failures.append("missing_manifest_negative_test_failed")

    gate_json = OUT / "sorting_rollback_validation_gate_phase_23e.json"
    gate_txt = OUT / "sorting_rollback_validation_gate_phase_23e.txt"

    gate = {
        "phase": "23E",
        "feature": "SORTING_ROLLBACK_VALIDATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "result": result,
        "negative_tests": {
            "missing_manifest_blockers": list(missing_manifest_blockers),
        },
        "failures": failures,
        "completion_notice": "PHASE_23E_COMPLETE_ROLLBACK_VALIDATION_ESTABLISHED" if not failures else "PHASE_23E_BLOCKED",
        "next_phase": "23F_CONTROLLED_EXECUTION_GATE",
        "result_json": run["paths"]["json"],
        "result_report": run["paths"]["report"],
    }

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 23E ROLLBACK VALIDATION GATE",
        "======================================",
        f"passed={gate['passed']}",
        f"schema={gate['schema']}",
        f"source_execution_schema={run.get('source_execution_schema')}",
        f"execution_passed={result.get('execution_passed')}",
        f"rollback_performed={result.get('rollback_performed')}",
        f"rollback_operation_count={result.get('rollback_operation_count')}",
        f"before_state_hash={result.get('before_state_hash')}",
        f"after_execution_state_hash={result.get('after_execution_state_hash')}",
        f"after_rollback_state_hash={result.get('after_rollback_state_hash')}",
        f"repository_restored={result.get('repository_restored')}",
        f"active_repository_mutated={result.get('active_repository_mutated')}",
        f"execution_lab_only={result.get('execution_lab_only')}",
        f"delete_operations_performed={result.get('delete_operations_performed')}",
        f"archive_operations_performed={result.get('archive_operations_performed')}",
        f"automatic_execution={result.get('automatic_execution')}",
        f"continuous_watcher={result.get('continuous_watcher')}",
        f"blocker_count={result.get('blocker_count')}",
        f"missing_manifest_negative_blockers={len(missing_manifest_blockers)}",
        f"completion_notice={gate['completion_notice']}",
        f"next_phase={gate['next_phase']}",
        f"result_json={gate['result_json']}",
        f"result_report={gate['result_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_23E_ROLLBACK_VALIDATION" if gate["passed"] else "FAIL_PHASE_23E_ROLLBACK_VALIDATION")
    print(f"schema={gate['schema']}")
    print(f"source_execution_schema={run.get('source_execution_schema')}")
    print(f"execution_passed={result.get('execution_passed')}")
    print(f"rollback_performed={result.get('rollback_performed')}")
    print(f"rollback_operation_count={result.get('rollback_operation_count')}")
    print(f"repository_restored={result.get('repository_restored')}")
    print(f"active_repository_mutated={result.get('active_repository_mutated')}")
    print(f"execution_lab_only={result.get('execution_lab_only')}")
    print(f"blocker_count={result.get('blocker_count')}")
    print(f"missing_manifest_negative_blockers={len(missing_manifest_blockers)}")
    print(f"completion_notice={gate['completion_notice']}")
    print(f"result_json={gate['result_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
