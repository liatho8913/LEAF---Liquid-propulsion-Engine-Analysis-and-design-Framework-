from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from project_maintenance.workspace_architecture.engineering_tool_registry_phase_22b import (
    build_engineering_tool_registry,
)
from project_maintenance.workspace_architecture.engineering_panel_contract_phase_22c import (
    build_engineering_panel_contracts,
)
from project_maintenance.workspace_architecture.design_session_manager_phase_22d import (
    DesignSessionManager,
)
from project_maintenance.workspace_architecture.report_export_routing_phase_22f import (
    build_report_export_routing_model,
)

SCHEMA = "LEAF_WORKSPACE_TOOL_ACTIVATION_BINDING_PHASE_22G_V1"


@dataclass(frozen=True)
class WorkspaceToolActivationBinding:
    tool_id: str
    label: str
    panel_id: str
    activation_state: str
    session_required: bool
    report_routes_available: int
    export_routes_available: int
    workspace_visible: bool
    workspace_enabled: bool
    blocked_reason: str
    qt_executes_solver: bool
    qt_generates_reports: bool
    qt_generates_exports: bool
    filesystem_mutation: bool


def build_workspace_tool_activation_binding(project_root: str | Path = ".") -> dict[str, Any]:
    registry = build_engineering_tool_registry(project_root)
    panel_contracts = build_engineering_panel_contracts(project_root)
    routing = build_report_export_routing_model(project_root)

    manager = DesignSessionManager(project_root)
    session = manager.create_session(design_label="Workspace Activation Session", active_tool_id=None)
    manager.save_state(session)

    contract_by_tool = {
        contract["tool_id"]: contract
        for contract in panel_contracts.get("contracts", [])
    }

    routes_by_tool: dict[str, list[dict[str, Any]]] = {}
    for route in routing.get("routes", []):
        routes_by_tool.setdefault(route["source_tool_id"], []).append(route)

    bindings: list[WorkspaceToolActivationBinding] = []

    for tool in registry.get("tools", []):
        tool_id = tool["tool_id"]
        contract = contract_by_tool.get(tool_id)
        routes = routes_by_tool.get(tool_id, [])

        report_routes = [route for route in routes if route.get("output_type") == "report"]
        export_routes = [route for route in routes if route.get("output_type") == "export"]

        has_contract = contract is not None
        session_required = tool_id in {
            "regen",
            "materials",
            "coatings",
            "graph_explorer",
            "station_viewer",
        }

        workspace_visible = bool(tool.get("user_visible")) and has_contract
        workspace_enabled = workspace_visible and (
            not session_required or bool(session.session_id)
        )

        blocked_reason = ""
        if not has_contract:
            blocked_reason = "missing_panel_contract"
        elif session_required and not session.session_id:
            blocked_reason = "missing_design_session"
        elif tool.get("activation_state") != "planned":
            blocked_reason = f"unsupported_activation_state:{tool.get('activation_state')}"

        bindings.append(
            WorkspaceToolActivationBinding(
                tool_id=tool_id,
                label=tool["label"],
                panel_id=contract["panel_id"] if contract else "",
                activation_state="workspace_bound_pending_real_tool_adapter",
                session_required=session_required,
                report_routes_available=len(report_routes),
                export_routes_available=len(export_routes),
                workspace_visible=workspace_visible,
                workspace_enabled=workspace_enabled,
                blocked_reason=blocked_reason,
                qt_executes_solver=False,
                qt_generates_reports=False,
                qt_generates_exports=False,
                filesystem_mutation=False,
            )
        )

    return {
        "schema": SCHEMA,
        "phase": "22G",
        "feature": "WORKSPACE_TOOL_ACTIVATION_BINDING",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_registry_schema": registry.get("schema"),
        "source_panel_contract_schema": panel_contracts.get("schema"),
        "source_routing_schema": routing.get("schema"),
        "session_schema": "LEAF_DESIGN_SESSION_MANAGER_PHASE_22D_V1",
        "activation_rule": "Workspace activation may make tools visible and selectable, but it must not execute solvers, generate reports, generate exports, or mutate files.",
        "bindings": [asdict(binding) for binding in bindings],
        "summary": {
            "binding_count": len(bindings),
            "workspace_visible_tools": sum(1 for binding in bindings if binding.workspace_visible),
            "workspace_enabled_tools": sum(1 for binding in bindings if binding.workspace_enabled),
            "session_required_tools": sum(1 for binding in bindings if binding.session_required),
            "tools_with_report_routes": sum(1 for binding in bindings if binding.report_routes_available > 0),
            "tools_with_export_routes": sum(1 for binding in bindings if binding.export_routes_available > 0),
            "blocked_tools": sum(1 for binding in bindings if binding.blocked_reason),
            "qt_executes_solver_count": sum(1 for binding in bindings if binding.qt_executes_solver),
            "qt_generates_reports_count": sum(1 for binding in bindings if binding.qt_generates_reports),
            "qt_generates_exports_count": sum(1 for binding in bindings if binding.qt_generates_exports),
            "filesystem_mutation_count": sum(1 for binding in bindings if binding.filesystem_mutation),
            "activation_binding_is_metadata_only": True,
            "ready_for_22h_engineering_workspace_completion_gate": True,
        },
        "safety_boundaries": {
            "qt_executes_solver": False,
            "qt_generates_reports": False,
            "qt_generates_exports": False,
            "qt_owns_tool_logic": False,
            "filesystem_mutation": False,
            "automatic_sorting_activation": False,
        },
    }


