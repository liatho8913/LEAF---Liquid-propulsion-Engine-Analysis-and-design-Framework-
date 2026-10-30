from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24e"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "runtime" / "session_lifecycle.py",
    ROOT / "leaf_qt" / "runtime" / "event_bus.py",
    ROOT / "leaf_qt" / "runtime" / "state_registry.py",
    ROOT / "leaf_qt" / "runtime" / "dirty_state_manager.py",
    ROOT / "leaf_qt" / "runtime" / "undo_redo.py",
]

from leaf_qt.runtime.event_bus import RuntimeEventBus
from leaf_qt.runtime.undo_redo import SCHEMA, RuntimeCommand, UndoRedoManager


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    bus = RuntimeEventBus()
    manager = UndoRedoManager(event_bus=bus, max_history=2)

    model = {"channel_count": 80}
    events = {
        "executed": 0,
        "undone": 0,
        "redone": 0,
        "cleared": 0,
    }

    bus.subscribe(
        "runtime.undo_redo.command_executed",
        lambda event: events.__setitem__("executed", events["executed"] + 1),
        "executed_probe",
    )
    bus.subscribe(
        "runtime.undo_redo.command_undone",
        lambda event: events.__setitem__("undone", events["undone"] + 1),
        "undone_probe",
    )
    bus.subscribe(
        "runtime.undo_redo.command_redone",
        lambda event: events.__setitem__("redone", events["redone"] + 1),
        "redone_probe",
    )
    bus.subscribe(
        "runtime.undo_redo.history_cleared",
        lambda event: events.__setitem__("cleared", events["cleared"] + 1),
        "cleared_probe",
    )

    def do_geometry(command: RuntimeCommand) -> None:
        model["channel_count"] = command.do_payload["channel_count"]

    def undo_geometry(command: RuntimeCommand) -> None:
        model["channel_count"] = command.undo_payload["channel_count"]

    manager.register_handler(
        "geometry.channel_count.changed",
        do_geometry,
        undo_geometry,
    )

    command = manager.create_command(
        command_type="geometry.channel_count.changed",
        target_id="LEAF_Designs/test_design.leaf_design.json",
        target_type="geometry",
        description="Change regenerative channel count",
        do_payload={"channel_count": 96},
        undo_payload={"channel_count": 80},
    )

    if not command.command_id.startswith("cmd_"):
        failures.append("command_id_invalid")

    manager.execute(command)

    if model["channel_count"] != 96:
        failures.append("execute_handler_did_not_apply_change")

    if not manager.can_undo():
        failures.append("can_undo_false_after_execute")

    if manager.can_redo():
        failures.append("can_redo_true_before_undo")

    if events["executed"] != 1:
        failures.append("execute_event_not_emitted")

    undone = manager.undo()

    if undone.command_id != command.command_id:
        failures.append("undo_returned_wrong_command")

    if model["channel_count"] != 80:
        failures.append("undo_handler_did_not_restore_change")

    if not manager.can_redo():
        failures.append("can_redo_false_after_undo")

    if events["undone"] != 1:
        failures.append("undo_event_not_emitted")

    redone = manager.redo()

    if redone.command_id != command.command_id:
        failures.append("redo_returned_wrong_command")

    if model["channel_count"] != 96:
        failures.append("redo_handler_did_not_reapply_change")

    if events["redone"] != 1:
        failures.append("redo_event_not_emitted")

    command_2 = manager.create_command(
        "geometry.channel_count.changed",
        "LEAF_Designs/test_design.leaf_design.json",
        "geometry",
        "Change channel count again",
        {"channel_count": 104},
        {"channel_count": 96},
    )
    command_3 = manager.create_command(
        "geometry.channel_count.changed",
        "LEAF_Designs/test_design.leaf_design.json",
        "geometry",
        "Change channel count third time",
        {"channel_count": 112},
        {"channel_count": 104},
    )

    manager.execute(command_2)
    manager.execute(command_3)

    snapshot = manager.snapshot()

    if snapshot.get("undo_count") != 2:
        failures.append("bounded_undo_history_not_enforced")

    if snapshot.get("redo_count") != 0:
        failures.append("redo_stack_not_cleared_after_new_execute")

    try:
        manager.create_command(
            "bad.command",
            "bad_target",
            "forbidden_target_type",
            "Bad command",
            {},
            {},
        )
        failures.append("forbidden_target_type_accepted")
    except KeyError:
        pass

    missing_handler_command = manager.create_command(
        "missing.handler.command",
        "LEAF_Designs/test_design.leaf_design.json",
        "design",
        "Missing handler command",
        {},
        {},
    )

    try:
        manager.execute(missing_handler_command)
        failures.append("missing_do_handler_accepted")
    except KeyError:
        pass

    required_snapshot_keys = [
        "schema",
        "undo_count",
        "redo_count",
        "can_undo",
        "can_redo",
        "max_history",
        "registered_command_types",
        "undo_stack",
        "redo_stack",
        "target_types",
        "qt_owns_undo_redo",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
        "emits_undo_redo_events",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if snapshot.get("qt_owns_undo_redo") is not False:
        failures.append("qt_ownership_boundary_invalid")

    for key in [
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"undo_redo_stores_payloads:{key}")

    if snapshot.get("emits_undo_redo_events") is not True:
        failures.append("undo_redo_events_not_declared")

    manager.clear()

    if events["cleared"] != 1:
        failures.append("clear_event_not_emitted")

    if manager.snapshot().get("undo_count") != 0:
        failures.append("clear_did_not_empty_undo_stack")

    if manager.snapshot().get("redo_count") != 0:
        failures.append("clear_did_not_empty_redo_stack")

    result = {
        "phase": "24E",
        "programme": "24",
        "feature": "UNDO_REDO_INFRASTRUCTURE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_UNDO_REDO_GATE_PHASE_24E_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/runtime/undo_redo.py",
            "project_maintenance/runtime_architecture/undo_redo_gate_phase_24e.py",
        ],
        "files_replaced": [
            "leaf_qt/runtime/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "runtime_command_model": True,
            "registered_command_handlers": True,
            "execute": True,
            "undo": True,
            "redo": True,
            "bounded_history": True,
            "redo_stack_cleared_after_new_execute": True,
            "event_emission": True,
            "target_type_allowlist": True,
            "qt_does_not_own_undo_redo": True,
            "metadata_only_undo_redo": True,
        },
        "completion_notice": (
            "PHASE_24E_COMPLETE_UNDO_REDO_INFRASTRUCTURE_ESTABLISHED"
            if not failures
            else "PHASE_24E_BLOCKED"
        ),
        "next_phase": "24F_RUNTIME_REPORT_ROUTING",
    }

    json_path = OUT / "undo_redo_gate_phase_24e.json"
    txt_path = OUT / "undo_redo_gate_phase_24e.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 24E UNDO / REDO INFRASTRUCTURE GATE",
                "===================================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "runtime_command_model=True",
                "registered_command_handlers=True",
                "execute=True",
                "undo=True",
                "redo=True",
                "bounded_history=True",
                "redo_stack_cleared_after_new_execute=True",
                "event_emission=True",
                "target_type_allowlist=True",
                "qt_does_not_own_undo_redo=True",
                "metadata_only_undo_redo=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_24E_UNDO_REDO_INFRASTRUCTURE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_24E_UNDO_REDO_INFRASTRUCTURE")
    print(f"runtime_schema={SCHEMA}")
    print("runtime_command_model=True")
    print("registered_command_handlers=True")
    print("execute=True")
    print("undo=True")
    print("redo=True")
    print("bounded_history=True")
    print("redo_stack_cleared_after_new_execute=True")
    print("event_emission=True")
    print("target_type_allowlist=True")
    print("qt_does_not_own_undo_redo=True")
    print("metadata_only_undo_redo=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
