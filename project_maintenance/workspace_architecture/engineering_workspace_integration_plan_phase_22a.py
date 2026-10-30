from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_ENGINEERING_WORKSPACE_INTEGRATION_PLAN_PHASE_22A_V1"


@dataclass(frozen=True)
class EngineeringWorkspaceStep:
    phase: str
    name: str
    purpose: str
    completion_condition: str


def build_engineering_workspace_integration_plan(project_root: str | Path = ".") -> dict[str, Any]:
    steps = [
        EngineeringWorkspaceStep(
            "22B",
            "Engineering Tool Registry",
            "Create the canonical registry for engineering tools such as Regen, Materials, Coatings, Graph Explorer, Reports and Exports.",
            "Every engineering tool has a stable id, label, owner, model source, panel adapter and activation state.",
        ),
        EngineeringWorkspaceStep(
            "22C",
            "Engineering Panel Contract",
            "Define the reusable contract that allows engineering modules to appear inside the workspace without leaking solver logic into Qt.",
            "Each panel exposes model, validation, report and action contracts before any widget binding.",
        ),
        EngineeringWorkspaceStep(
            "22D",
            "Design Session Manager",
            "Define ownership of active user designs, open sessions, dirty state, save state and selected engineering context.",
            "The workspace can identify the active design session without owning engineering calculations.",
        ),
        EngineeringWorkspaceStep(
            "22E",
            "Engineering Document Model",
            "Define how Designs, Projects, Reports and Exports become workspace documents.",
            "User-facing documents have canonical ids, paths, metadata and ownership boundaries.",
        ),
        EngineeringWorkspaceStep(
            "22F",
            "Report And Export Routing",
            "Route engineering reports and exports through shared workspace infrastructure.",
            "Reports and exports are discoverable from the workspace without duplicating report generation logic.",
        ),
        EngineeringWorkspaceStep(
            "22G",
            "Workspace Tool Activation Binding",
            "Bind registered engineering tools into the Programme 21 workspace shell.",
            "Tools can be activated from the workspace using registry and panel contracts only.",
        ),
        EngineeringWorkspaceStep(
            "22H",
            "Engineering Workspace Completion Gate",
            "Audit the full Programme 22 engineering workspace integration layer.",
            "Programme 22 is signed off with model-first architecture preserved.",
        ),
    ]

    return {
        "schema": SCHEMA,
        "phase": "22A",
        "feature": "ENGINEERING_WORKSPACE_INTEGRATION_PLANNING",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "objective": "Define how LEAF engineering modules plug into the completed Programme 21 workspace without moving engineering logic into Qt.",
        "architecture_rule": "Workspace hosts engineering tools; workspace never becomes engineering logic.",
        "canonical_flow": [
            "Engineering Model",
            "Engineering Controller",
            "Validation Owner",
            "Report Owner",
            "Workspace Adapter",
            "Qt Panel",
        ],
        "forbidden_flow": [
            "Qt Button",
            "Solver Logic",
        ],
        "programme_22_steps": [asdict(step) for step in steps],
        "required_contracts": {
            "engineering_tool_registry": {
                "required": True,
                "purpose": "Canonical list of engineering tools and their model/controller/report ownership.",
            },
            "panel_contract": {
                "required": True,
                "purpose": "Reusable adapter contract between engineering systems and workspace panels.",
            },
            "design_session_contract": {
                "required": True,
                "purpose": "Own active design/session state without hiding user data in internal folders.",
            },
            "report_export_contract": {
                "required": True,
                "purpose": "Route reports and exports through user-facing workspace resources.",
            },
            "activation_contract": {
                "required": True,
                "purpose": "Control when engineering tools are visible, enabled, disabled or blocked.",
            },
        },
        "non_negotiable_principles": {
            "foundations_first": True,
            "one_feature_at_a_time": True,
            "model_first": True,
            "qt_presentation_only": True,
            "replacement_over_accumulation": True,
            "reuse_existing_infrastructure": True,
            "developer_user_architecture_separation": True,
            "user_resources_easy_to_find": True,
            "canonical_user_storage": "LEAF_Designs",
        },
        "safety_boundaries": {
            "qt_owns_solver_logic": False,
            "qt_owns_validation_logic": False,
            "qt_owns_report_logic": False,
            "qt_owns_sorting_logic": False,
            "automatic_sorting_activation": False,
            "filesystem_mutation": False,
            "engineering_calculation_execution": False,
        },
        "completion_criteria": {
            "programme_22_roadmap_defined": True,
            "contracts_defined": True,
            "unsafe_execution_blocked": True,
            "model_first_architecture_preserved": True,
            "ready_for_22b_engineering_tool_registry": True,
        },
    }


def write_engineering_workspace_integration_plan(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_22a"
    out_dir.mkdir(parents=True, exist_ok=True)

    plan = build_engineering_workspace_integration_plan(root)

    json_path = out_dir / "engineering_workspace_integration_plan_phase_22a.json"
    txt_path = out_dir / "engineering_workspace_integration_plan_phase_22a.txt"

    json_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    txt_path.write_text("\n".join([
        "LEAF PHASE 22A ENGINEERING WORKSPACE INTEGRATION PLAN",
        "====================================================",
        f"schema={plan['schema']}",
        f"phase={plan['phase']}",
        f"feature={plan['feature']}",
        f"objective={plan['objective']}",
        f"architecture_rule={plan['architecture_rule']}",
        "",
        "Programme 22 Steps:",
        *[
            f"{step['phase']} — {step['name']} — {step['purpose']}"
            for step in plan["programme_22_steps"]
        ],
        "",
        "Safety Boundaries:",
        *[
            f"{key}={value}"
            for key, value in plan["safety_boundaries"].items()
        ],
        "",
        "Completion Criteria:",
        *[
            f"{key}={value}"
            for key, value in plan["completion_criteria"].items()
        ],
    ]), encoding="utf-8")

    return {
        "plan": plan,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_engineering_workspace_integration_plan(Path.cwd())
    print("PASS_PHASE_22A_ENGINEERING_WORKSPACE_INTEGRATION_PLAN_WRITTEN")
    print(f"schema={result['plan']['schema']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
