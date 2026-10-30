from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.sorting_activation_completion_phase_23h import (
    SCHEMA,
    run_sorting_activation_completion,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_23h"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_safe_execution_sandbox_phase_23c.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_small_batch_execution_phase_23d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_rollback_validation_phase_23e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_controlled_execution_gate_phase_23f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_continuous_watch_readiness_phase_23g.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_activation_completion_phase_23h.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_activation_completion_gate_phase_23h.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    run = run_sorting_activation_completion(ROOT)
    result = run["result"]

    if run.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if result.get("programme_complete") is not True:
        failures.append("programme_not_complete")

    if result.get("completed_phase_count") != 7:
        failures.append("completed_phase_count_invalid")

    if result.get("phase_count") != 7:
        failures.append("phase_count_invalid")

    for key in [
        "controlled_execution_available",
        "manual_approval_required",
        "rollback_required",
        "small_batch_required",
        "future_watch_readiness_only",
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

    if not result.get("deterministic_completion_hash"):
        failures.append("deterministic_completion_hash_missing")

    gate_json = OUT / "sorting_activation_completion_gate_phase_23h.json"
    gate_txt = OUT / "sorting_activation_completion_gate_phase_23h.txt"

    gate = {
        "phase": "23H",
        "feature": "SORTING_ACTIVATION_COMPLETION_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "result": result,
        "failures": failures,
        "completion_notice": "PHASE_23H_COMPLETE_SORTING_ACTIVATION_SIGNED_OFF" if not failures else "PHASE_23H_BLOCKED",
        "programme_notice": "PROGRAMME_23_COMPLETE_CONTROLLED_SORTING_ACTIVATION_SIGNED_OFF" if not failures else "PROGRAMME_23_BLOCKED",
        "next_programme": "Programme 24 — Engineering Workspace Runtime",
        "next_phase": "24A_RUNTIME_SESSION_LIFECYCLE",
        "result_json": run["paths"]["json"],
        "result_report": run["paths"]["report"],
    }

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 23H SORTING ACTIVATION COMPLETION GATE",
        "================================================",
        f"passed={gate['passed']}",
        f"schema={gate['schema']}",
        f"programme_complete={result.get('programme_complete')}",
        f"completed_phase_count={result.get('completed_phase_count')}/{result.get('phase_count')}",
        f"controlled_execution_available={result.get('controlled_execution_available')}",
        f"automatic_execution_enabled={result.get('automatic_execution_enabled')}",
        f"continuous_watcher_enabled={result.get('continuous_watcher_enabled')}",
        f"delete_operations_enabled={result.get('delete_operations_enabled')}",
        f"archive_operations_enabled={result.get('archive_operations_enabled')}",
        f"active_repository_mutation_default={result.get('active_repository_mutation_default')}",
        f"manual_approval_required={result.get('manual_approval_required')}",
        f"rollback_required={result.get('rollback_required')}",
        f"small_batch_required={result.get('small_batch_required')}",
        f"future_watch_readiness_only={result.get('future_watch_readiness_only')}",
        f"blocker_count={result.get('blocker_count')}",
        f"completion_notice={gate['completion_notice']}",
        f"programme_notice={gate['programme_notice']}",
        f"next_programme={gate['next_programme']}",
        f"next_phase={gate['next_phase']}",
        f"result_json={gate['result_json']}",
        f"result_report={gate['result_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_23H_SORTING_ACTIVATION_COMPLETION" if gate["passed"] else "FAIL_PHASE_23H_SORTING_ACTIVATION_COMPLETION")
    print(f"schema={gate['schema']}")
    print(f"programme_complete={result.get('programme_complete')}")
    print(f"completed_phase_count={result.get('completed_phase_count')}/{result.get('phase_count')}")
    print(f"controlled_execution_available={result.get('controlled_execution_available')}")
    print(f"automatic_execution_enabled={result.get('automatic_execution_enabled')}")
    print(f"continuous_watcher_enabled={result.get('continuous_watcher_enabled')}")
    print(f"delete_operations_enabled={result.get('delete_operations_enabled')}")
    print(f"archive_operations_enabled={result.get('archive_operations_enabled')}")
    print(f"manual_approval_required={result.get('manual_approval_required')}")
    print(f"rollback_required={result.get('rollback_required')}")
    print(f"small_batch_required={result.get('small_batch_required')}")
    print(f"future_watch_readiness_only={result.get('future_watch_readiness_only')}")
    print(f"blocker_count={result.get('blocker_count')}")
    print(f"completion_notice={gate['completion_notice']}")
    print(f"programme_notice={gate['programme_notice']}")
    print(f"result_json={gate['result_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
