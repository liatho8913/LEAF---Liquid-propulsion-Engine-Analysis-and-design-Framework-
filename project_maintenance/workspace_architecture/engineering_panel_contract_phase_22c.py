from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from project_maintenance.workspace_architecture.engineering_tool_registry_phase_22b import (
    build_engineering_tool_registry,
)

SCHEMA = "LEAF_ENGINEERING_PANEL_CONTRACT_PHASE_22C_V1"


@dataclass(frozen=True)
class EngineeringPanelContract:
    tool_id: str
    panel_id: str
    panel_label: str
    required_model_contract: str
    required_controller_contract: str
    required_validation_contract: str
    required_report_contract: str
    workspace_adapter: str
    qt_binding_state: str
    qt_executes_solver: bool
    qt_owns_validation: bool
    qt_owns_reports: bool
    filesystem_mutation: bool


def build_engineering_panel_contracts(project_root: str | Path = ".") -> dict[str, Any]:
    registry = build_engineering_tool_registry(project_root)
    tools = registry.get("tools", [])

    contracts: list[EngineeringPanelContract] = []

    for tool in tools:
        tool_id = tool["tool_id"]
        label = tool["label"]

        contracts.append(
            EngineeringPanelContract(
                tool_id=tool_id,
                panel_id=f"engineering_panel_{tool_id}",
                panel_label=label,
                required_model_contract=f"{tool_id}_model_contract",
                required_controller_contract=f"{tool_id}_controller_contract",
                required_validation_contract=f"{tool_id}_validation_contract",
                required_report_contract=f"{tool_id}_report_contract",
                workspace_adapter=f"{tool_id}_workspace_panel_adapter",
                qt_binding_state="contract_defined_pending_binding",
                qt_executes_solver=False,
                qt_owns_validation=False,
                qt_owns_reports=False,
                filesystem_mutation=False,
            )
        )

    return {
        "schema": SCHEMA,
        "phase": "22C",
        "feature": "ENGINEERING_PANEL_CONTRACT",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "source_registry_schema": registry.get("schema"),
        "contract_rule": "Engineering panels expose contracts to the workspace. Qt may render a panel but must not own solver, validation, report, or filesystem logic.",
        "contracts": [asdict(contract) for contract in contracts],
        "contract_flow": [
            "Engineering Tool Registry",
            "Engineering Panel Contract",
            "Workspace Adapter",
            "Qt Panel Shell",
        ],
        "forbidden_flow": [
            "Qt Widget",
            "Direct Solver Call",
            "Direct Validation Mutation",
            "Direct Report Generation",
            "Direct Filesystem Mutation",
        ],
        "summary": {
            "contract_count": len(contracts),
            "registered_tool_count": len(tools),
            "all_registered_tools_have_panel_contracts": len(contracts) == len(tools),
            "qt_executes_solver_count": sum(1 for contract in contracts if contract.qt_executes_solver),
            "qt_owns_validation_count": sum(1 for contract in contracts if contract.qt_owns_validation),
            "qt_owns_reports_count": sum(1 for contract in contracts if contract.qt_owns_reports),
            "filesystem_mutation_count": sum(1 for contract in contracts if contract.filesystem_mutation),
            "contracts_are_metadata_only": True,
            "ready_for_22d_design_session_manager": True,
        },
        "safety_boundaries": {
            "qt_executes_solver": False,
            "qt_owns_validation": False,
            "qt_owns_reports": False,
            "qt_owns_filesystem_mutation": False,
            "automatic_sorting_activation": False,
            "engineering_calculation_execution": False,
        },
    }


def write_engineering_panel_contracts(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_22c"
    out_dir.mkdir(parents=True, exist_ok=True)

    contracts = build_engineering_panel_contracts(root)

    json_path = out_dir / "engineering_panel_contract_phase_22c.json"
    txt_path = out_dir / "engineering_panel_contract_phase_22c.txt"

    json_path.write_text(json.dumps(contracts, indent=2), encoding="utf-8")

    txt_path.write_text("\n".join([
        "LEAF PHASE 22C ENGINEERING PANEL CONTRACT",
        "=========================================",
        f"schema={contracts['schema']}",
        f"phase={contracts['phase']}",
        f"feature={contracts['feature']}",
        f"source_registry_schema={contracts['source_registry_schema']}",
        f"contract_count={contracts['summary']['contract_count']}",
        f"registered_tool_count={contracts['summary']['registered_tool_count']}",
        f"all_registered_tools_have_panel_contracts={contracts['summary']['all_registered_tools_have_panel_contracts']}",
        f"qt_executes_solver_count={contracts['summary']['qt_executes_solver_count']}",
        f"qt_owns_validation_count={contracts['summary']['qt_owns_validation_count']}",
        f"qt_owns_reports_count={contracts['summary']['qt_owns_reports_count']}",
        f"filesystem_mutation_count={contracts['summary']['filesystem_mutation_count']}",
        f"contracts_are_metadata_only={contracts['summary']['contracts_are_metadata_only']}",
        f"ready_for_22d_design_session_manager={contracts['summary']['ready_for_22d_design_session_manager']}",
        "",
        "Panel Contracts:",
        *[
            f"{contract['tool_id']} -> {contract['panel_id']} -> {contract['workspace_adapter']}"
            for contract in contracts["contracts"]
        ],
    ]), encoding="utf-8")

    return {
        "contracts": contracts,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_engineering_panel_contracts(Path.cwd())
    print("PASS_PHASE_22C_ENGINEERING_PANEL_CONTRACT_WRITTEN")
    print(f"schema={result['contracts']['schema']}")
    print(f"contract_count={result['contracts']['summary']['contract_count']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
