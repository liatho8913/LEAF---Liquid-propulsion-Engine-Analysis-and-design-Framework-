from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from project_maintenance.workspace_architecture.engineering_document_model_phase_22e import (
    USER_EXPORT_ROOT,
    USER_REPORT_ROOT,
    build_engineering_document_model,
)
from project_maintenance.workspace_architecture.engineering_tool_registry_phase_22b import (
    build_engineering_tool_registry,
)

SCHEMA = "LEAF_REPORT_EXPORT_ROUTING_PHASE_22F_V1"


@dataclass(frozen=True)
class ReportExportRoute:
    route_id: str
    source_tool_id: str
    output_type: str
    owner_layer: str
    canonical_root: str
    default_extension: str
    workspace_document_type: str
    generation_owner: str
    qt_generates_output: bool
    qt_owns_report_logic: bool
    qt_owns_export_logic: bool
    filesystem_mutation_requires_user_action: bool


def build_report_export_routing_model(project_root: str | Path = ".") -> dict[str, Any]:
    tool_registry = build_engineering_tool_registry(project_root)
    document_model = build_engineering_document_model(project_root)

    engineering_tools = [
        tool for tool in tool_registry.get("tools", [])
        if tool.get("tool_id") in {
            "regen",
            "materials",
            "coatings",
            "graph_explorer",
            "station_viewer",
        }
    ]

    routes: list[ReportExportRoute] = []

    for tool in engineering_tools:
        tool_id = tool["tool_id"]

        routes.append(
            ReportExportRoute(
                route_id=f"{tool_id}_report_route",
                source_tool_id=tool_id,
                output_type="report",
                owner_layer=tool.get("report_owner", "report_owner"),
                canonical_root=USER_REPORT_ROOT,
                default_extension=".leaf_report.json",
                workspace_document_type="report",
                generation_owner=tool.get("report_owner", "report_owner"),
                qt_generates_output=False,
                qt_owns_report_logic=False,
                qt_owns_export_logic=False,
                filesystem_mutation_requires_user_action=True,
            )
        )

        routes.append(
            ReportExportRoute(
                route_id=f"{tool_id}_export_route",
                source_tool_id=tool_id,
                output_type="export",
                owner_layer="export_owner",
                canonical_root=USER_EXPORT_ROOT,
                default_extension=".leaf_export",
                workspace_document_type="export",
                generation_owner="export_owner",
                qt_generates_output=False,
                qt_owns_report_logic=False,
                qt_owns_export_logic=False,
                filesystem_mutation_requires_user_action=True,
            )
        )

    return {
        "schema": SCHEMA,
        "phase": "22F",
        "feature": "REPORT_AND_EXPORT_ROUTING",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_tool_registry_schema": tool_registry.get("schema"),
        "source_document_model_schema": document_model.get("schema"),
        "routing_rule": "Reports and exports route through canonical document roots and ownership layers. Qt may request routing but must not generate report/export payloads.",
        "routes": [asdict(route) for route in routes],
        "summary": {
            "route_count": len(routes),
            "report_routes": sum(1 for route in routes if route.output_type == "report"),
            "export_routes": sum(1 for route in routes if route.output_type == "export"),
            "source_engineering_tools": len(engineering_tools),
            "report_root": USER_REPORT_ROOT,
            "export_root": USER_EXPORT_ROOT,
            "qt_generates_output_count": sum(1 for route in routes if route.qt_generates_output),
            "qt_owns_report_logic_count": sum(1 for route in routes if route.qt_owns_report_logic),
            "qt_owns_export_logic_count": sum(1 for route in routes if route.qt_owns_export_logic),
            "filesystem_mutation_requires_user_action_count": sum(
                1 for route in routes if route.filesystem_mutation_requires_user_action
            ),
            "routes_are_metadata_only": True,
            "ready_for_22g_workspace_tool_activation_binding": True,
        },
        "safety_boundaries": {
            "qt_generates_reports": False,
            "qt_generates_exports": False,
            "qt_owns_report_logic": False,
            "qt_owns_export_logic": False,
            "automatic_filesystem_mutation": False,
            "automatic_sorting_activation": False,
            "solver_execution": False,
        },
    }


def write_report_export_routing_model(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_22f"
    out_dir.mkdir(parents=True, exist_ok=True)

    model = build_report_export_routing_model(root)

    json_path = out_dir / "report_export_routing_phase_22f.json"
    txt_path = out_dir / "report_export_routing_phase_22f.txt"

    json_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    txt_path.write_text("\n".join([
        "LEAF PHASE 22F REPORT AND EXPORT ROUTING",
        "========================================",
        f"schema={model['schema']}",
        f"phase={model['phase']}",
        f"feature={model['feature']}",
        f"source_tool_registry_schema={model['source_tool_registry_schema']}",
        f"source_document_model_schema={model['source_document_model_schema']}",
        f"route_count={model['summary']['route_count']}",
        f"report_routes={model['summary']['report_routes']}",
        f"export_routes={model['summary']['export_routes']}",
        f"source_engineering_tools={model['summary']['source_engineering_tools']}",
        f"report_root={model['summary']['report_root']}",
        f"export_root={model['summary']['export_root']}",
        f"qt_generates_output_count={model['summary']['qt_generates_output_count']}",
        f"qt_owns_report_logic_count={model['summary']['qt_owns_report_logic_count']}",
        f"qt_owns_export_logic_count={model['summary']['qt_owns_export_logic_count']}",
        f"routes_are_metadata_only={model['summary']['routes_are_metadata_only']}",
        f"ready_for_22g_workspace_tool_activation_binding={model['summary']['ready_for_22g_workspace_tool_activation_binding']}",
        "",
        "Routes:",
        *[
            f"{route['route_id']} -> {route['source_tool_id']} -> {route['output_type']} -> {route['canonical_root']}"
            for route in model["routes"]
        ],
    ]), encoding="utf-8")

    return {
        "model": model,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_report_export_routing_model(Path.cwd())
    print("PASS_PHASE_22F_REPORT_EXPORT_ROUTING_WRITTEN")
    print(f"schema={result['model']['schema']}")
    print(f"route_count={result['model']['summary']['route_count']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
