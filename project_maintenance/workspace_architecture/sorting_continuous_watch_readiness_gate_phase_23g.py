from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.sorting_continuous_watch_readiness_phase_23g import (
    SCHEMA,
    run_continuous_watch_readiness,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_23g"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_controlled_execution_gate_phase_23f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_controlled_execution_master_gate_phase_23f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_continuous_watch_readiness_phase_23g.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_continuous_watch_readiness_gate_phase_23g.py",
]

FORBIDDEN_WATCH_MARKERS = [
    "watchdog",
    "Observer(",
    "schedule(",
    "while True",
    "time.sleep",
    "threading.Thread",
    "asyncio.create_task",
    "multiprocessing",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    readiness_source = (ROOT / "project_maintenance" / "workspace_architecture" / "sorting_continuous_watch_readiness_phase_23g.py").read_text(encoding="utf-8")
    for marker in FORBIDDEN_WATCH_MARKERS:
        if marker in readiness_source:
            failures.append(f"forbidden_watch_marker_present:{marker}")

    run = run_continuous_watch_readiness(ROOT)
    result = run["result"]

    if run.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    for key in [
        "phase_23f_passed",
        "controlled_execution_available",
        "continuous_watch_ready_for_future_design",
        "manual_approval_required",
        "rollback_required",
        "small_batch_required",
        "controlled_execution_gate_required",
        "readiness_only",
    ]:
        if result.get(key) is not True:
            failures.append(f"required_true_failed:{key}")

    for key in [
        "continuous_watcher_enabled",
        "automatic_execution_enabled",
        "filesystem_monitor_created",
        "polling_loop_created",
        "background_task_created",
        "mutation_allowed_from_watch",
    ]:
        if result.get(key) is not False:
            failures.append(f"required_false_failed:{key}")

    if result.get("blocker_count") != 0:
        failures.append("blockers_detected")

    if not result.get("deterministic_readiness_hash"):
        failures.append("deterministic_readiness_hash_missing")

    gate_json = OUT / "sorting_continuous_watch_readiness_gate_phase_23g.json"
    gate_txt = OUT / "sorting_continuous_watch_readiness_gate_phase_23g.txt"

    gate = {
        "phase": "23G",
        "feature": "CONTINUOUS_WATCH_READINESS_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "result": result,
        "forbidden_watch_markers_checked": FORBIDDEN_WATCH_MARKERS,
        "failures": failures,
        "completion_notice": "PHASE_23G_COMPLETE_CONTINUOUS_WATCH_READINESS_ESTABLISHED" if not failures else "PHASE_23G_BLOCKED",
        "next_phase": "23H_SORTING_ACTIVATION_COMPLETION",
        "result_json": run["paths"]["json"],
        "result_report": run["paths"]["report"],
    }

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 23G CONTINUOUS WATCH READINESS GATE",
        "==============================================",
        f"passed={gate['passed']}",
        f"schema={gate['schema']}",
        f"phase_23f_passed={result.get('phase_23f_passed')}",
        f"controlled_execution_available={result.get('controlled_execution_available')}",
        f"continuous_watch_ready_for_future_design={result.get('continuous_watch_ready_for_future_design')}",
        f"continuous_watcher_enabled={result.get('continuous_watcher_enabled')}",
        f"automatic_execution_enabled={result.get('automatic_execution_enabled')}",
        f"filesystem_monitor_created={result.get('filesystem_monitor_created')}",
        f"polling_loop_created={result.get('polling_loop_created')}",
        f"background_task_created={result.get('background_task_created')}",
        f"mutation_allowed_from_watch={result.get('mutation_allowed_from_watch')}",
        f"manual_approval_required={result.get('manual_approval_required')}",
        f"rollback_required={result.get('rollback_required')}",
        f"small_batch_required={result.get('small_batch_required')}",
        f"controlled_execution_gate_required={result.get('controlled_execution_gate_required')}",
        f"readiness_only={result.get('readiness_only')}",
        f"blocker_count={result.get('blocker_count')}",
        f"completion_notice={gate['completion_notice']}",
        f"next_phase={gate['next_phase']}",
        f"result_json={gate['result_json']}",
        f"result_report={gate['result_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_23G_CONTINUOUS_WATCH_READINESS" if gate["passed"] else "FAIL_PHASE_23G_CONTINUOUS_WATCH_READINESS")
    print(f"schema={gate['schema']}")
    print(f"phase_23f_passed={result.get('phase_23f_passed')}")
    print(f"controlled_execution_available={result.get('controlled_execution_available')}")
    print(f"continuous_watch_ready_for_future_design={result.get('continuous_watch_ready_for_future_design')}")
    print(f"continuous_watcher_enabled={result.get('continuous_watcher_enabled')}")
    print(f"automatic_execution_enabled={result.get('automatic_execution_enabled')}")
    print(f"filesystem_monitor_created={result.get('filesystem_monitor_created')}")
    print(f"polling_loop_created={result.get('polling_loop_created')}")
    print(f"background_task_created={result.get('background_task_created')}")
    print(f"mutation_allowed_from_watch={result.get('mutation_allowed_from_watch')}")
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
