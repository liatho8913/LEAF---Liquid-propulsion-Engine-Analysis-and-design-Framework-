from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.import_verification_rollback_snapshot_phase_19f import (
    SCHEMA,
    build_import_verification_rollback_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_19f"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "controlled_import_execution_phase_19e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "import_verification_rollback_snapshot_phase_19f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "import_verification_rollback_snapshot_gate_phase_19f.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    snapshot = build_import_verification_rollback_snapshot(ROOT)
    summary = snapshot["summary"]
    policy = snapshot["execution_policy"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if snapshot.get("source_execution_schema") != "LEAF_CONTROLLED_IMPORT_EXECUTION_PHASE_19E_V1":
        failures.append("source_execution_schema_invalid")

    if snapshot.get("source_execution_mode") != "DRY_RUN_VALIDATION":
        failures.append("source_execution_mode_not_dry_run")

    for key in [
        "verification_is_read_only",
        "creates_rollback_snapshot_only",
        "manual_rollback_required",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "imports_files",
        "copies_files",
        "moves_existing_files",
        "deletes_files",
        "archives_files",
        "rollback_execution_allowed",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    for key in [
        "verification_failures",
        "delete_operations_created",
        "move_operations_created",
        "archive_operations_created",
    ]:
        if summary.get(key) != 0:
            failures.append(f"unsafe_or_failure_summary_nonzero={key}")

    if summary.get("executed_records") == 0:
        if summary.get("safe_no_op_state") is not True:
            failures.append("safe_no_op_state_not_true_when_no_execution")
        if summary.get("rollback_records") != 0:
            failures.append("rollback_records_created_for_no_op")
        if summary.get("verification_records") != 0:
            failures.append("verification_records_created_for_no_op")

    for review_id, item in snapshot.get("rollback_records", {}).items():
        if item.get("rollback_automatic_execution_allowed") is not False:
            failures.append(f"rollback_auto_execution_allowed={review_id}")
        if item.get("source_preserved") is not True:
            failures.append(f"rollback_source_not_preserved={review_id}")
        for key in [
            "delete_original_allowed",
            "move_original_allowed",
            "archive_original_allowed",
        ]:
            if item.get(key) is not False:
                failures.append(f"rollback_unsafe_flag_not_false={review_id}:{key}")

    snapshot_path = OUT / "import_verification_rollback_snapshot_phase_19f.json"
    gate_json = OUT / "import_verification_rollback_snapshot_gate_phase_19f.json"
    gate_txt = OUT / "import_verification_rollback_snapshot_gate_phase_19f.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    result = {
        "phase": "19F",
        "feature": "IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": snapshot.get("schema"),
        "source_execution_schema": snapshot.get("source_execution_schema"),
        "source_execution_mode": snapshot.get("source_execution_mode"),
        "summary": summary,
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_19F_COMPLETE_IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT_ESTABLISHED" if not failures else "PHASE_19F_BLOCKED",
        "next_phase": "19G_SORTING_INTEGRATION_COMPLETION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 19F IMPORT VERIFICATION ROLLBACK SNAPSHOT",
        "======================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_execution_schema={result['source_execution_schema']}",
        f"source_execution_mode={result['source_execution_mode']}",
        f"executed_records={summary.get('executed_records')}",
        f"verification_records={summary.get('verification_records')}",
        f"rollback_records={summary.get('rollback_records')}",
        f"verified_imports={summary.get('verified_imports')}",
        f"verification_failures={summary.get('verification_failures')}",
        f"safe_no_op_state={summary.get('safe_no_op_state')}",
        f"rollback_execution_allowed={summary.get('rollback_execution_allowed')}",
        f"delete_operations_created={summary.get('delete_operations_created')}",
        f"move_operations_created={summary.get('move_operations_created')}",
        f"archive_operations_created={summary.get('archive_operations_created')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_19F_IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT" if result["passed"] else "FAIL_PHASE_19F_IMPORT_VERIFICATION_ROLLBACK_SNAPSHOT")
    print(f"schema={result['schema']}")
    print(f"source_execution_schema={result['source_execution_schema']}")
    print(f"source_execution_mode={result['source_execution_mode']}")
    print(f"executed_records={summary.get('executed_records')}")
    print(f"verification_records={summary.get('verification_records')}")
    print(f"rollback_records={summary.get('rollback_records')}")
    print(f"verified_imports={summary.get('verified_imports')}")
    print(f"verification_failures={summary.get('verification_failures')}")
    print(f"safe_no_op_state={summary.get('safe_no_op_state')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
