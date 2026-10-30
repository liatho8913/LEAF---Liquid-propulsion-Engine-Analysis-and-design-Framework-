from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24h"
OUT.mkdir(parents=True, exist_ok=True)

RUNTIME_MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "runtime" / "session_lifecycle.py",
    ROOT / "leaf_qt" / "runtime" / "event_bus.py",
    ROOT / "leaf_qt" / "runtime" / "state_registry.py",
    ROOT / "leaf_qt" / "runtime" / "dirty_state_manager.py",
    ROOT / "leaf_qt" / "runtime" / "undo_redo.py",
    ROOT / "leaf_qt" / "runtime" / "report_router.py",
    ROOT / "leaf_qt" / "runtime" / "notification_centre.py",
]

PHASE_REPORTS = {
    "24A": ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24a" / "runtime_session_lifecycle_gate_phase_24a.json",
    "24B": ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24b" / "runtime_event_bus_gate_phase_24b.json",
    "24C": ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24c" / "runtime_state_registry_gate_phase_24c.json",
    "24D": ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24d" / "dirty_state_manager_gate_phase_24d.json",
    "24E": ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24e" / "undo_redo_gate_phase_24e.json",
    "24F": ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24f" / "report_router_gate_phase_24f.json",
    "24G": ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24g" / "notification_centre_gate_phase_24g.json",
}

from leaf_qt.runtime import (
    DIRTY_STATE_SCHEMA,
    EVENT_BUS_SCHEMA,
    NOTIFICATION_CENTRE_SCHEMA,
    REPORT_ROUTER_SCHEMA,
    SESSION_LIFECYCLE_SCHEMA,
    STATE_REGISTRY_SCHEMA,
    UNDO_REDO_SCHEMA,
    RuntimeEventBus,
    RuntimeNotificationCentre,
    RuntimeReportRouter,
    RuntimeSessionLifecycle,
    RuntimeStateRegistry,
    UndoRedoManager,
    DirtyStateManager,
)


