from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.sorting_safe_execution_sandbox_phase_23c import (
    SortingSafeExecutionSandbox,
)
from project_maintenance.workspace_architecture.sorting_small_batch_execution_phase_23d import (
    SCHEMA,
    SMALL_BATCH_LIMIT,
    SortingSmallBatchExecutionEngine,
    run_sorting_small_batch_execution,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_23d"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_safe_execution_sandbox_phase_23c.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_small_batch_execution_phase_23d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_small_batch_execution_gate_phase_23d.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    run = run_sorting_small_batch_execution(ROOT)
    result = run["result"]

    required_true = [
        "execution_lab_only",
        "rollback_manifest_created",
        "passed",
    ]
    required_false = [
        "active_repository_mutated",
        "delete_operations_performed",
        "archive_operations_performed",
        "automatic_execution",
        "continuous_watcher",
    ]

    if run.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if run.get("source_sandbox_schema") != "LEAF_SORTING_SAFE_EXECUTION_SANDBOX_PHASE_23C_V2":
        failures.append("source_sandbox_schema_invalid")

    if result.get("operation_count") != 3:
        failures.append("operation_count_invalid")

    if result.get("operation_count") > SMALL_BATCH_LIMIT:
        failures.append("small_batch_limit_exceeded")

    if result.get("executed_operation_count") != result.get("operation_count"):
        failures.append("executed_operation_count_invalid")

    if result.get("blocker_count") != 0:
        failures.append("blockers_detected")

    for key in required_true:
        if result.get(key) is not True:
            failures.append(f"required_true_failed:{key}")

    for key in required_false:
        if result.get(key) is not False:
            failures.append(f"required_false_failed:{key}")

    operation_types = sorted({operation["operation_type"] for operation in result.get("operations", [])})
    if operation_types != ["copy", "import_route", "move"]:
        failures.append(f"operation_type_coverage_invalid:{operation_types}")

    if not result.get("deterministic_result_hash"):
        failures.append("deterministic_result_hash_missing")

    engine = SortingSmallBatchExecutionEngine(ROOT)

    outside_plan = engine.build_small_batch_plan()
    outside_operation = SortingSafeExecutionSandbox(ROOT).build_operation(
        operation_id="small_batch_outside_repo_001",
        source_path="leaf_qt/main_window.py",
        destination_path="_leaf_artifacts/workspace_architecture/phase_23d/execution_lab/destination/main_window.py",
        operation_type="copy",
        approved=True,
        snapshot_available=True,
    )
    outside_plan = type(outside_plan)(
        plan_id="outside_plan",
        batch_id="outside_batch",
        operations=(outside_operation,),
        small_batch_limit=SMALL_BATCH_LIMIT,
        simulation_only=False,
        real_filesystem_mutation_allowed=True,
        automatic_execution=False,
        continuous_watcher=False,
        delete_operations_allowed=False,
        archive_operations_allowed=False,
    )
    outside_blockers = engine.validate_plan_for_small_batch_execution(outside_plan)
    if not any("source_outside_execution_lab" in blocker for blocker in outside_blockers):
        failures.append("outside_execution_lab_negative_test_failed")

    delete_plan = engine.build_small_batch_plan()
    delete_operation = SortingSafeExecutionSandbox(ROOT).build_operation(
        operation_id="small_batch_delete_forbidden_001",
        source_path="_leaf_artifacts/workspace_architecture/phase_23d/execution_lab/source/delete_forbidden.py",
        destination_path="_leaf_artifacts/workspace_architecture/phase_23d/execution_lab/destination/delete_forbidden.py",
        operation_type="delete",
        approved=True,
        snapshot_available=True,
    )
    delete_source = ROOT / delete_operation.source_path
    delete_source.parent.mkdir(parents=True, exist_ok=True)
    delete_source.write_text("print('delete forbidden')\n", encoding="utf-8")

    delete_plan = type(delete_plan)(
        plan_id="delete_plan",
        batch_id="delete_batch",
        operations=(delete_operation,),
        small_batch_limit=SMALL_BATCH_LIMIT,
        simulation_only=False,
        real_filesystem_mutation_allowed=True,
        automatic_execution=False,
        continuous_watcher=False,
        delete_operations_allowed=False,
        archive_operations_allowed=False,
    )
    delete_blockers = engine.validate_plan_for_small_batch_execution(delete_plan)
    if not any("forbidden_operation_type" in blocker for blocker in delete_blockers):
        failures.append("delete_negative_test_failed")

    too_many_operations = tuple(delete_plan.operations * 6)
    too_many_plan = type(delete_plan)(
        plan_id="too_many_plan",
        batch_id="too_many_batch",
        operations=too_many_operations,
        small_batch_limit=SMALL_BATCH_LIMIT,
        simulation_only=False,
        real_filesystem_mutation_allowed=True,
        automatic_execution=False,
        continuous_watcher=False,
        delete_operations_allowed=False,
        archive_operations_allowed=False,
    )
    too_many_blockers = engine.validate_plan_for_small_batch_execution(too_many_plan)
    if not any("small_batch_limit_exceeded" in blocker for blocker in too_many_blockers):
        failures.append("too_many_operations_negative_test_failed")

    gate_json = OUT / "sorting_small_batch_execution_gate_phase_23d.json"
    gate_txt = OUT / "sorting_small_batch_execution_gate_phase_23d.txt"

    gate = {
        "phase": "23D",
        "feature": "SORTING_SMALL_BATCH_EXECUTION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "result": result,
        "negative_tests": {
            "outside_execution_lab_blockers": list(outside_blockers),
            "delete_blockers": list(delete_blockers),
            "too_many_blockers": list(too_many_blockers),
        },
        "failures": failures,
        "completion_notice": "PHASE_23D_COMPLETE_SMALL_BATCH_EXECUTION_ESTABLISHED" if not failures else "PHASE_23D_BLOCKED",
        "next_phase": "23E_ROLLBACK_VALIDATION",
        "result_json": run["paths"]["json"],
        "result_report": run["paths"]["report"],
    }

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 23D SMALL BATCH EXECUTION GATE",
        "=========================================",
        f"passed={gate['passed']}",
        f"schema={gate['schema']}",
        f"source_sandbox_schema={run.get('source_sandbox_schema')}",
        f"operation_count={result.get('operation_count')}",
        f"executed_operation_count={result.get('executed_operation_count')}",
        f"execution_lab_root={result.get('execution_lab_root')}",
        f"active_repository_mutated={result.get('active_repository_mutated')}",
        f"execution_lab_only={result.get('execution_lab_only')}",
        f"delete_operations_performed={result.get('delete_operations_performed')}",
        f"archive_operations_performed={result.get('archive_operations_performed')}",
        f"automatic_execution={result.get('automatic_execution')}",
        f"continuous_watcher={result.get('continuous_watcher')}",
        f"rollback_manifest_created={result.get('rollback_manifest_created')}",
        f"blocker_count={result.get('blocker_count')}",
        f"deterministic_result_hash={result.get('deterministic_result_hash')}",
        f"outside_execution_lab_negative_blockers={len(outside_blockers)}",
        f"delete_negative_blockers={len(delete_blockers)}",
        f"too_many_negative_blockers={len(too_many_blockers)}",
        f"completion_notice={gate['completion_notice']}",
        f"next_phase={gate['next_phase']}",
        f"result_json={gate['result_json']}",
        f"result_report={gate['result_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_23D_SMALL_BATCH_EXECUTION" if gate["passed"] else "FAIL_PHASE_23D_SMALL_BATCH_EXECUTION")
    print(f"schema={gate['schema']}")
    print(f"source_sandbox_schema={run.get('source_sandbox_schema')}")
    print(f"operation_count={result.get('operation_count')}")
    print(f"executed_operation_count={result.get('executed_operation_count')}")
    print(f"execution_lab_root={result.get('execution_lab_root')}")
    print(f"active_repository_mutated={result.get('active_repository_mutated')}")
    print(f"execution_lab_only={result.get('execution_lab_only')}")
    print(f"delete_operations_performed={result.get('delete_operations_performed')}")
    print(f"archive_operations_performed={result.get('archive_operations_performed')}")
    print(f"automatic_execution={result.get('automatic_execution')}")
    print(f"continuous_watcher={result.get('continuous_watcher')}")
    print(f"rollback_manifest_created={result.get('rollback_manifest_created')}")
    print(f"blocker_count={result.get('blocker_count')}")
    print(f"outside_execution_lab_negative_blockers={len(outside_blockers)}")
    print(f"delete_negative_blockers={len(delete_blockers)}")
    print(f"too_many_negative_blockers={len(too_many_blockers)}")
    print(f"completion_notice={gate['completion_notice']}")
    print(f"result_json={gate['result_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
