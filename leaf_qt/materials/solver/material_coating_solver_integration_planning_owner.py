"""
LEAF Material / Coating Solver Integration Planning Owner
========================================================

PHASE 10A

This owner plans the transition from completed material/coating foundations
into actual regen solver integration.

Important:
- This phase does NOT alter solver behaviour.
- This phase does NOT apply material properties automatically.
- This phase does NOT mark solver integration complete.
- This phase only audits and maps integration requirements.

Conservative rule:
- Placeholder data must never be treated as solver-ready.
- PARTIAL_SOURCE_MODE must never be treated as final solver-ready.
- Only SOURCED_VALIDATION_MODE may be treated as solver-ready.
"""


PHASE_10A_REQUIRED_PATHS = {
    "material_thermal_conductivity": {
        "category": "material",
        "future_phase": "10B",
        "required_action": "Integrate sourced/interpolated material k(T) into regen wall heat-transfer calculations.",
    },
    "material_specific_heat": {
        "category": "material",
        "future_phase": "10B",
        "required_action": "Integrate sourced/interpolated material Cp(T) into thermal capacity and thermal inertia calculations.",
    },
    "material_density": {
        "category": "material",
        "future_phase": "10B",
        "required_action": "Integrate sourced/interpolated material rho(T) into mass, inertia, and manufacturing estimates.",
    },
    "material_temperature_limit": {
        "category": "material",
        "future_phase": "10B",
        "required_action": "Connect sourced material temperature limits to regen wall validation gates.",
    },
    "material_yield_or_strength_limit": {
        "category": "material",
        "future_phase": "10B",
        "required_action": "Connect sourced yield/strength limits to structural margin checks.",
    },
    "coating_thermal_conductivity": {
        "category": "coating",
        "future_phase": "10C",
        "required_action": "Integrate sourced coating conductivity into coating thermal resistance.",
    },
    "coating_thickness": {
        "category": "coating",
        "future_phase": "10C",
        "required_action": "Integrate coating thickness into the regen hot-wall thermal resistance chain.",
    },
    "coating_thermal_resistance": {
        "category": "coating",
        "future_phase": "10C",
        "required_action": "Calculate and apply coating thermal resistance before wall-temperature validation.",
    },
    "coating_temperature_limit": {
        "category": "coating",
        "future_phase": "10C",
        "required_action": "Connect sourced coating temperature limits to coating validation gates.",
    },
}


def attach_material_coating_solver_integration_planning_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_material_coating_solver_integration_plan(results)
    results.update(audit)
    return results


def build_material_coating_solver_integration_plan(results):
    results = results if isinstance(results, dict) else {}

    material_mode = str(
        results.get("material_source_validation_mode", "UNKNOWN")
    ).upper()

    coating_mode = str(
        results.get("coating_source_validation_mode", "UNKNOWN")
    ).upper()

    material_placeholder = bool(
        results.get("material_source_is_placeholder", False)
    )

    coating_placeholder = bool(
        results.get("coating_source_is_placeholder", False)
    )

    material_foundation_complete = bool(
        results.get("stage_9_material_foundation_complete", False)
        or results.get("phase_9e_material_completion_audit_complete", False)
    )

    material_and_coating_foundation_complete = bool(
        results.get("stage_9_material_and_coating_foundation_complete", False)
        or results.get("phase_9h_material_and_coating_foundation_audit_complete", False)
    )

    findings = []
    blockers = []
    phase_10b_actions = []
    phase_10c_actions = []

    for key, spec in PHASE_10A_REQUIRED_PATHS.items():
        category = spec["category"]
        future_phase = spec["future_phase"]

        if category == "material":
            readiness = _classify_material_solver_readiness(
                material_mode=material_mode,
                material_placeholder=material_placeholder,
                material_foundation_complete=material_foundation_complete,
            )
        else:
            readiness = _classify_coating_solver_readiness(
                coating_mode=coating_mode,
                coating_placeholder=coating_placeholder,
                material_and_coating_foundation_complete=material_and_coating_foundation_complete,
            )

        finding = {
            "path": key,
            "category": category,
            "readiness": readiness,
            "future_phase": future_phase,
            "required_action": spec["required_action"],
        }

        findings.append(finding)

        if future_phase == "10B":
            phase_10b_actions.append(spec["required_action"])

        if future_phase == "10C":
            phase_10c_actions.append(spec["required_action"])

        if readiness in (
            "BLOCKED_PLACEHOLDER",
            "BLOCKED_PARTIAL_SOURCE",
            "BLOCKED_FOUNDATION_INCOMPLETE",
        ):
            blockers.append(
                f"{key}: {readiness}"
            )

    complete = len(findings) == len(PHASE_10A_REQUIRED_PATHS)

    status = (
        "PASS_PHASE_10A_SOLVER_INTEGRATION_PLANNING_OWNER"
        if complete
        else "FAIL_PHASE_10A_SOLVER_INTEGRATION_PLANNING_OWNER"
    )

    text = build_phase_10a_solver_integration_planning_text(
        status=status,
        complete=complete,
        material_mode=material_mode,
        coating_mode=coating_mode,
        material_placeholder=material_placeholder,
        coating_placeholder=coating_placeholder,
        material_foundation_complete=material_foundation_complete,
        material_and_coating_foundation_complete=material_and_coating_foundation_complete,
        findings=findings,
        blockers=blockers,
        phase_10b_actions=phase_10b_actions,
        phase_10c_actions=phase_10c_actions,
    )

    return {
        "phase_10a_solver_integration_planning_owner_complete": complete,
        "phase_10a_solver_integration_planning_owner_status": status,
        "phase_10a_solver_integration_planning_owner_text": text,
        "phase_10a_solver_integration_planning_owner_findings": findings,
        "phase_10a_solver_integration_planning_owner_blockers": blockers,
        "phase_10a_material_integration_actions": phase_10b_actions,
        "phase_10a_coating_integration_actions": phase_10c_actions,
        "stage_10_solver_integration_planning_started": True,
        "stage_10_solver_integration_planning_complete": complete,
        "stage_10_solver_integration_status": "PLANNING_ONLY_NO_SOLVER_CHANGE",
    }


