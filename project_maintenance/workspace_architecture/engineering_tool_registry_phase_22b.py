from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_ENGINEERING_TOOL_REGISTRY_PHASE_22B_V1"


@dataclass(frozen=True)
class EngineeringToolRecord:
    tool_id: str
    label: str
    category: str
    owner_layer: str
    model_source: str
    controller_source: str
    validation_owner: str
    report_owner: str
    workspace_panel_adapter: str
    activation_state: str
    user_visible: bool
    qt_executes_solver: bool
    qt_owns_logic: bool


def build_engineering_tool_registry(project_root: str | Path = ".") -> dict[str, Any]:
    tools = [
        EngineeringToolRecord(
            "regen",
            "Regenerative Cooling",
            "thermal_management",
            "engineering_module",
            "leaf_qt regen model/controller stack",
            "existing regen controllers",
            "existing regen validation owners",
            "existing regen report owners",
            "pending_22c_panel_contract",
            "planned",
            True,
            False,
            False,
        ),
        EngineeringToolRecord(
            "materials",
            "Materials",
            "materials",
            "engineering_module",
            "leaf_qt material database/model stack",
            "existing material controllers",
            "existing material validation/source-quality owners",
            "existing material/coating report owners",
            "pending_22c_panel_contract",
            "planned",
            True,
            False,
            False,
        ),
        EngineeringToolRecord(
            "coatings",
            "Coatings",
            "materials",
            "engineering_module",
            "leaf_qt coating/source-quality stack",
            "existing coating controllers",
            "existing coating validation/source-quality owners",
            "existing coating report owners",
            "pending_22c_panel_contract",
            "planned",
            True,
            False,
            False,
        ),
        EngineeringToolRecord(
            "graph_explorer",
            "Graph Explorer",
            "analysis",
            "engineering_visualisation",
            "existing graph explorer model inputs",
            "existing graph explorer controller/window",
            "existing variable/dependency validation",
            "export/report routing pending 22f",
            "pending_22c_panel_contract",
            "planned",
            True,
            False,
            False,
        ),
        EngineeringToolRecord(
            "station_viewer",
            "Station Viewer",
            "analysis",
            "engineering_visualisation",
            "existing station table/report model",
            "existing station viewer/controller",
            "existing station validation",
            "existing station report/export owner",
            "pending_22c_panel_contract",
            "planned",
            True,
            False,
            False,
        ),
        EngineeringToolRecord(
            "reports",
            "Reports",
            "documentation",
            "workspace_resource",
            "workspace report resources",
            "existing report ownership layer",
            "report ownership validation",
            "canonical report owners",
            "pending_22c_panel_contract",
            "planned",
            True,
            False,
            False,
        ),
        EngineeringToolRecord(
            "exports",
            "Exports",
            "documentation",
            "workspace_resource",
            "workspace export resources",
            "existing export/report routing",
            "export validation pending 22f",
            "canonical export/report owners",
            "pending_22c_panel_contract",
            "planned",
            True,
            False,
            False,
        ),
    ]

    return {
        "schema": SCHEMA,
        "phase": "22B",
        "feature": "ENGINEERING_TOOL_REGISTRY",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "registry_rule": "Engineering tools register metadata and ownership only. They do not execute through Qt.",
        "tools": [asdict(tool) for tool in tools],
        "summary": {
            "tool_count": len(tools),
            "user_visible_tools": sum(1 for tool in tools if tool.user_visible),
            "planned_tools": sum(1 for tool in tools if tool.activation_state == "planned"),
            "qt_executes_solver_count": sum(1 for tool in tools if tool.qt_executes_solver),
            "qt_owns_logic_count": sum(1 for tool in tools if tool.qt_owns_logic),
            "registry_is_metadata_only": True,
            "ready_for_22c_panel_contract": True,
        },
        "safety_boundaries": {
            "qt_executes_solver": False,
            "qt_owns_engineering_logic": False,
            "registry_executes_tools": False,
            "filesystem_mutation": False,
            "automatic_sorting_activation": False,
        },
    }


def write_engineering_tool_registry(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_22b"
    out_dir.mkdir(parents=True, exist_ok=True)

    registry = build_engineering_tool_registry(root)

    json_path = out_dir / "engineering_tool_registry_phase_22b.json"
    txt_path = out_dir / "engineering_tool_registry_phase_22b.txt"

    json_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    txt_path.write_text("\n".join([
        "LEAF PHASE 22B ENGINEERING TOOL REGISTRY",
        "========================================",
        f"schema={registry['schema']}",
        f"phase={registry['phase']}",
        f"feature={registry['feature']}",
        f"tool_count={registry['summary']['tool_count']}",
        f"user_visible_tools={registry['summary']['user_visible_tools']}",
        f"planned_tools={registry['summary']['planned_tools']}",
        f"qt_executes_solver_count={registry['summary']['qt_executes_solver_count']}",
        f"qt_owns_logic_count={registry['summary']['qt_owns_logic_count']}",
        f"registry_is_metadata_only={registry['summary']['registry_is_metadata_only']}",
        f"ready_for_22c_panel_contract={registry['summary']['ready_for_22c_panel_contract']}",
        "",
        "Registered Tools:",
        *[
            f"{tool['tool_id']} — {tool['label']} — {tool['category']} — {tool['activation_state']}"
            for tool in registry["tools"]
        ],
    ]), encoding="utf-8")

    return {
        "registry": registry,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_engineering_tool_registry(Path.cwd())
    print("PASS_PHASE_22B_ENGINEERING_TOOL_REGISTRY_WRITTEN")
    print(f"schema={result['registry']['schema']}")
    print(f"tool_count={result['registry']['summary']['tool_count']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
