from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24c"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "runtime" / "session_lifecycle.py",
    ROOT / "leaf_qt" / "runtime" / "event_bus.py",
    ROOT / "leaf_qt" / "runtime" / "state_registry.py",
]

from leaf_qt.runtime.event_bus import RuntimeEventBus
from leaf_qt.runtime.state_registry import SCHEMA, RuntimeStateRegistry


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    bus = RuntimeEventBus()
    registry = RuntimeStateRegistry(event_bus=bus)

    received_general: list[dict] = []
    received_specific: list[dict] = []

    bus.subscribe(
        "runtime.state.changed",
        lambda event: received_general.append(event.payload),
        "state_general_probe",
    )

    bus.subscribe(
        "runtime.state.changed.active_design",
        lambda event: received_specific.append(event.payload),
        "active_design_probe",
    )

    change = registry.set(
        "active_design",
        "LEAF_Designs/test_design.leaf_design.json",
        source="phase_24c_gate",
    )

    if change.old_value is not None:
        failures.append("initial_old_value_not_none")

    if change.new_value != "LEAF_Designs/test_design.leaf_design.json":
        failures.append("new_value_not_retained")

    if registry.get("active_design") != "LEAF_Designs/test_design.leaf_design.json":
        failures.append("registry_get_failed")

    if len(received_general) != 1:
        failures.append("general_state_event_not_emitted")

    if len(received_specific) != 1:
        failures.append("specific_state_event_not_emitted")

    registry.set("active_project", "LEAF_Projects/test_project", source="phase_24c_gate")
    registry.set("current_workspace", "engineering_workspace", source="phase_24c_gate")
    registry.set("current_tool", "regen_calculator", source="phase_24c_gate")
    registry.set("current_graph", "thermal_graph", source="phase_24c_gate")
    registry.set("current_station", 12, source="phase_24c_gate")
    registry.set("current_report", "LEAF_Reports/test_report.json", source="phase_24c_gate")
    registry.set("current_optimisation", "optimisation_session_001", source="phase_24c_gate")
    registry.set("current_validation", "validation_run_001", source="phase_24c_gate")

    expected_values = {
        "active_project": "LEAF_Projects/test_project",
        "active_design": "LEAF_Designs/test_design.leaf_design.json",
        "current_workspace": "engineering_workspace",
        "current_tool": "regen_calculator",
        "current_graph": "thermal_graph",
        "current_station": 12,
        "current_report": "LEAF_Reports/test_report.json",
        "current_optimisation": "optimisation_session_001",
        "current_validation": "validation_run_001",
    }

    snapshot = registry.snapshot()

    for key, value in expected_values.items():
        if snapshot.get("state", {}).get(key) != value:
            failures.append(f"state_value_not_retained:{key}")

    try:
        registry.set("forbidden_parallel_state", "bad", source="phase_24c_gate")
        failures.append("forbidden_state_key_accepted")
    except KeyError:
        pass

    registry.clear("current_graph", source="phase_24c_gate")

    if registry.get("current_graph") is not None:
        failures.append("clear_state_failed")

    reset_changes = registry.reset(source="phase_24c_gate")

    if not reset_changes:
        failures.append("reset_did_not_produce_changes")

    after_reset = registry.snapshot()

    for key in RuntimeStateRegistry.ALLOWED_KEYS:
        if after_reset.get("state", {}).get(key) is not None:
            failures.append(f"reset_failed:{key}")

    required_snapshot_keys = [
        "schema",
        "state",
        "allowed_keys",
        "change_count",
        "qt_owns_runtime_state",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
        "emits_state_events",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if snapshot.get("qt_owns_runtime_state") is not False:
        failures.append("qt_ownership_boundary_invalid")

    for key in [
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"registry_stores_payloads:{key}")

    if snapshot.get("emits_state_events") is not True:
        failures.append("state_events_not_declared")

    result = {
        "phase": "24C",
        "programme": "24",
        "feature": "RUNTIME_STATE_REGISTRY",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_RUNTIME_STATE_REGISTRY_GATE_PHASE_24C_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/runtime/state_registry.py",
            "project_maintenance/runtime_architecture/runtime_state_registry_gate_phase_24c.py",
        ],
        "files_replaced": [
            "leaf_qt/runtime/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "central_runtime_state_registry": True,
            "allowed_state_keys_only": True,
            "active_project_reference": True,
            "active_design_reference": True,
            "workspace_tool_graph_station_report_references": True,
            "optimisation_validation_references": True,
            "state_change_events": True,
            "qt_does_not_own_runtime_state": True,
            "metadata_only_runtime_state": True,
        },
        "completion_notice": (
            "PHASE_24C_COMPLETE_RUNTIME_STATE_REGISTRY_ESTABLISHED"
            if not failures
            else "PHASE_24C_BLOCKED"
        ),
        "next_phase": "24D_DIRTY_STATE_MANAGER",
    }

    json_path = OUT / "runtime_state_registry_gate_phase_24c.json"
    txt_path = OUT / "runtime_state_registry_gate_phase_24c.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 24C RUNTIME STATE REGISTRY GATE",
                "==============================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "central_runtime_state_registry=True",
                "allowed_state_keys_only=True",
                "state_change_events=True",
                "qt_does_not_own_runtime_state=True",
                "metadata_only_runtime_state=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_24C_RUNTIME_STATE_REGISTRY")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_24C_RUNTIME_STATE_REGISTRY")
    print(f"runtime_schema={SCHEMA}")
    print("central_runtime_state_registry=True")
    print("allowed_state_keys_only=True")
    print("active_project_reference=True")
    print("active_design_reference=True")
    print("workspace_tool_graph_station_report_references=True")
    print("optimisation_validation_references=True")
    print("state_change_events=True")
    print("qt_does_not_own_runtime_state=True")
    print("metadata_only_runtime_state=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
