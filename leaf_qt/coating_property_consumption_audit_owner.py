
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
PHASE 10C.1
Coating Property Consumption Audit Owner

Purpose:
    Audit how coating properties are currently consumed before coating solver
    integration begins.

This file does NOT change solver behaviour.
"""

REQUIRED_COATING_CONSUMPTION_PATHS = {
    "coating_thermal_conductivity": {
        "symbol": "k_coating(T)",
        "future_phase": "10C.2",
        "required_action": "Integrate sourced coating conductivity into coating thermal resistance.",
    },
    "coating_thickness": {
        "symbol": "t_coating",
        "future_phase": "10C.3",
        "required_action": "Integrate coating thickness into the hot-wall thermal resistance chain.",
    },
    "coating_thermal_resistance": {
        "symbol": "R_coating",
        "future_phase": "10C.4",
        "required_action": "Calculate coating thermal resistance from thickness and conductivity.",
    },
    "coating_temperature_limit": {
        "symbol": "T_coating_limit",
        "future_phase": "10C.5",
        "required_action": "Connect sourced coating temperature limit to coating validation gates.",
    },
    "bond_coat_pathway": {
        "symbol": "bond_coat",
        "future_phase": "10C.6",
        "required_action": "Audit and integrate bond coat pathway where selected.",
    },
}


def attach_coating_property_consumption_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_coating_property_consumption_audit(results)
    results.update(audit)
    return results


def build_coating_property_consumption_audit(results):
    results = results if isinstance(results, dict) else {}

    phase_10b_complete = bool(
        results.get("phase_10b8_material_integration_completion_audit_complete", False)
    )

    coating_mode = str(
        results.get("coating_source_validation_mode")
        or results.get("coating_validation_mode")
        or "UNKNOWN"
    ).upper()

    coating_placeholder = bool(
        results.get("coating_source_is_placeholder", False)
    )

    coating_selected = _coating_is_selected(results)

    coating_foundation_complete = bool(
        results.get("phase_9h_material_and_coating_foundation_audit_complete", False)
        or results.get("stage_9_material_and_coating_foundation_complete", False)
    )

    findings = []
    blockers = []
    integration_actions = []

    for key, spec in REQUIRED_COATING_CONSUMPTION_PATHS.items():
        current_value = results.get(key, None)

        consumption_status = _classify_coating_consumption(
            current_value=current_value,
            phase_10b_complete=phase_10b_complete,
            coating_selected=coating_selected,
            coating_mode=coating_mode,
            coating_placeholder=coating_placeholder,
            coating_foundation_complete=coating_foundation_complete,
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
        phase_10b_complete
        and len(findings) == len(REQUIRED_COATING_CONSUMPTION_PATHS)
    )

    status = (
        "PASS_PHASE_10C1_COATING_PROPERTY_CONSUMPTION_AUDIT_OWNER"
        if complete
        else "FAIL_PHASE_10C1_COATING_PROPERTY_CONSUMPTION_AUDIT_OWNER"
    )

    text = build_coating_property_consumption_audit_text(
        status=status,
        complete=complete,
        phase_10b_complete=phase_10b_complete,
        coating_selected=coating_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        coating_foundation_complete=coating_foundation_complete,
        findings=findings,
        blockers=blockers,
        integration_actions=integration_actions,
    )

    return {
        "phase_10c1_coating_property_consumption_audit_owner_complete": complete,
        "phase_10c1_coating_property_consumption_audit_owner_status": status,
        "phase_10c1_coating_property_consumption_audit_owner_text": text,
        "phase_10c1_coating_property_consumption_audit_owner_findings": findings,
        "phase_10c1_coating_property_consumption_audit_owner_blockers": blockers,
        "phase_10c1_coating_property_consumption_audit_owner_actions": integration_actions,
        "stage_10c_coating_property_integration_started": True,
        "stage_10c_coating_property_consumption_audit_complete": complete,
        "stage_10c_coating_property_integration_status": "CONSUMPTION_AUDIT_ONLY_NO_SOLVER_CHANGE",
    }


def _coating_is_selected(results):
    coating_name = str(
        results.get("selected_coating_material")
        or results.get("coating_material")
        or results.get("coating_name")
        or ""
    ).strip().upper()

    if coating_name in ("", "NONE", "NO_COATING", "N/A"):
        return False

    thickness = _safe_float(results.get("coating_thickness"))

    if thickness is not None and thickness > 0:
        return True

    return bool(coating_name)


def _classify_coating_consumption(
        current_value,
        phase_10b_complete,
        coating_selected,
        coating_mode,
        coating_placeholder,
        coating_foundation_complete,
):
    if not phase_10b_complete:
        return "BLOCKED_PHASE_10B_INCOMPLETE"

    if not coating_foundation_complete:
        return "BLOCKED_COATING_FOUNDATION_INCOMPLETE"

    if not coating_selected:
        return "NO_COATING_SELECTED"

    if coating_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if coating_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if coating_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if coating_mode != "SOURCED_VALIDATION_MODE":
        return "REVIEW_REQUIRED"

    if current_value is None:
        return "MISSING_FROM_SOLVER_OUTPUTS"

    return "PRESENT_STATIC_OR_UNVERIFIED"


def build_coating_property_consumption_audit_text(
        status,
        complete,
        phase_10b_complete,
        coating_selected,
        coating_mode,
        coating_placeholder,
        coating_foundation_complete,
        findings,
        blockers,
        integration_actions,
):
    lines = []

    lines.append("PHASE 10C.1 — COATING PROPERTY CONSUMPTION AUDIT OWNER")
    lines.append("======================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Audit only.")
    lines.append("- No solver behaviour is changed.")
    lines.append("- No coating values are automatically applied.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Phase 10B material integration complete: {phase_10b_complete}")
    lines.append(f"- Coating selected: {coating_selected}")
    lines.append(f"- Coating validation mode: {coating_mode}")
    lines.append(f"- Coating placeholder: {coating_placeholder}")
    lines.append(f"- Coating foundation complete: {coating_foundation_complete}")
    lines.append("")
    lines.append("Coating Consumption Paths:")

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
        "Phase 10C.1 has mapped coating property consumption. "
        "Actual coating solver integration begins after this audit passes."
    )

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None
