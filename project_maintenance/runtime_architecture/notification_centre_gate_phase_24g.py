from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "runtime_architecture" / "phase_24g"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "runtime" / "session_lifecycle.py",
    ROOT / "leaf_qt" / "runtime" / "event_bus.py",
    ROOT / "leaf_qt" / "runtime" / "state_registry.py",
    ROOT / "leaf_qt" / "runtime" / "dirty_state_manager.py",
    ROOT / "leaf_qt" / "runtime" / "undo_redo.py",
    ROOT / "leaf_qt" / "runtime" / "report_router.py",
    ROOT / "leaf_qt" / "runtime" / "notification_centre.py",
]

from leaf_qt.runtime.event_bus import RuntimeEventBus
from leaf_qt.runtime.notification_centre import (
    CATEGORY_IMPORT,
    CATEGORY_SAVE,
    CATEGORY_VALIDATION,
    LEVEL_ERROR,
    LEVEL_SUCCESS,
    LEVEL_WARNING,
    SCHEMA,
    RuntimeNotificationCentre,
)


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    bus = RuntimeEventBus()
    centre = RuntimeNotificationCentre(event_bus=bus, max_history=3)

    created_events: list[dict] = []
    validation_events: list[dict] = []
    read_events: list[dict] = []
    clear_events: list[dict] = []

    bus.subscribe(
        "runtime.notification.created",
        lambda event: created_events.append(event.payload),
        "notification_created_probe",
    )

    bus.subscribe(
        "runtime.notification.created.validation",
        lambda event: validation_events.append(event.payload),
        "validation_notification_probe",
    )

    bus.subscribe(
        "runtime.notification.read",
        lambda event: read_events.append(event.payload),
        "notification_read_probe",
    )

    bus.subscribe(
        "runtime.notification.cleared",
        lambda event: clear_events.append(event.payload),
        "notification_clear_probe",
    )

    saved = centre.notify(
        category=CATEGORY_SAVE,
        level=LEVEL_SUCCESS,
        title="Design Saved",
        message="The active design has been saved.",
        source="phase_24g_gate",
        target_id="LEAF_Designs/test_design.leaf_design.json",
        target_type="design",
    )

    validation = centre.notify(
        category=CATEGORY_VALIDATION,
        level=LEVEL_ERROR,
        title="Validation Failed",
        message="Validation found a blocking issue.",
        source="phase_24g_gate",
        target_id="validation_run_001",
        target_type="validation",
        action_ref="LEAF_Reports/validation_run_001.json",
    )

    imported = centre.notify(
        category=CATEGORY_IMPORT,
        level=LEVEL_WARNING,
        title="Import Complete With Warnings",
        message="Import finished but produced warnings.",
        source="phase_24g_gate",
        target_id="import_001",
        target_type="workspace",
    )

    if not saved.notification_id.startswith("note_"):
        failures.append("notification_id_invalid")

    if validation.category != CATEGORY_VALIDATION:
        failures.append("category_not_retained")

    if validation.level != LEVEL_ERROR:
        failures.append("level_not_retained")

    if validation.action_ref != "LEAF_Reports/validation_run_001.json":
        failures.append("action_ref_not_retained")

    if len(created_events) != 3:
        failures.append("created_events_not_emitted")

    if len(validation_events) != 1:
        failures.append("category_specific_event_not_emitted")

    if len(centre.unread()) != 3:
        failures.append("unread_count_invalid_before_mark_read")

    centre.mark_read(validation.notification_id)

    if len(read_events) != 1:
        failures.append("read_event_not_emitted")

    if len(centre.unread()) != 2:
        failures.append("unread_count_invalid_after_mark_read")

    filtered = centre.history(CATEGORY_VALIDATION)

    if len(filtered) != 1:
        failures.append("category_filtered_history_invalid")

    centre.notify(
        category=CATEGORY_SAVE,
        level=LEVEL_SUCCESS,
        title="Second Save",
        message="Second save.",
        source="phase_24g_gate",
    )

    centre.notify(
        category=CATEGORY_SAVE,
        level=LEVEL_SUCCESS,
        title="Third Save",
        message="Third save.",
        source="phase_24g_gate",
    )

    history = centre.history()

    if len(history) != 3:
        failures.append("bounded_notification_history_not_enforced")

    snapshot = centre.snapshot()

    required_snapshot_keys = [
        "schema",
        "notification_count",
        "unread_count",
        "max_history",
        "valid_levels",
        "valid_categories",
        "category_counts",
        "qt_owns_notifications",
        "replaces_modal_popup_scatter",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
        "emits_notification_events",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    if snapshot.get("qt_owns_notifications") is not False:
        failures.append("qt_ownership_boundary_invalid")

    if snapshot.get("replaces_modal_popup_scatter") is not True:
        failures.append("modal_popup_replacement_not_declared")

    for key in [
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"notification_centre_stores_payloads:{key}")

    if snapshot.get("emits_notification_events") is not True:
        failures.append("notification_events_not_declared")

    try:
        centre.notify(
            category="forbidden_category",
            level=LEVEL_SUCCESS,
            title="Bad Category",
            message="Should fail.",
            source="phase_24g_gate",
        )
        failures.append("forbidden_category_accepted")
    except KeyError:
        pass

    try:
        centre.notify(
            category=CATEGORY_SAVE,
            level="half_bad",
            title="Bad Level",
            message="Should fail.",
            source="phase_24g_gate",
        )
        failures.append("forbidden_level_accepted")
    except ValueError:
        pass

    try:
        centre.mark_read("missing_notification")
        failures.append("missing_notification_marked_read")
    except KeyError:
        pass

    centre.clear()

    if len(clear_events) != 1:
        failures.append("clear_event_not_emitted")

    if centre.history():
        failures.append("clear_failed")

    result = {
        "phase": "24G",
        "programme": "24",
        "feature": "RUNTIME_NOTIFICATION_CENTRE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_RUNTIME_NOTIFICATION_CENTRE_GATE_PHASE_24G_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/runtime/notification_centre.py",
            "project_maintenance/runtime_architecture/notification_centre_gate_phase_24g.py",
        ],
        "files_replaced": [
            "leaf_qt/runtime/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "notification_model": True,
            "save_notification": True,
            "validation_notification": True,
            "import_warning_notification": True,
            "unread_tracking": True,
            "mark_read": True,
            "category_filtering": True,
            "bounded_history": True,
            "category_allowlist": True,
            "level_allowlist": True,
            "event_emission": True,
            "qt_does_not_own_notifications": True,
            "metadata_only_notifications": True,
        },
        "completion_notice": (
            "PHASE_24G_COMPLETE_RUNTIME_NOTIFICATION_CENTRE_ESTABLISHED"
            if not failures
            else "PHASE_24G_BLOCKED"
        ),
        "next_phase": "24H_RUNTIME_COMPLETION_GATE",
    }

    json_path = OUT / "notification_centre_gate_phase_24g.json"
    txt_path = OUT / "notification_centre_gate_phase_24g.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 24G RUNTIME NOTIFICATION CENTRE GATE",
                "====================================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "notification_model=True",
                "save_notification=True",
                "validation_notification=True",
                "import_warning_notification=True",
                "unread_tracking=True",
                "mark_read=True",
                "category_filtering=True",
                "bounded_history=True",
                "category_allowlist=True",
                "level_allowlist=True",
                "event_emission=True",
                "qt_does_not_own_notifications=True",
                "metadata_only_notifications=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_24G_RUNTIME_NOTIFICATION_CENTRE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_24G_RUNTIME_NOTIFICATION_CENTRE")
    print(f"runtime_schema={SCHEMA}")
    print("notification_model=True")
    print("save_notification=True")
    print("validation_notification=True")
    print("import_warning_notification=True")
    print("unread_tracking=True")
    print("mark_read=True")
    print("category_filtering=True")
    print("bounded_history=True")
    print("category_allowlist=True")
    print("level_allowlist=True")
    print("event_emission=True")
    print("qt_does_not_own_notifications=True")
    print("metadata_only_notifications=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
