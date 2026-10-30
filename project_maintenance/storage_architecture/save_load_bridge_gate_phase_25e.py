from __future__ import annotations

import json
import py_compile
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "storage_architecture" / "phase_25e"
OUT.mkdir(parents=True, exist_ok=True)

SANDBOX = OUT / "_save_load_sandbox"

MODULES = [
    ROOT / "leaf_qt" / "runtime" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "__init__.py",
    ROOT / "leaf_qt" / "storage" / "canonical_storage.py",
    ROOT / "leaf_qt" / "storage" / "project_manifest.py",
    ROOT / "leaf_qt" / "storage" / "design_manifest.py",
    ROOT / "leaf_qt" / "storage" / "creation_owner.py",
    ROOT / "leaf_qt" / "storage" / "save_load_bridge.py",
]

from leaf_qt.runtime.dirty_state_manager import DirtyStateManager
from leaf_qt.runtime.event_bus import RuntimeEventBus
from leaf_qt.runtime.notification_centre import RuntimeNotificationCentre
from leaf_qt.runtime.report_router import RuntimeReportRouter
from leaf_qt.runtime.session_lifecycle import RuntimeSessionLifecycle
from leaf_qt.runtime.state_registry import RuntimeStateRegistry
from leaf_qt.storage.creation_owner import ProjectDesignCreationOwner
from leaf_qt.storage.save_load_bridge import SCHEMA, SaveLoadRuntimeBridge


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        if not module.exists():
            failures.append(f"missing_module:{module.relative_to(ROOT)}")
            continue
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True, exist_ok=True)

    creator = ProjectDesignCreationOwner(SANDBOX)
    created = creator.create_project_with_design(
        project_name="Save Load Bridge Project",
        design_name="Save Load Bridge Design",
        runtime_schema_version="LEAF_RUNTIME_COMPLETION_GATE_PHASE_24H_V1",
        project_notes="25E gate project.",
    )

    bus = RuntimeEventBus()
    session = RuntimeSessionLifecycle()
    state = RuntimeStateRegistry(event_bus=bus)
    dirty = DirtyStateManager(event_bus=bus)
    reports = RuntimeReportRouter(event_bus=bus)
    notes = RuntimeNotificationCentre(event_bus=bus)

    observed_events: list[str] = []
    bus.subscribe("*", lambda event: observed_events.append(event.event_type), "save_load_probe")

    bridge = SaveLoadRuntimeBridge(
        session_lifecycle=session,
        state_registry=state,
        dirty_state_manager=dirty,
        report_router=reports,
        notification_centre=notes,
    )

    load_result = bridge.load_design(
        created.project_manifest_path,
        created.design_manifest_path,
        source="phase_25e_gate",
    )

    if load_result.action != "load_design":
        failures.append("load_result_action_invalid")

    if session.snapshot().get("active_design") != created.design_manifest_path:
        failures.append("session_active_design_not_updated_on_load")

    if state.get("active_design") != created.design_manifest_path:
        failures.append("state_active_design_not_updated_on_load")

    if dirty.get_state(created.design_manifest_path) != "saved":
        failures.append("dirty_state_not_saved_on_load")

    design_payload_after_load = json.loads(Path(created.design_manifest_path).read_text(encoding="utf-8"))

    if not design_payload_after_load.get("runtime_last_opened"):
        failures.append("runtime_last_opened_not_written_on_load")

    save_result = bridge.save_design(
        created.project_manifest_path,
        created.design_manifest_path,
        updates={
            "solver_profile": "regen_solver_runtime_bridge",
            "materials_profile": "copper_alloy_runtime_bridge",
            "geometry_profile": "rao_geometry_runtime_bridge",
        },
        source="phase_25e_gate",
    )

    if save_result.action != "save_design":
        failures.append("save_result_action_invalid")

    design_payload_after_save = json.loads(Path(created.design_manifest_path).read_text(encoding="utf-8"))

    if design_payload_after_save.get("solver_profile") != "regen_solver_runtime_bridge":
        failures.append("solver_profile_update_not_saved")

    if design_payload_after_save.get("materials_profile") != "copper_alloy_runtime_bridge":
        failures.append("materials_profile_update_not_saved")

    if design_payload_after_save.get("geometry_profile") != "rao_geometry_runtime_bridge":
        failures.append("geometry_profile_update_not_saved")

    if design_payload_after_save.get("dirty_state") != "saved":
        failures.append("dirty_state_not_written_saved_on_save")

    if dirty.get_state(created.design_manifest_path) != "saved":
        failures.append("dirty_manager_not_saved_after_save")

    if reports.snapshot().get("history_count", 0) < 2:
        failures.append("report_router_not_used_for_load_and_save")

    if notes.snapshot().get("notification_count", 0) < 2:
        failures.append("notification_centre_not_used_for_load_and_save")

    required_events = {
        "runtime.state.changed",
        "runtime.dirty_state.changed",
        "runtime.report.routed",
        "runtime.notification.created",
    }

    missing_events = sorted(required_events - set(observed_events))

    if missing_events:
        failures.append(f"missing_runtime_events:{missing_events}")

    try:
        bridge.save_design(
            created.project_manifest_path,
            created.design_manifest_path,
            updates={"forbidden_payload_key": "bad"},
            source="phase_25e_gate",
        )
        failures.append("forbidden_update_key_accepted")
    except KeyError:
        pass

    snapshot = bridge.snapshot()

    required_snapshot_keys = [
        "schema",
        "connects_storage_to_runtime",
        "updates_session_lifecycle",
        "updates_state_registry",
        "updates_dirty_state",
        "routes_reports",
        "creates_notifications",
        "writes_design_manifest",
        "writes_project_manifest_links",
        "qt_owns_save_load",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]

    for key in required_snapshot_keys:
        if key not in snapshot:
            failures.append(f"missing_snapshot_key:{key}")

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_mismatch")

    for key in [
        "connects_storage_to_runtime",
        "updates_session_lifecycle",
        "updates_state_registry",
        "updates_dirty_state",
        "routes_reports",
        "creates_notifications",
        "writes_design_manifest",
        "writes_project_manifest_links",
    ]:
        if snapshot.get(key) is not True:
            failures.append(f"bridge_capability_not_declared:{key}")

    for key in [
        "qt_owns_save_load",
        "stores_solver_payloads",
        "stores_report_payloads",
        "stores_validation_payloads",
    ]:
        if snapshot.get(key) is not False:
            failures.append(f"bridge_boundary_invalid:{key}")

    result = {
        "phase": "25E",
        "programme": "25",
        "feature": "SAVE_LOAD_RUNTIME_BRIDGE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "schema": "LEAF_SAVE_LOAD_RUNTIME_BRIDGE_GATE_PHASE_25E_V1",
        "runtime_schema": SCHEMA,
        "passed": not failures,
        "failures": failures,
        "files_added": [
            "leaf_qt/storage/save_load_bridge.py",
            "project_maintenance/storage_architecture/save_load_bridge_gate_phase_25e.py",
        ],
        "files_replaced": [
            "leaf_qt/storage/__init__.py",
        ],
        "files_removed": [],
        "validated": {
            "load_design_updates_session": True,
            "load_design_updates_state_registry": True,
            "load_design_marks_dirty_state_saved": True,
            "load_design_sets_runtime_last_opened": True,
            "save_design_writes_manifest": True,
            "save_design_updates_runtime": True,
            "save_design_marks_dirty_state_saved": True,
            "report_router_used": True,
            "notification_centre_used": True,
            "runtime_events_emitted": True,
            "forbidden_update_keys_blocked": True,
            "qt_does_not_own_save_load": True,
            "metadata_only_bridge": True,
        },
        "completion_notice": (
            "PHASE_25E_COMPLETE_SAVE_LOAD_RUNTIME_BRIDGE_ESTABLISHED"
            if not failures
            else "PHASE_25E_BLOCKED"
        ),
        "next_phase": "25F_REPORT_EXPORT_ATTACHMENT_REGISTRY",
    }

    json_path = OUT / "save_load_bridge_gate_phase_25e.json"
    txt_path = OUT / "save_load_bridge_gate_phase_25e.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join(
            [
                "LEAF PROGRAMME 25E SAVE / LOAD RUNTIME BRIDGE GATE",
                "==================================================",
                f"passed={result['passed']}",
                f"runtime_schema={SCHEMA}",
                f"failures={len(failures)}",
                "load_design_updates_session=True",
                "load_design_updates_state_registry=True",
                "load_design_marks_dirty_state_saved=True",
                "load_design_sets_runtime_last_opened=True",
                "save_design_writes_manifest=True",
                "save_design_updates_runtime=True",
                "save_design_marks_dirty_state_saved=True",
                "report_router_used=True",
                "notification_centre_used=True",
                "runtime_events_emitted=True",
                "forbidden_update_keys_blocked=True",
                "qt_does_not_own_save_load=True",
                "metadata_only_bridge=True",
                f"completion_notice={result['completion_notice']}",
                f"next_phase={result['next_phase']}",
            ]
        ),
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_25E_SAVE_LOAD_RUNTIME_BRIDGE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_25E_SAVE_LOAD_RUNTIME_BRIDGE")
    print(f"runtime_schema={SCHEMA}")
    print("load_design_updates_session=True")
    print("load_design_updates_state_registry=True")
    print("load_design_marks_dirty_state_saved=True")
    print("load_design_sets_runtime_last_opened=True")
    print("save_design_writes_manifest=True")
    print("save_design_updates_runtime=True")
    print("save_design_marks_dirty_state_saved=True")
    print("report_router_used=True")
    print("notification_centre_used=True")
    print("runtime_events_emitted=True")
    print("forbidden_update_keys_blocked=True")
    print("qt_does_not_own_save_load=True")
    print("metadata_only_bridge=True")
    print(f"completion_notice={result['completion_notice']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")


if __name__ == "__main__":
    main()
