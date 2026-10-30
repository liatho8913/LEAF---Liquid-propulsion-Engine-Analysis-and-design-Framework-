from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.workspace_runtime_core import (
    PANEL_PROVIDER_SCHEMA as SCHEMA,
    build_workspace_panel_data_providers,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_20b"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_integration_completion_phase_19g.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_panel_data_providers_gate_phase_20b.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    providers = build_workspace_panel_data_providers(ROOT)
    summary = providers["summary"]
    policy = providers["execution_policy"]
    activation = providers["activation_status"]

    expected_schemas = {
        "source_sidebar_schema": "LEAF_WORKSPACE_SIDEBAR_MODEL_PHASE_20A_V1",
        "source_navigation_schema": "LEAF_WORKSPACE_NAVIGATION_MODEL_PHASE_18D_V1",
        "source_import_review_schema": "LEAF_IMPORT_REVIEW_REGISTRY_PHASE_19B_V1",
        "source_sorting_completion_schema": "LEAF_SORTING_INTEGRATION_COMPLETION_PHASE_19G_V1",
    }

    if providers.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    for key, expected in expected_schemas.items():
        if providers.get(key) != expected:
            failures.append(f"{key}_invalid")

    if activation.get("panel_data_providers_ready") is not True:
        failures.append("panel_data_providers_not_ready")

    if activation.get("ready_for_qt_panel_binding") is not True:
        failures.append("not_ready_for_qt_panel_binding")

    if activation.get("automatic_import_active") is not False:
        failures.append("automatic_import_active_not_false")

    if activation.get("gui_execution_active") is not False:
        failures.append("gui_execution_active_not_false")

    if summary.get("panel_providers") != 6:
        failures.append("panel_provider_count_invalid")

    if summary.get("sidebar_panel_coverage_complete") is not True:
        failures.append("sidebar_panel_coverage_incomplete")

    if summary.get("missing_panel_providers"):
        failures.append("missing_panel_providers_present")

    if summary.get("developer_internal_panels_exposed") != 0:
        failures.append("developer_internal_panels_exposed")

    if summary.get("panels_requiring_internal_path_knowledge") != 0:
        failures.append("panels_require_internal_path_knowledge")

    for key in ["data_provider_only"]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "qt_widgets_created",
        "imports_files",
        "moves_files",
        "deletes_files",
        "archives_files",
        "automatic_import_allowed",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    for name, panel in providers.get("panels", {}).items():
        if panel.get("developer_internal") is not False:
            failures.append(f"panel_developer_internal={name}")
        if panel.get("user_facing") is not True:
            failures.append(f"panel_not_user_facing={name}")

    provider_path = OUT / "workspace_panel_data_providers_phase_20b.json"
    gate_json = OUT / "workspace_panel_data_providers_gate_phase_20b.json"
    gate_txt = OUT / "workspace_panel_data_providers_gate_phase_20b.txt"

    provider_path.write_text(json.dumps(providers, indent=2), encoding="utf-8")

    result = {
        "phase": "20B",
        "feature": "WORKSPACE_PANEL_DATA_PROVIDERS",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": providers.get("schema"),
        "summary": summary,
        "activation_status": activation,
        "failures": failures,
        "providers_json": provider_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_20B_COMPLETE_WORKSPACE_PANEL_DATA_PROVIDERS_ESTABLISHED" if not failures else "PHASE_20B_BLOCKED",
        "next_phase": "20C_WORKSPACE_OPEN_SAVE_IMPORT_ACTION_MODEL",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 20B WORKSPACE PANEL DATA PROVIDERS",
        "================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"panel_providers={summary.get('panel_providers')}",
        f"sidebar_panel_coverage_complete={summary.get('sidebar_panel_coverage_complete')}",
        f"resource_panels={summary.get('resource_panels')}",
        f"import_review_panel_ready={summary.get('import_review_panel_ready')}",
        f"sorting_health_panel_ready={summary.get('sorting_health_panel_ready')}",
        f"developer_internal_panels_exposed={summary.get('developer_internal_panels_exposed')}",
        f"panels_requiring_internal_path_knowledge={summary.get('panels_requiring_internal_path_knowledge')}",
        f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}",
        f"automatic_import_active={activation.get('automatic_import_active')}",
        f"gui_execution_active={activation.get('gui_execution_active')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"providers_json={result['providers_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_20B_WORKSPACE_PANEL_DATA_PROVIDERS" if result["passed"] else "FAIL_PHASE_20B_WORKSPACE_PANEL_DATA_PROVIDERS")
    print(f"schema={result['schema']}")
    print(f"panel_providers={summary.get('panel_providers')}")
    print(f"sidebar_panel_coverage_complete={summary.get('sidebar_panel_coverage_complete')}")
    print(f"resource_panels={summary.get('resource_panels')}")
    print(f"import_review_panel_ready={summary.get('import_review_panel_ready')}")
    print(f"sorting_health_panel_ready={summary.get('sorting_health_panel_ready')}")
    print(f"developer_internal_panels_exposed={summary.get('developer_internal_panels_exposed')}")
    print(f"panels_requiring_internal_path_knowledge={summary.get('panels_requiring_internal_path_knowledge')}")
    print(f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"providers_json={result['providers_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