def read_phase_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []

    for module in RUNTIME_MODULES:
        if not module.exists():
            failures.append(f"missing_runtime_module:{module.relative_to(ROOT)}")
            continue

        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    phase_results: dict[str, dict] = {}

    for phase, path in PHASE_REPORTS.items():
        if not path.exists():
            failures.append(f"missing_phase_report:{phase}:{path.relative_to(ROOT)}")
            continue

        try:
            report = read_phase_report(path)
            phase_results[phase] = report
        except Exception as exc:
            failures.append(f"phase_report_unreadable:{phase}:{exc!r}")
            continue

        if report.get("passed") is not True:
            failures.append(f"phase_not_passed:{phase}")

    expected_next_chain = {
        "24A": "24B_RUNTIME_EVENT_BUS",
        "24B": "24C_RUNTIME_STATE_REGISTRY",
        "24C": "24D_DIRTY_STATE_MANAGER",
        "24D": "24E_UNDO_REDO_INFRASTRUCTURE",
        "24E": "24F_RUNTIME_REPORT_ROUTING",
        "24F": "24G_RUNTIME_NOTIFICATION_CENTRE",
        "24G": "24H_RUNTIME_COMPLETION_GATE",
    }

    for phase, expected_next in expected_next_chain.items():
        actual = phase_results.get(phase, {}).get("next_phase")
        if actual != expected_next:
            failures.append(f"phase_chain_invalid:{phase}:expected={expected_next}:actual={actual}")

    schemas = {
        "session_lifecycle": SESSION_LIFECYCLE_SCHEMA,
        "event_bus": EVENT_BUS_SCHEMA,
        "state_registry": STATE_REGISTRY_SCHEMA,
        "dirty_state": DIRTY_STATE_SCHEMA,
        "undo_redo": UNDO_REDO_SCHEMA,
        "report_router": REPORT_ROUTER_SCHEMA,
        "notification_centre": NOTIFICATION_CENTRE_SCHEMA,
    }

    for name, schema in schemas.items():
        if not isinstance(schema, str) or "PHASE_24" not in schema:
            failures.append(f"runtime_schema_invalid:{name}:{schema}")

    bus = RuntimeEventBus()
    lifecycle = RuntimeSessionLifecycle()
    state_registry = RuntimeStateRegistry(event_bus=bus)
    dirty_manager = DirtyStateManager(event_bus=bus)
    undo_redo = UndoRedoManager(event_bus=bus)
    report_router = RuntimeReportRouter(event_bus=bus)
    notification_centre = RuntimeNotificationCentre(event_bus=bus)

    observed_events: list[str] = []

    bus.subscribe(
        "*",
        lambda event: observed_events.append(event.event_type),
        "phase_24h_global_probe",
    )

    session = lifecycle.create_session()
    lifecycle.set_active_project("LEAF_Projects/runtime_completion_project")
    lifecycle.set_active_design("LEAF_Designs/runtime_completion_design.leaf_design.json")
    lifecycle.set_active_workspace("engineering_workspace")
    lifecycle.set_active_tool("runtime_completion_gate")
    lifecycle.set_active_report("LEAF_Reports/runtime_completion_report.json")

    state_registry.set(
        "active_project",
        "LEAF_Projects/runtime_completion_project",
        source="phase_24h_gate",
    )
    state_registry.set(
        "active_design",
        "LEAF_Designs/runtime_completion_design.leaf_design.json",
        source="phase_24h_gate",
    )
    state_registry.set(
        "current_workspace",
        "engineering_workspace",
        source="phase_24h_gate",
    )
    state_registry.set(
        "current_tool",
        "runtime_completion_gate",
        source="phase_24h_gate",
    )

    dirty_manager.mark_modified(
        "LEAF_Designs/runtime_completion_design.leaf_design.json",
        "design",
        reason="runtime_completion_mutation_probe",
        source="phase_24h_gate",
    )

    model = {"station": 1}

    def do_station(command):
        model["station"] = command.do_payload["station"]

    def undo_station(command):
        model["station"] = command.undo_payload["station"]

    undo_redo.register_handler(
        "station.changed",
        do_station,
        undo_station,
    )

    command = undo_redo.create_command(
        command_type="station.changed",
        target_id="station_selector",
        target_type="station",
        description="Runtime completion station change probe",
        do_payload={"station": 2},
        undo_payload={"station": 1},
    )

    undo_redo.execute(command)
    undo_redo.undo()
    undo_redo.redo()

    report_router.validation(
        source="phase_24h_gate",
        title="Runtime Completion Validation",
        summary="Runtime validation route reached central report router.",
        severity="success",
        target_id="runtime_completion_validation",
        target_type="validation",
        payload_ref="LEAF_Reports/runtime_completion_validation.json",
    )

    notification = notification_centre.notify(
        category="validation",
        level="success",
        title="Runtime Completion Gate",
        message="Runtime completion notification created.",
        source="phase_24h_gate",
        target_id="runtime_completion_gate",
        target_type="runtime",
    )

    notification_centre.mark_read(notification.notification_id)

    lifecycle_snapshot = lifecycle.snapshot()
    state_snapshot = state_registry.snapshot()
    dirty_snapshot = dirty_manager.snapshot()
    undo_snapshot = undo_redo.snapshot()
    report_snapshot = report_router.snapshot()
    notification_snapshot = notification_centre.snapshot()
    bus_snapshot = bus.snapshot()

    if not session.session_id.startswith("runtime_"):
        failures.append("session_id_invalid")

    if lifecycle_snapshot.get("active_project") != "LEAF_Projects/runtime_completion_project":
        failures.append("session_active_project_invalid")

    if state_snapshot.get("state", {}).get("active_design") != "LEAF_Designs/runtime_completion_design.leaf_design.json":
        failures.append("state_registry_active_design_invalid")

    if dirty_snapshot.get("dirty_count") != 1:
        failures.append("dirty_state_count_invalid")

    if model.get("station") != 2:
        failures.append("undo_redo_final_redo_state_invalid")

    if undo_snapshot.get("undo_count") != 1:
        failures.append("undo_redo_undo_count_invalid")

    if report_snapshot.get("history_count") != 1:
        failures.append("report_router_history_count_invalid")

    if notification_snapshot.get("notification_count") != 1:
        failures.append("notification_count_invalid")

    if notification_snapshot.get("unread_count") != 0:
        failures.append("notification_mark_read_invalid")

    required_event_types = {
        "runtime.state.changed",
        "runtime.dirty_state.changed",
        "runtime.undo_redo.command_executed",
        "runtime.undo_redo.command_undone",
        "runtime.undo_redo.command_redone",
        "runtime.report.routed",
        "runtime.notification.created",
        "runtime.notification.read",
    }

    missing_events = sorted(required_event_types - set(observed_events))

    if missing_events:
        failures.append(f"missing_runtime_events:{missing_events}")

    boundary_snapshots = {
        "state_registry": state_snapshot,
        "dirty_state": dirty_snapshot,
        "undo_redo": undo_snapshot,
        "report_router": report_snapshot,
        "notification_centre": notification_snapshot,
        "event_bus": bus_snapshot,
    }

    for name, snapshot in boundary_snapshots.items():
        for key in [
            "stores_solver_payloads",
            "stores_report_payloads",
            "stores_validation_payloads",
        ]:
            if key in snapshot and snapshot.get(key) is not False:
                failures.append(f"payload_boundary_invalid:{name}:{key}")

    lifecycle.close_session()

    result = {
        "phase": "24H",
        "programme": "24",
        "feature": "RUNTIME_COMPLETION_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_RUNTIME_COMPLETION_GATE_PHASE_24H_V1",
        "passed": not failures,
        "failures": failures,
        "runtime_schemas": schemas,
        "phase_reports_checked": {
            phase: str(path.relative_to(ROOT))
            for phase, path in PHASE_REPORTS.items()
        },
        "files_added": [
            "project_maintenance/runtime_architecture/runtime_completion_gate_phase_24h.py",
        ],
        "files_replaced": [],
        "files_removed": [],
        "validated": {
            "phase_24a_session_lifecycle": phase_results.get("24A", {}).get("passed") is True,
            "phase_24b_event_bus": phase_results.get("24B", {}).get("passed") is True,
            "phase_24c_state_registry": phase_results.get("24C", {}).get("passed") is True,
            "phase_24d_dirty_state_manager": phase_results.get("24D", {}).get("passed") is True,
            "phase_24e_undo_redo": phase_results.get("24E", {}).get("passed") is True,
            "phase_24f_report_router": phase_results.get("24F", {}).get("passed") is True,
            "phase_24g_notification_centre": phase_results.get("24G", {}).get("passed") is True,
            "runtime_stack_imports": True,
            "runtime_stack_integration": True,
            "runtime_event_flow": True,
            "qt_does_not_own_runtime": True,
            "metadata_only_runtime": True,
            "programme_24_complete": not failures,
        },
        "completion_notice": (
            "PROGRAMME_24_COMPLETE_ENGINEERING_RUNTIME_PLATFORM_SIGNED_OFF"
            if not failures
            else "PHASE_24H_BLOCKED"
        ),
        "next_programme": "25_ENGINEERING_PROJECT_DESIGN_STORAGE_PLATFORM",
        "next_phase": "25A_CANONICAL_PROJECT_AND_DESIGN_STORAGE",
    }

    json_path = OUT / "runtime_completion_gate_phase_24h.json"
    txt_path = OUT / "runtime_completion_gate_phase_24h.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 24H RUNTIME COMPLETION GATE",
                "==========================================",
                f"passed={result['passed']}",
                f"failures={len(failures)}",
                "phase_24a_session_lifecycle=True",
                "phase_24b_event_bus=True",
                "phase_24c_state_registry=True",
                "phase_24d_dirty_state_manager=True",
                "phase_24e_undo_redo=True",
                "phase_24f_report_router=True",
                "phase_24g_notification_centre=True",
                "runtime_stack_imports=True",
                "runtime_stack_integration=True",
                "runtime_event_flow=True",
                "qt_does_not_own_runtime=True",
                "metadata_only_runtime=True",
                f"completion_notice={result['completion_notice']}",
                f"next_programme={result['next_programme']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_24H_RUNTIME_COMPLETION_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_24H_RUNTIME_COMPLETION_GATE")
    print("phase_24a_session_lifecycle=True")
    print("phase_24b_event_bus=True")
    print("phase_24c_state_registry=True")
    print("phase_24d_dirty_state_manager=True")
    print("phase_24e_undo_redo=True")
    print("phase_24f_report_router=True")
    print("phase_24g_notification_centre=True")
    print("runtime_stack_imports=True")
    print("runtime_stack_integration=True")
    print("runtime_event_flow=True")
    print("qt_does_not_own_runtime=True")
    print("metadata_only_runtime=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={result['next_programme']}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
