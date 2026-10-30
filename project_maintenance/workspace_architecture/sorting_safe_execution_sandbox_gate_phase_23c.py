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
    SCHEMA,
    SUPPORTED_SIMULATED_OPERATIONS,
    SortingSafeExecutionSandbox,
    write_sorting_safe_execution_sandbox,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_23c"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_user_approval_rules_phase_23b.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_safe_execution_sandbox_phase_23c.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_safe_execution_sandbox_gate_phase_23c.py",
]

FORBIDDEN_SOURCE_MARKERS = [
    "shutil.move",
    "shutil.copy",
    "copyfile(",
    "copy2(",
    ".rename(",
    ".replace(",
    ".unlink(",
    ".rmdir(",
    "os.remove(",
    "os.unlink(",
    "os.rename(",
    "os.replace(",
    "send2trash",
]


def _source_safety_failures() -> list[str]:
    failures: list[str] = []
    sandbox_source = MODULES[1].read_text(encoding="utf-8")
    for marker in FORBIDDEN_SOURCE_MARKERS:
        if marker in sandbox_source:
            failures.append(f"forbidden_mutation_marker_present:{marker}")
    return failures


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    failures.extend(_source_safety_failures())

    written = write_sorting_safe_execution_sandbox(ROOT)
    snapshot = written["snapshot"]
    summary = snapshot["summary"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if snapshot.get("source_approval_rules_schema") != "LEAF_SORTING_USER_APPROVAL_RULES_PHASE_23B_V1":
        failures.append("source_approval_rules_schema_invalid")

    expected_models = {
        "plan_model",
        "operation_model",
        "approval_model",
        "rollback_model",
        "result_model",
        "log_model",
    }
    if set(snapshot.get("execution_model", {})) != expected_models:
        failures.append("execution_model_set_invalid")

    if summary.get("operation_count") != 3:
        failures.append("operation_count_invalid")

    if summary.get("simulated_operation_count") != summary.get("operation_count"):
        failures.append("simulated_operation_count_invalid")

    if summary.get("rollback_reference_count") != summary.get("operation_count"):
        failures.append("rollback_reference_count_invalid")

    if summary.get("blocker_count") != 0:
        failures.append("sandbox_blockers_detected")

    if summary.get("operation_types") != sorted(SUPPORTED_SIMULATED_OPERATIONS):
        failures.append("operation_type_coverage_invalid")

    for key in [
        "sandbox_passed",
        "manual_approval_required",
        "rollback_snapshot_required",
        "small_batch_limit_required",
        "simulation_only",
        "ready_for_23d_small_batch_execution",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true:{key}")

    for key in [
        "real_filesystem_mutation_performed",
        "imports_files",
        "copies_real_files",
        "moves_real_files",
        "deletes_files",
        "archives_files",
        "automatic_execution",
        "continuous_watcher",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false:{key}")

    if not summary.get("plan_hash") or not summary.get("result_hash"):
        failures.append("deterministic_hashes_missing")

    sandbox = SortingSafeExecutionSandbox(ROOT)
    bad_operation = sandbox.build_operation(
        operation_id="sandbox_bad_delete_001",
        source_path="leaf_qt/bad.py",
        destination_path="leaf_qt/bad_deleted.py",
        operation_type="delete",
        approved=True,
        snapshot_available=True,
    )

    sample = sandbox.build_sample_plan()
    bad_plan = type(sample)(
        plan_id="bad_plan_delete_forbidden",
        batch_id="bad_batch_delete_forbidden",
        operations=(bad_operation,),
    )

    bad_log = sandbox.simulate_plan(bad_plan)
    if bad_log.sandbox_passed is not False:
        failures.append("negative_delete_plan_did_not_fail")
    if not any("forbidden_operation_type" in blocker for blocker in bad_log.blockers):
        failures.append("negative_delete_blocker_missing")
    if bad_log.real_filesystem_mutation_performed is not False:
        failures.append("negative_plan_mutated_filesystem")

    gate_json = OUT / "sorting_safe_execution_sandbox_gate_phase_23c.json"
    gate_txt = OUT / "sorting_safe_execution_sandbox_gate_phase_23c.txt"

    result = {
        "phase": "23C",
        "feature": "SORTING_SAFE_EXECUTION_SANDBOX",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": summary,
        "source_safety_markers_checked": FORBIDDEN_SOURCE_MARKERS,
        "negative_delete_plan_blockers": list(bad_log.blockers),
        "failures": failures,
        "snapshot_json": written["json_path"],
        "snapshot_report": written["txt_path"],
        "completion_notice": "PHASE_23C_COMPLETE_SAFE_EXECUTION_SANDBOX_ESTABLISHED" if not failures else "PHASE_23C_BLOCKED",
        "next_phase": "23D_SMALL_BATCH_EXECUTION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 23C SAFE EXECUTION SANDBOX GATE",
        "==========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_approval_rules_schema={snapshot.get('source_approval_rules_schema')}",
        f"sandbox_class={summary.get('sandbox_class')}",
        f"sandbox_root={summary.get('sandbox_root')}",
        f"plan_id={summary.get('plan_id')}",
        f"batch_id={summary.get('batch_id')}",
        f"operation_count={summary.get('operation_count')}",
        f"simulated_operation_count={summary.get('simulated_operation_count')}",
        f"rollback_reference_count={summary.get('rollback_reference_count')}",
        f"blocker_count={summary.get('blocker_count')}",
        f"sandbox_passed={summary.get('sandbox_passed')}",
        f"manual_approval_required={summary.get('manual_approval_required')}",
        f"rollback_snapshot_required={summary.get('rollback_snapshot_required')}",
        f"small_batch_limit_required={summary.get('small_batch_limit_required')}",
        f"simulation_only={summary.get('simulation_only')}",
        f"real_filesystem_mutation_performed={summary.get('real_filesystem_mutation_performed')}",
        f"imports_files={summary.get('imports_files')}",
        f"copies_real_files={summary.get('copies_real_files')}",
        f"moves_real_files={summary.get('moves_real_files')}",
        f"deletes_files={summary.get('deletes_files')}",
        f"archives_files={summary.get('archives_files')}",
        f"automatic_execution={summary.get('automatic_execution')}",
        f"continuous_watcher={summary.get('continuous_watcher')}",
        f"plan_hash={summary.get('plan_hash')}",
        f"result_hash={summary.get('result_hash')}",
        f"ready_for_23d_small_batch_execution={summary.get('ready_for_23d_small_batch_execution')}",
        f"negative_delete_plan_blockers={len(bad_log.blockers)}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"snapshot_report={result['snapshot_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_23C_SAFE_EXECUTION_SANDBOX" if result["passed"] else "FAIL_PHASE_23C_SAFE_EXECUTION_SANDBOX")
    print(f"schema={result['schema']}")
    print(f"source_approval_rules_schema={snapshot.get('source_approval_rules_schema')}")
    print(f"sandbox_class={summary.get('sandbox_class')}")
    print(f"operation_count={summary.get('operation_count')}")
    print(f"simulated_operation_count={summary.get('simulated_operation_count')}")
    print(f"rollback_reference_count={summary.get('rollback_reference_count')}")
    print(f"blocker_count={summary.get('blocker_count')}")
    print(f"sandbox_passed={summary.get('sandbox_passed')}")
    print(f"simulation_only={summary.get('simulation_only')}")
    print(f"real_filesystem_mutation_performed={summary.get('real_filesystem_mutation_performed')}")
    print(f"negative_delete_plan_blockers={len(bad_log.blockers)}")
    print(f"ready_for_23d_small_batch_execution={summary.get('ready_for_23d_small_batch_execution')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
