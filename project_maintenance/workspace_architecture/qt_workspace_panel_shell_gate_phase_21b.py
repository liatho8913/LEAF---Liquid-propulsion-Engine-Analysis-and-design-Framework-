from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.workspace_panel_shell_phase_21b import (
    SCHEMA,
    build_workspace_panel_shell_snapshot,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21b"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_panel_shell_phase_21b.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "qt_workspace_panel_shell_gate_phase_21b.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    snapshot = build_workspace_panel_shell_snapshot(ROOT)
    summary = snapshot["summary"]

    if snapshot.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if snapshot.get("source_panel_provider_schema") != "LEAF_WORKSPACE_PANEL_DATA_PROVIDERS_PHASE_20B_V1":
        failures.append("source_panel_provider_schema_invalid")

    if summary.get("panel_providers") != 6:
        failures.append("panel_provider_count_invalid")

    if summary.get("resource_panels") != 4:
        failures.append("resource_panel_count_invalid")

    if summary.get("import_review_panels") != 1:
        failures.append("import_review_panel_count_invalid")

    if summary.get("sorting_health_panels") != 1:
        failures.append("sorting_health_panel_count_invalid")

    if summary.get("developer_internal_panels_exposed") != 0:
        failures.append("developer_internal_panels_exposed")

    if summary.get("panels_requiring_internal_path_knowledge") != 0:
        failures.append("panels_require_internal_path_knowledge")

    for key in [
        "presentation_only",
        "consumes_phase_20b_providers",
        "sidebar_section_mapping_complete",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true={key}")

    for key in [
        "imports_files",
        "moves_files",
        "deletes_files",
        "archives_files",
        "automatic_import_allowed",
    ]:
        if summary.get(key) is not False:
            failures.append(f"unsafe_summary_not_false={key}")

    expected_panels = {
        "Designs",
        "Projects",
        "Reports",
        "Exports",
        "Import Review",
        "Sorting Health",
    }

    if set(snapshot.get("available_panels", [])) != expected_panels:
        failures.append("available_panels_invalid")

    snapshot_path = OUT / "qt_workspace_panel_shell_snapshot_phase_21b.json"
    gate_json = OUT / "qt_workspace_panel_shell_gate_phase_21b.json"
    gate_txt = OUT / "qt_workspace_panel_shell_gate_phase_21b.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    result = {
        "phase": "21B",
        "feature": "QT_WORKSPACE_PANEL_SHELL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": snapshot.get("schema"),
        "source_panel_provider_schema": snapshot.get("source_panel_provider_schema"),
        "summary": summary,
        "available_panels": snapshot.get("available_panels", []),
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_21B_COMPLETE_QT_WORKSPACE_PANEL_SHELL_ESTABLISHED" if not failures else "PHASE_21B_BLOCKED",
        "next_phase": "21C_QT_WORKSPACE_TOOLBAR",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 21B QT WORKSPACE PANEL SHELL",
        "========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_panel_provider_schema={result['source_panel_provider_schema']}",
        f"panel_providers={summary.get('panel_providers')}",
        f"resource_panels={summary.get('resource_panels')}",
        f"import_review_panels={summary.get('import_review_panels')}",
        f"sorting_health_panels={summary.get('sorting_health_panels')}",
        f"developer_internal_panels_exposed={summary.get('developer_internal_panels_exposed')}",
        f"panels_requiring_internal_path_knowledge={summary.get('panels_requiring_internal_path_knowledge')}",
        f"presentation_only={summary.get('presentation_only')}",
        f"consumes_phase_20b_providers={summary.get('consumes_phase_20b_providers')}",
        f"sidebar_section_mapping_complete={summary.get('sidebar_section_mapping_complete')}",
        f"imports_files={summary.get('imports_files')}",
        f"moves_files={summary.get('moves_files')}",
        f"deletes_files={summary.get('deletes_files')}",
        f"archives_files={summary.get('archives_files')}",
        f"automatic_import_allowed={summary.get('automatic_import_allowed')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"snapshot_json={result['snapshot_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_21B_QT_WORKSPACE_PANEL_SHELL" if result["passed"] else "FAIL_PHASE_21B_QT_WORKSPACE_PANEL_SHELL")
    print(f"schema={result['schema']}")
    print(f"source_panel_provider_schema={result['source_panel_provider_schema']}")
    print(f"panel_providers={summary.get('panel_providers')}")
    print(f"resource_panels={summary.get('resource_panels')}")
    print(f"import_review_panels={summary.get('import_review_panels')}")
    print(f"sorting_health_panels={summary.get('sorting_health_panels')}")
    print(f"developer_internal_panels_exposed={summary.get('developer_internal_panels_exposed')}")
    print(f"panels_requiring_internal_path_knowledge={summary.get('panels_requiring_internal_path_knowledge')}")
    print(f"presentation_only={summary.get('presentation_only')}")
    print(f"consumes_phase_20b_providers={summary.get('consumes_phase_20b_providers')}")
    print(f"sidebar_section_mapping_complete={summary.get('sidebar_section_mapping_complete')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"snapshot_json={result['snapshot_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