def _classify_material_solver_readiness(
        material_mode,
        material_placeholder,
        material_foundation_complete,
):
    if material_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if not material_foundation_complete:
        return "BLOCKED_FOUNDATION_INCOMPLETE"

    if material_mode == "SOURCED_VALIDATION_MODE":
        return "READY_FOR_PHASE_10B_MAPPING"

    return "REVIEW_REQUIRED"


def _classify_coating_solver_readiness(
        coating_mode,
        coating_placeholder,
        material_and_coating_foundation_complete,
):
    if coating_mode in ("NONE", "NO_COATING", ""):
        return "NO_COATING_SELECTED"

    if coating_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if coating_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if coating_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if not material_and_coating_foundation_complete:
        return "BLOCKED_FOUNDATION_INCOMPLETE"

    if coating_mode == "SOURCED_VALIDATION_MODE":
        return "READY_FOR_PHASE_10C_MAPPING"

    return "REVIEW_REQUIRED"


def build_phase_10a_solver_integration_planning_text(
        status,
        complete,
        material_mode,
        coating_mode,
        material_placeholder,
        coating_placeholder,
        material_foundation_complete,
        material_and_coating_foundation_complete,
        findings,
        blockers,
        phase_10b_actions,
        phase_10c_actions,
):
    lines = []

    lines.append("PHASE 10A — MATERIAL / COATING SOLVER INTEGRATION PLANNING OWNER")
    lines.append("================================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Planning and audit only.")
    lines.append("- No regen solver behaviour is changed in Phase 10A.")
    lines.append("- No sourced values are applied automatically in Phase 10A.")
    lines.append("")
    lines.append("Foundation Inputs:")
    lines.append(f"- Material validation mode: {material_mode}")
    lines.append(f"- Material placeholder: {material_placeholder}")
    lines.append(f"- Material foundation complete: {material_foundation_complete}")
    lines.append(f"- Coating validation mode: {coating_mode}")
    lines.append(f"- Coating placeholder: {coating_placeholder}")
    lines.append(
        f"- Material/coating foundation complete: {material_and_coating_foundation_complete}"
    )
    lines.append("")

    lines.append("Mapped Solver Integration Paths:")
    for finding in findings:
        lines.append(
            f"- {finding['path']} | "
            f"{finding['category']} | "
            f"{finding['readiness']} | "
            f"{finding['future_phase']}"
        )
        lines.append(f"  Action: {finding['required_action']}")

    lines.append("")

    if blockers:
        lines.append("Conservative Blockers:")
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("Conservative Blockers:")
        lines.append("- None at planning level.")

    lines.append("")
    lines.append("Phase 10B Material Integration Actions:")
    for action in phase_10b_actions:
        lines.append(f"- {action}")

    lines.append("")
    lines.append("Phase 10C Coating Integration Actions:")
    for action in phase_10c_actions:
        lines.append(f"- {action}")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "Phase 10A has mapped the required solver integration routes. "
        "Actual solver integration begins in Phase 10B."
    )

    return "\n".join(lines)