def write_workspace_tool_activation_binding(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_22g"
    out_dir.mkdir(parents=True, exist_ok=True)

    model = build_workspace_tool_activation_binding(root)

    json_path = out_dir / "workspace_tool_activation_binding_phase_22g.json"
    txt_path = out_dir / "workspace_tool_activation_binding_phase_22g.txt"

    json_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    txt_path.write_text("\n".join([
        "LEAF PHASE 22G WORKSPACE TOOL ACTIVATION BINDING",
        "================================================",
        f"schema={model['schema']}",
        f"phase={model['phase']}",
        f"feature={model['feature']}",
        f"source_registry_schema={model['source_registry_schema']}",
        f"source_panel_contract_schema={model['source_panel_contract_schema']}",
        f"source_routing_schema={model['source_routing_schema']}",
        f"binding_count={model['summary']['binding_count']}",
        f"workspace_visible_tools={model['summary']['workspace_visible_tools']}",
        f"workspace_enabled_tools={model['summary']['workspace_enabled_tools']}",
        f"session_required_tools={model['summary']['session_required_tools']}",
        f"tools_with_report_routes={model['summary']['tools_with_report_routes']}",
        f"tools_with_export_routes={model['summary']['tools_with_export_routes']}",
        f"blocked_tools={model['summary']['blocked_tools']}",
        f"qt_executes_solver_count={model['summary']['qt_executes_solver_count']}",
        f"qt_generates_reports_count={model['summary']['qt_generates_reports_count']}",
        f"qt_generates_exports_count={model['summary']['qt_generates_exports_count']}",
        f"filesystem_mutation_count={model['summary']['filesystem_mutation_count']}",
        f"activation_binding_is_metadata_only={model['summary']['activation_binding_is_metadata_only']}",
        f"ready_for_22h_engineering_workspace_completion_gate={model['summary']['ready_for_22h_engineering_workspace_completion_gate']}",
        "",
        "Bindings:",
        *[
            f"{binding['tool_id']} -> {binding['panel_id']} -> visible={binding['workspace_visible']} enabled={binding['workspace_enabled']}"
            for binding in model["bindings"]
        ],
    ]), encoding="utf-8")

    return {
        "model": model,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_workspace_tool_activation_binding(Path.cwd())
    print("PASS_PHASE_22G_WORKSPACE_TOOL_ACTIVATION_BINDING_WRITTEN")
    print(f"schema={result['model']['schema']}")
    print(f"binding_count={result['model']['summary']['binding_count']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
