from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.workspace_main_window_phase_21f import (
    SCHEMA,
    build_workspace_main_window_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21f"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_main_window_phase_21f.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_panel_shell_phase_21b.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_toolbar_phase_21c.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "import_review_window_phase_21d.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "sorting_health_dashboard_phase_21e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "qt_workspace_main_window_gate_phase_21f.py",
]

MODULES.extend(sorted((ROOT / "leaf_qt").glob("*sidebar*21a*.py")))


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    snapshot = build_workspace_main_window_snapshot(ROOT)
    summary = snapshot["summary"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    for key in [
        "presentation_only",
        "integrates_phase_21a_sidebar",
        "integrates_phase_21b_panel_shell",
        "integrates_phase_21c_toolbar",
        "integrates_phase_21d_import_review_window",
        "integrates_phase_21e_sorting_health_dashboard",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true={key}")

    for key in [
        "qt_owns_repository_logic",
        "qt_owns_sorting_logic",
        "qt_owns_action_logic",
        "imports_files",
        "copies_files",
        "moves_files",
        "deletes_files",
        "archives_files",
        "automatic_import_allowed",
        "unsafe_toolbar_actions_execute",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false={key}")

    snapshot_path = OUT / "qt_workspace_main_window_snapshot_phase_21f.json"
    gate_json = OUT / "qt_workspace_main_window_gate_phase_21f.json"
    gate_txt = OUT / "qt_workspace_main_window_gate_phase_21f.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    result = {
        "phase": "21F",
        "feature": "QT_WORKSPACE_MAIN_WINDOW_INTEGRATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": snapshot.get("schema"),
        "summary": summary,
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_21F_COMPLETE_WORKSPACE_MAIN_WINDOW_INTEGRATION_ESTABLISHED" if not failures else "PHASE_21F_BLOCKED",
        "next_phase": "21G_WORKSPACE_LAYOUT_PERSISTENCE",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 21F WORKSPACE MAIN WINDOW INTEGRATION",
        "================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"main_window_class={summary.get('main_window_class')}",
        f"sidebar_shell_class={summary.get('sidebar_shell_class')}",
        f"panel_shell_class={summary.get('panel_shell_class')}",
        f"toolbar_class={summary.get('toolbar_class')}",
        f"import_review_window_class={summary.get('import_review_window_class')}",
        f"sorting_health_dashboard_class={summary.get('sorting_health_dashboard_class')}",
        f"presentation_only={summary.get('presentation_only')}",
        f"integrates_phase_21a_sidebar={summary.get('integrates_phase_21a_sidebar')}",
        f"integrates_phase_21b_panel_shell={summary.get('integrates_phase_21b_panel_shell')}",
        f"integrates_phase_21c_toolbar={summary.get('integrates_phase_21c_toolbar')}",
        f"integrates_phase_21d_import_review_window={summary.get('integrates_phase_21d_import_review_window')}",
        f"integrates_phase_21e_sorting_health_dashboard={summary.get('integrates_phase_21e_sorting_health_dashboard')}",
        f"qt_owns_repository_logic={summary.get('qt_owns_repository_logic')}",
        f"qt_owns_sorting_logic={summary.get('qt_owns_sorting_logic')}",
        f"qt_owns_action_logic={summary.get('qt_owns_action_logic')}",
        f"imports_files={summary.get('imports_files')}",
        f"moves_files={summary.get('moves_files')}",
        f"deletes_files={summary.get('deletes_files')}",
        f"archives_files={summary.get('archives_files')}",
        f"automatic_import_allowed={summary.get('automatic_import_allowed')}",
        f"unsafe_toolbar_actions_execute={summary.get('unsafe_toolbar_actions_execute')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_21F_WORKSPACE_MAIN_WINDOW_INTEGRATION" if result["passed"] else "FAIL_PHASE_21F_WORKSPACE_MAIN_WINDOW_INTEGRATION")
    print(f"schema={result['schema']}")
    print(f"main_window_class={summary.get('main_window_class')}")
    print(f"sidebar_shell_class={summary.get('sidebar_shell_class')}")
    print(f"panel_shell_class={summary.get('panel_shell_class')}")
    print(f"toolbar_class={summary.get('toolbar_class')}")
    print(f"import_review_window_class={summary.get('import_review_window_class')}")
    print(f"sorting_health_dashboard_class={summary.get('sorting_health_dashboard_class')}")
    print(f"presentation_only={summary.get('presentation_only')}")
    print(f"integrates_phase_21a_sidebar={summary.get('integrates_phase_21a_sidebar')}")
    print(f"integrates_phase_21b_panel_shell={summary.get('integrates_phase_21b_panel_shell')}")
    print(f"integrates_phase_21c_toolbar={summary.get('integrates_phase_21c_toolbar')}")
    print(f"integrates_phase_21d_import_review_window={summary.get('integrates_phase_21d_import_review_window')}")
    print(f"integrates_phase_21e_sorting_health_dashboard={summary.get('integrates_phase_21e_sorting_health_dashboard')}")
    print(f"qt_owns_repository_logic={summary.get('qt_owns_repository_logic')}")
    print(f"qt_owns_sorting_logic={summary.get('qt_owns_sorting_logic')}")
    print(f"qt_owns_action_logic={summary.get('qt_owns_action_logic')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
