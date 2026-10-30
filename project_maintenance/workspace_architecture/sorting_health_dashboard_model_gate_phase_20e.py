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
    SORTING_HEALTH_SCHEMA as SCHEMA,
    build_sorting_health_dashboard_model,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_20e"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_integration_completion_phase_19g.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_health_dashboard_model_gate_phase_20e.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    model = build_sorting_health_dashboard_model(ROOT)
    summary = model["summary"]
    policy = model["execution_policy"]
    activation = model["activation_status"]

    expected_schemas = {
        "source_sorting_completion_schema": "LEAF_SORTING_INTEGRATION_COMPLETION_PHASE_19G_V1",
        "source_panel_provider_schema": "LEAF_WORKSPACE_PANEL_DATA_PROVIDERS_PHASE_20B_V1",
        "source_import_review_ui_schema": "LEAF_IMPORT_REVIEW_UI_MODEL_PHASE_20D_V1",
    }

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    for key, expected in expected_schemas.items():
        if model.get(key) != expected:
            failures.append(f"{key}_invalid")

    if activation.get("sorting_health_dashboard_model_ready") is not True:
        failures.append("dashboard_model_not_ready")

    if activation.get("ready_for_qt_dashboard_binding") is not True:
        failures.append("not_ready_for_qt_dashboard_binding")

    for key in ["automatic_import_active", "gui_execution_active"]:
        if activation.get(key) is not False:
            failures.append(f"activation_not_false={key}")

    if summary.get("dashboard_cards", 0) < 8:
        failures.append("dashboard_card_count_too_low")

    if summary.get("unsafe_flags") != 0:
        failures.append("unsafe_flags_nonzero")

    if summary.get("developer_internal_cards_exposed") != 0:
        failures.append("developer_internal_cards_exposed")

    if summary.get("cards_requiring_internal_path_knowledge") != 0:
        failures.append("cards_require_internal_path_knowledge")

    for key in ["dashboard_model_only"]:
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

    model_path = OUT / "sorting_health_dashboard_model_phase_20e.json"
    gate_json = OUT / "sorting_health_dashboard_model_gate_phase_20e.json"
    gate_txt = OUT / "sorting_health_dashboard_model_gate_phase_20e.txt"

    model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    result = {
        "phase": "20E",
        "feature": "SORTING_HEALTH_DASHBOARD_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": model.get("schema"),
        "summary": summary,
        "activation_status": activation,
        "failures": failures,
        "dashboard_json": model_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_20E_COMPLETE_SORTING_HEALTH_DASHBOARD_MODEL_ESTABLISHED" if not failures else "PHASE_20E_BLOCKED",
        "next_phase": "20F_WORKSPACE_ACTIVATION_COMPLETION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 20E SORTING HEALTH DASHBOARD MODEL",
        "==============================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"dashboard_cards={summary.get('dashboard_cards')}",
        f"pass_cards={summary.get('pass_cards')}",
        f"review_cards={summary.get('review_cards')}",
        f"unsafe_flags={summary.get('unsafe_flags')}",
        f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}",
        f"developer_internal_cards_exposed={summary.get('developer_internal_cards_exposed')}",
        f"cards_requiring_internal_path_knowledge={summary.get('cards_requiring_internal_path_knowledge')}",
        f"automatic_import_active={activation.get('automatic_import_active')}",
        f"gui_execution_active={activation.get('gui_execution_active')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"dashboard_json={result['dashboard_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_20E_SORTING_HEALTH_DASHBOARD_MODEL" if result["passed"] else "FAIL_PHASE_20E_SORTING_HEALTH_DASHBOARD_MODEL")
    print(f"schema={result['schema']}")
    print(f"dashboard_cards={summary.get('dashboard_cards')}")
    print(f"pass_cards={summary.get('pass_cards')}")
    print(f"review_cards={summary.get('review_cards')}")
    print(f"unsafe_flags={summary.get('unsafe_flags')}")
    print(f"ready_for_qt_binding={summary.get('ready_for_qt_binding')}")
    print(f"developer_internal_cards_exposed={summary.get('developer_internal_cards_exposed')}")
    print(f"cards_requiring_internal_path_knowledge={summary.get('cards_requiring_internal_path_knowledge')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"dashboard_json={result['dashboard_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
