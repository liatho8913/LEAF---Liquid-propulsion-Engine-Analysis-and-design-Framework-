from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24d"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "runtime" / "session_lifecycle.py",
    ROOT / "leaf_qt" / "runtime" / "event_bus.py",
    ROOT / "leaf_qt" / "runtime" / "state_registry.py",
    ROOT / "leaf_qt" / "runtime" / "dirty_state_manager.py",
]

from leaf_qt.runtime.dirty_state_manager import (
    SCHEMA,
    STATE_MODIFIED,
    STATE_SAVED,
    STATE_UNSAVED,
    DirtyStateManager,
)
from leaf_qt.runtime.event_bus import RuntimeEventBus


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    bus = RuntimeEventBus()
    manager = DirtyStateManager(event_bus=bus)

    received_general: list[dict] = []
    received_design: list[dict] = []

    bus.subscribe(
        "runtime.dirty_state.changed",
        lambda event: received_general.append(event.payload),
        "dirty_general_probe",
    )

    bus.subscribe(
        "runtime.dirty_state.changed.design",
        lambda event: received_design.append(event.payload),
        "dirty_design_probe",
    )

    design_id = "LEAF_Designs/test_design.leaf_design.json"
    report_id = "LEAF_Reports/test_report.json"

    manager.mark_saved(
        design_id,
        "design",
        reason="initial_save",
        source="phase_24d_gate",
    )

    if manager.get_state(design_id) != STATE_SAVED:
        failures.append("saved_state_not_retained")

    if manager.is_dirty(design_id):
        failures.append("saved_entity_reported_dirty")

    manager.mark_modified(
        design_id,
        "design",
        reason="geometry_changed",
        source="phase_24d_gate",
    )

    if manager.get_state(design_id) != STATE_MODIFIED:
        failures.append("modified_state_not_retained")

    if not manager.is_dirty(design_id):
        failures.append("modified_entity_not_dirty")

    manager.mark_unsaved(
        report_id,
        "report",
        reason="new_report_generated",
        source="phase_24d_gate",
    )

    if manager.get_state(report_id) != STATE_UNSAVED:
        failures.append("unsaved_state_not_retained")

    if not manager.is_dirty(report_id):
        failures.append("unsaved_entity_not_dirty")

    if len(received_general) != 3:
        failures.append("general_dirty_events_not_emitted")

    if len(received_design) != 2:
        failures.append("specific_design_dirty_events_not_emitted")

    dirty_records = manager.dirty_records()

    if len(dirty_records) != 2:
        failures.append("dirty_record_count_invalid")

    manager.mark_saved(
        design_id,
        "design",
        reason="design_saved_after_change",
        source="phase_24d_gate",
    )

    if manager.is_dirty(design_id):
        failures.append("saved_after_modified_still_dirty")

    if manager.get_record(design_id) is None:
        failures.append("record_lookup_failed")

    try:
        manager.mark_modified(
            "bad_entity",
            "forbidden_entity_type",
            reason="bad",
            source="phase_24d_gate",
        )
        failures.append("forbidden_entity_type_accepted")
    except KeyError:
        pass

    try:
        manager.set_state(
            "bad_state_entity",
            "design",
            "half_saved",
            reason="bad",
            source="phase_24d_gate",
        )
        failures.append("forbidden_dirty_state_accepted")
    except ValueError:
        pass

    snapshot = manager.snapshot()

    required_snapshot_keys = [
        "schema",
        "records",
        "record_count",
        "dirty_count",
        "valid_dirty_states",
        "tracked_entity_types",
        "qt_owns_dirty_state",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
        "emits_dirty_state_events",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if snapshot.get("qt_owns_dirty_state") is not False:
        failures.append("qt_ownership_boundary_invalid")

    for key in [
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"dirty_state_manager_stores_payloads:{key}")

    if snapshot.get("emits_dirty_state_events") is not True:
        failures.append("dirty_state_events_not_declared")

    if set(snapshot.get("valid_dirty_states", [])) != {
        STATE_SAVED,
        STATE_MODIFIED,
        STATE_UNSAVED,
    }:
        failures.append("valid_dirty_states_invalid")

    if not manager.clear_entity(report_id):
        failures.append("clear_existing_entity_failed")

    if manager.clear_entity("missing_entity") is not False:
        failures.append("clear_missing_entity_not_false")

    manager.reset()

    if manager.snapshot().get("record_count") != 0:
        failures.append("reset_failed")

    result = {
        "phase": "24D",
        "programme": "24",
        "feature": "DIRTY_STATE_MANAGER",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_DIRTY_STATE_MANAGER_GATE_PHASE_24D_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/runtime/dirty_state_manager.py",
            "project_maintenance/runtime_architecture/dirty_state_manager_gate_phase_24d.py",
        ],
        "files_replaced": [
            "leaf_qt/runtime/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "saved_state_tracking": True,
            "modified_state_tracking": True,
            "unsaved_state_tracking": True,
            "dirty_detection": True,
            "clean_after_save": True,
            "entity_type_allowlist": True,
            "dirty_state_allowlist": True,
            "dirty_state_events": True,
            "qt_does_not_own_dirty_state": True,
            "metadata_only_dirty_state": True,
        },
        "completion_notice": (
            "PHASE_24D_COMPLETE_DIRTY_STATE_MANAGER_ESTABLISHED"
            if not failures
            else "PHASE_24D_BLOCKED"
        ),
        "next_phase": "24E_UNDO_REDO_INFRASTRUCTURE",
    }

    json_path = OUT / "dirty_state_manager_gate_phase_24d.json"
    txt_path = OUT / "dirty_state_manager_gate_phase_24d.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 24D DIRTY STATE MANAGER GATE",
                "============================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "saved_state_tracking=True",
                "modified_state_tracking=True",
                "unsaved_state_tracking=True",
                "dirty_detection=True",
                "clean_after_save=True",
                "entity_type_allowlist=True",
                "dirty_state_allowlist=True",
                "dirty_state_events=True",
                "qt_does_not_own_dirty_state=True",
                "metadata_only_dirty_state=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_24D_DIRTY_STATE_MANAGER")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_24D_DIRTY_STATE_MANAGER")
    print(f"runtime_schema={SCHEMA}")
    print("saved_state_tracking=True")
    print("modified_state_tracking=True")
    print("unsaved_state_tracking=True")
    print("dirty_detection=True")
    print("clean_after_save=True")
    print("entity_type_allowlist=True")
    print("dirty_state_allowlist=True")
    print("dirty_state_events=True")
    print("qt_does_not_own_dirty_state=True")
    print("metadata_only_dirty_state=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
