from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.design_session_manager_phase_22d import (
    SCHEMA,
    USER_DESIGN_ROOT,
    DesignSessionManager,
    build_design_session_manager_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22d"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "design_session_manager_phase_22d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "design_session_manager_gate_phase_22d.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    manager = DesignSessionManager(ROOT)
    session = manager.create_session(design_label="Reusable Test Design", active_tool_id="regen")
    saved = manager.save_state(session)
    loaded = manager.load_state()
    snapshot = build_design_session_manager_snapshot(ROOT)
    summary = snapshot["summary"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if summary.get("canonical_user_design_root") != USER_DESIGN_ROOT:
        failures.append("canonical_user_design_root_invalid")

    if not str(session.design_path).startswith(f"{USER_DESIGN_ROOT}/"):
        failures.append("session_design_path_not_user_visible")

    if loaded.get("valid") is not True:
        failures.append("loaded_session_state_invalid")

    if saved.get("state_type") != "session_metadata_only":
        failures.append("state_type_invalid")

    for key in [
        "user_visible_storage",
        "filesystem_mutation_limited_to_session_metadata",
        "ready_for_22e_engineering_document_model",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true:{key}")

    for key in [
        "internal_storage",
        "qt_owns_design_logic",
        "stores_engineering_calculation_data",
        "stores_solver_state",
        "stores_validation_state",
        "stores_report_payloads",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false:{key}")

    result = {
        "phase": "22D",
        "feature": "DESIGN_SESSION_MANAGER",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": summary,
        "failures": failures,
        "snapshot_json": "",
        "completion_notice": "PHASE_22D_COMPLETE_DESIGN_SESSION_MANAGER_ESTABLISHED" if not failures else "PHASE_22D_BLOCKED",
        "next_phase": "22E_ENGINEERING_DOCUMENT_MODEL",
    }

    snapshot_path = OUT / "design_session_manager_snapshot_phase_22d.json"
    gate_json = OUT / "design_session_manager_gate_phase_22d.json"
    gate_txt = OUT / "design_session_manager_gate_phase_22d.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    result["snapshot_json"] = snapshot_path.relative_to(ROOT).as_posix()

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 22D DESIGN SESSION MANAGER GATE",
        "==========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"manager_class={summary.get('manager_class')}",
        f"canonical_user_design_root={summary.get('canonical_user_design_root')}",
        f"session_state_path={summary.get('session_state_path')}",
        f"sample_design_path={summary.get('sample_design_path')}",
        f"session_state_exists={summary.get('session_state_exists')}",
        f"session_state_valid={summary.get('session_state_valid')}",
        f"user_visible_storage={summary.get('user_visible_storage')}",
        f"internal_storage={summary.get('internal_storage')}",
        f"qt_owns_design_logic={summary.get('qt_owns_design_logic')}",
        f"stores_engineering_calculation_data={summary.get('stores_engineering_calculation_data')}",
        f"stores_solver_state={summary.get('stores_solver_state')}",
        f"stores_validation_state={summary.get('stores_validation_state')}",
        f"stores_report_payloads={summary.get('stores_report_payloads')}",
        f"filesystem_mutation_limited_to_session_metadata={summary.get('filesystem_mutation_limited_to_session_metadata')}",
        f"ready_for_22e_engineering_document_model={summary.get('ready_for_22e_engineering_document_model')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_22D_DESIGN_SESSION_MANAGER" if result["passed"] else "FAIL_PHASE_22D_DESIGN_SESSION_MANAGER")
    print(f"schema={result['schema']}")
    print(f"manager_class={summary.get('manager_class')}")
    print(f"canonical_user_design_root={summary.get('canonical_user_design_root')}")
    print(f"session_state_path={summary.get('session_state_path')}")
    print(f"sample_design_path={summary.get('sample_design_path')}")
    print(f"session_state_valid={summary.get('session_state_valid')}")
    print(f"user_visible_storage={summary.get('user_visible_storage')}")
    print(f"internal_storage={summary.get('internal_storage')}")
    print(f"qt_owns_design_logic={summary.get('qt_owns_design_logic')}")
    print(f"filesystem_mutation_limited_to_session_metadata={summary.get('filesystem_mutation_limited_to_session_metadata')}")
    print(f"ready_for_22e_engineering_document_model={summary.get('ready_for_22e_engineering_document_model')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
