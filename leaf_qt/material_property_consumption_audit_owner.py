
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u62_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u62_is_fail_like(text) or _leaf_16u62_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u62_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u62_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u62_is_fail_like(value):
    return _leaf_16u62_status_severity(value) == "FAIL"


def _leaf_16u62_is_warn_like(value):
    return _leaf_16u62_status_severity(value) == "WARN"


def _leaf_16u62_is_pass_like(value):
    return _leaf_16u62_status_severity(value) == "PASS"


"""
PHASE 10B.1
Material Property Consumption Audit Owner

Purpose:
    Audit how material properties are currently consumed before actual solver
    integration begins.

This file does NOT change solver behaviour.
"""

REQUIRED_MATERIAL_CONSUMPTION_PATHS = {
    "material_thermal_conductivity": {
        "symbol": "k(T)",
        "future_phase": "10B.2",
        "required_action": "Replace static wall conductivity with sourced/interpolated k(T).",
    },
    "material_specific_heat": {
        "symbol": "Cp(T)",
        "future_phase": "10B.3",
        "required_action": "Replace static material Cp with sourced/interpolated Cp(T).",
    },
    "material_density": {
        "symbol": "rho(T)",
        "future_phase": "10B.4",
        "required_action": "Replace static density with sourced/interpolated rho(T).",
    },
    "material_temperature_limit": {
        "symbol": "T_limit",
        "future_phase": "10B.5",
        "required_action": "Connect sourced material temperature limits to wall validation.",
    },
    "material_yield_or_strength_limit": {
        "symbol": "sigma_y(T)",
        "future_phase": "10B.6",
        "required_action": "Connect sourced yield/strength limits to structural margin checks.",
    },
}


def attach_material_property_consumption_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_material_property_consumption_audit(results)
    results.update(audit)
    return results


def build_material_property_consumption_audit(results):
    results = results if isinstance(results, dict) else {}

    material_mode = str(
        results.get("material_source_validation_mode", "UNKNOWN")
    ).upper()

    material_placeholder = bool(
        results.get("material_source_is_placeholder", False)
    )

    material_foundation_complete = bool(
        results.get("phase_9e_material_completion_audit_complete", False)
        or results.get("stage_9_material_foundation_complete", False)
    )

    phase_10a_complete = bool(
        results.get("phase_10a_solver_integration_planning_owner_complete", False)
    )

    findings = []
    blockers = []
    integration_actions = []

    for key, spec in REQUIRED_MATERIAL_CONSUMPTION_PATHS.items():
        current_value = results.get(key, None)

        consumption_status = _classify_material_consumption(
            current_value=current_value,
            material_mode=material_mode,
            material_placeholder=material_placeholder,
            material_foundation_complete=material_foundation_complete,
            phase_10a_complete=phase_10a_complete,
        )

        finding = {
            "path": key,
            "symbol": spec["symbol"],
            "consumption_status": consumption_status,
            "future_phase": spec["future_phase"],
            "required_action": spec["required_action"],
        }

        findings.append(finding)
        integration_actions.append(spec["required_action"])

        if _leaf_16u62_is_fail_like(consumption_status):
            blockers.append(f"{key}: {consumption_status}")

    complete = (
        phase_10a_complete
        and len(findings) == len(REQUIRED_MATERIAL_CONSUMPTION_PATHS)
    )

    status = (
        "PASS_PHASE_10B1_MATERIAL_PROPERTY_CONSUMPTION_AUDIT_OWNER"
        if complete
        else "FAIL_PHASE_10B1_MATERIAL_PROPERTY_CONSUMPTION_AUDIT_OWNER"
    )

    text = build_material_property_consumption_audit_text(
        status=status,
        complete=complete,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        material_foundation_complete=material_foundation_complete,
        phase_10a_complete=phase_10a_complete,
        findings=findings,
        blockers=blockers,
        integration_actions=integration_actions,
    )

    return {
        "phase_10b1_material_property_consumption_audit_owner_complete": complete,
        "phase_10b1_material_property_consumption_audit_owner_status": status,
        "phase_10b1_material_property_consumption_audit_owner_text": text,
        "phase_10b1_material_property_consumption_audit_owner_findings": findings,
        "phase_10b1_material_property_consumption_audit_owner_blockers": blockers,
        "phase_10b1_material_property_consumption_audit_owner_actions": integration_actions,
        "stage_10b_material_property_integration_started": True,
        "stage_10b_material_property_consumption_audit_complete": complete,
        "stage_10b_material_property_integration_status": "CONSUMPTION_AUDIT_ONLY_NO_SOLVER_CHANGE",
    }


def _classify_material_consumption(
        current_value,
        material_mode,
        material_placeholder,
        material_foundation_complete,
        phase_10a_complete,
):
    if not phase_10a_complete:
        return "BLOCKED_PHASE_10A_INCOMPLETE"

    if not material_foundation_complete:
        return "BLOCKED_MATERIAL_FOUNDATION_INCOMPLETE"

    if material_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if material_mode != "SOURCED_VALIDATION_MODE":
        return "REVIEW_REQUIRED"

    if current_value is None:
        return "MISSING_FROM_SOLVER_OUTPUTS"

    return "PRESENT_STATIC_OR_UNVERIFIED"


def build_material_property_consumption_audit_text(
        status,
        complete,
        material_mode,
        material_placeholder,
        material_foundation_complete,
        phase_10a_complete,
        findings,
        blockers,
        integration_actions,
):
    lines = []

    lines.append("PHASE 10B.1 — MATERIAL PROPERTY CONSUMPTION AUDIT OWNER")
    lines.append("======================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Audit only.")
    lines.append("- No solver behaviour is changed.")
    lines.append("- No material values are automatically applied.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Material validation mode: {material_mode}")
    lines.append(f"- Material placeholder: {material_placeholder}")
    lines.append(f"- Material foundation complete: {material_foundation_complete}")
    lines.append(f"- Phase 10A complete: {phase_10a_complete}")
    lines.append("")
    lines.append("Material Consumption Paths:")

    for finding in findings:
        lines.append(
            f"- {finding['path']} | "
            f"{finding['symbol']} | "
            f"{finding['consumption_status']} | "
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
        lines.append("- None at audit level.")

    lines.append("")
    lines.append("Required Integration Actions:")
    for action in integration_actions:
        lines.append(f"- {action}")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "Phase 10B.1 has mapped material property consumption. "
        "Actual material solver integration begins after this audit passes."
    )

    return "\n".join(lines)
