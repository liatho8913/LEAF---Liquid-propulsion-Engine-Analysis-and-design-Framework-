from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_WORKSPACE_ACTIVATION_COMPLETION_PHASE_20F_V1"

PHASE_ARTIFACTS = {
    "20A": {
        "path": "_leaf_artifacts/workspace_architecture/phase_20a/workspace_sidebar_model_phase_20a.json",
        "schema": "LEAF_WORKSPACE_SIDEBAR_MODEL_PHASE_20A_V1",
    },
    "20B": {
        "path": "_leaf_artifacts/workspace_architecture/phase_20b/workspace_panel_data_providers_phase_20b.json",
        "schema": "LEAF_WORKSPACE_PANEL_DATA_PROVIDERS_PHASE_20B_V1",
    },
    "20C": {
        "path": "_leaf_artifacts/workspace_architecture/phase_20c/workspace_action_model_phase_20c.json",
        "schema": "LEAF_WORKSPACE_ACTION_MODEL_PHASE_20C_V1",
    },
    "20D": {
        "path": "_leaf_artifacts/workspace_architecture/phase_20d/import_review_ui_model_phase_20d.json",
        "schema": "LEAF_IMPORT_REVIEW_UI_MODEL_PHASE_20D_V1",
    },
    "20E": {
        "path": "_leaf_artifacts/workspace_architecture/phase_20e/sorting_health_dashboard_model_phase_20e.json",
        "schema": "LEAF_SORTING_HEALTH_DASHBOARD_MODEL_PHASE_20E_V1",
    },
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_workspace_activation_completion_certificate(root: str | Path = ".") -> dict[str, Any]:
    root = Path(root)
    failures: list[str] = []
    artifacts: dict[str, dict[str, Any]] = {}

    for phase, spec in PHASE_ARTIFACTS.items():
        path = root / spec["path"]
        data = _load_json(path)

        if data is None:
            failures.append(f"missing_artifact:{phase}:{spec['path']}")
            artifacts[phase] = {"path": spec["path"], "present": False, "schema_valid": False}
            continue

        schema_valid = data.get("schema") == spec["schema"]
        if not schema_valid:
            failures.append(f"schema_invalid:{phase}:{data.get('schema')}")

        artifacts[phase] = {
            "path": spec["path"],
            "present": True,
            "schema": data.get("schema"),
            "schema_valid": schema_valid,
            "summary": data.get("summary", {}),
            "activation_status": data.get("activation_status", {}),
            "execution_policy": data.get("execution_policy", {}),
        }

    sidebar = artifacts.get("20A", {}).get("summary", {})
    panels = artifacts.get("20B", {}).get("summary", {})
    actions = artifacts.get("20C", {}).get("summary", {})
    review_ui = artifacts.get("20D", {}).get("summary", {})
    dashboard = artifacts.get("20E", {}).get("summary", {})

    if sidebar.get("ready_for_qt_binding") is not True:
        failures.append("20A_not_ready_for_qt_binding")

    if panels.get("ready_for_qt_binding") is not True:
        failures.append("20B_not_ready_for_qt_binding")

    if actions.get("ready_for_qt_binding") is not True:
        failures.append("20C_not_ready_for_qt_binding")

    if review_ui.get("ready_for_qt_binding") is not True:
        failures.append("20D_not_ready_for_qt_binding")

    if dashboard.get("ready_for_qt_binding") is not True:
        failures.append("20E_not_ready_for_qt_binding")

    if sidebar.get("developer_internal_items_exposed", 0) != 0:
        failures.append("20A_developer_internal_items_exposed")

    if panels.get("developer_internal_panels_exposed", 0) != 0:
        failures.append("20B_developer_internal_panels_exposed")

    if actions.get("unsafe_enabled_actions", 0) != 0:
        failures.append("20C_unsafe_enabled_actions")

    if review_ui.get("approval_writeback_enabled") is not False:
        failures.append("20D_approval_writeback_enabled")

    if review_ui.get("execution_buttons_enabled") is not False:
        failures.append("20D_execution_buttons_enabled")

    if dashboard.get("unsafe_flags", 0) != 0:
        failures.append("20E_unsafe_flags_nonzero")

    programme_completed = not failures

    return {
        "schema": SCHEMA,
        "phase": "20F",
        "feature": "WORKSPACE_ACTIVATION_COMPLETION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "programme_completed": programme_completed,
        "completion_notice": "PHASE_20F_COMPLETE_WORKSPACE_ACTIVATION_SIGNED_OFF" if programme_completed else "PHASE_20F_BLOCKED",
        "workspace_activation_completed_phases": [
            "20A Workspace Sidebar Model",
            "20B Workspace Panel Data Providers",
            "20C Workspace Open / Save / Import Action Model",
            "20D Import Review UI Model",
            "20E Sorting Health Dashboard Model",
            "20F Workspace Activation Completion",
        ],
        "activation_status": {
            "workspace_sidebar_model_ready": sidebar.get("workspace_sidebar_model_ready"),
            "panel_data_providers_ready": panels.get("ready_for_qt_binding"),
            "action_model_ready": actions.get("ready_for_qt_binding"),
            "import_review_ui_model_ready": review_ui.get("ready_for_qt_binding"),
            "sorting_health_dashboard_model_ready": dashboard.get("ready_for_qt_binding"),
            "ready_for_qt_workspace_binding": programme_completed,
            "qt_widgets_created": False,
            "gui_execution_active": False,
            "automatic_import_active": False,
        },
        "design_philosophy_signed_off": {
            "models_before_widgets": True,
            "qt_widgets_consume_reusable_workspace_models": True,
            "no_repository_paths_hardcoded_into_widgets": True,
            "developer_architecture_hidden_from_engineer_workflow": True,
            "user_facing_navigation_uses_designs_projects_reports_exports": True,
            "dangerous_actions_locked_until_dedicated_approval_ui": True,
            "sustainability_means_no_duplicate_gui_logic": True,
        },
        "summary": {
            "artifacts_required": len(PHASE_ARTIFACTS),
            "artifacts_present": sum(1 for item in artifacts.values() if item.get("present")),
            "schemas_valid": sum(1 for item in artifacts.values() if item.get("schema_valid")),
            "sidebar_items": sidebar.get("sidebar_items", 0),
            "panel_providers": panels.get("panel_providers", 0),
            "actions": actions.get("actions", 0),
            "review_rows": review_ui.get("review_rows", 0),
            "dashboard_cards": dashboard.get("dashboard_cards", 0),
            "unsafe_enabled_actions": actions.get("unsafe_enabled_actions", 0),
            "unsafe_dashboard_flags": dashboard.get("unsafe_flags", 0),
            "programme_completed": programme_completed,
            "ready_for_next_programme": programme_completed,
            "next_programme": "21_QT_WORKSPACE_UI_BINDING",
        },
        "phase_artifacts": artifacts,
        "safety_locks": {
            "qt_widgets_created": False,
            "gui_execution_allowed": False,
            "approval_writeback_allowed": False,
            "automatic_import_allowed": False,
            "automatic_delete_allowed": False,
            "automatic_move_allowed": False,
            "automatic_archive_allowed": False,
            "completion_gate_execution_allowed": False,
        },
        "failures": failures,
        "next_recommended_programme": {
            "name": "Qt Workspace UI Binding",
            "purpose": "Bind the completed workspace sidebar, panels, actions, import review model, and sorting health dashboard into the actual PySide6 interface.",
            "first_feature": "21A Qt Workspace Sidebar Shell",
        },
    }


def write_workspace_activation_completion_certificate(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/workspace_architecture/phase_20f/workspace_activation_completion_certificate_phase_20f.json",
) -> dict[str, Any]:
    certificate = build_workspace_activation_completion_certificate(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    return certificate


if __name__ == "__main__":
    cert = write_workspace_activation_completion_certificate(".")
    summary = cert["summary"]

    print("LEAF_WORKSPACE_ACTIVATION_COMPLETION_PHASE_20F")
    print(f"schema={cert['schema']}")
    print(f"programme_completed={cert['programme_completed']}")
    print(f"artifacts_required={summary['artifacts_required']}")
    print(f"artifacts_present={summary['artifacts_present']}")
    print(f"schemas_valid={summary['schemas_valid']}")
    print(f"sidebar_items={summary['sidebar_items']}")
    print(f"panel_providers={summary['panel_providers']}")
    print(f"actions={summary['actions']}")
    print(f"review_rows={summary['review_rows']}")
    print(f"dashboard_cards={summary['dashboard_cards']}")
    print(f"completion_notice={cert['completion_notice']}")
    print(f"next_programme={summary['next_programme']}")
