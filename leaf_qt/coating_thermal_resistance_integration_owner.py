
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
PHASE 10C.4
Coating Thermal Resistance Integration Owner

Purpose:
    Calculate owned coating thermal resistance from:

        R_coating = t_coating / k_coating

This phase does NOT yet alter wall temperature, heat flux, or regen thermal
marching. It only creates the owned coating resistance pathway.
"""


def attach_coating_thermal_resistance_integration_owner(results):
    if not isinstance(results, dict):
        return results

    audit = apply_coating_thermal_resistance_integration(results)
    results.update(audit)
    return results


def apply_coating_thermal_resistance_integration(results):
    results = results if isinstance(results, dict) else {}

    phase_10c3_complete = bool(
        results.get("phase_10c3_coating_thickness_integration_owner_complete", False)
    )

    coating_selected = _coating_is_selected(results)

    coating_mode = str(
        results.get("coating_source_validation_mode")
        or results.get("coating_validation_mode")
        or "UNKNOWN"
    ).upper()

    coating_placeholder = bool(results.get("coating_source_is_placeholder", False))

    coating_k = _safe_float(results.get("coating_thermal_conductivity"))
    coating_t = _safe_float(results.get("effective_coating_thickness"))

    previous_r = _safe_float(
        results.get("coating_thermal_resistance")
        or results.get("effective_coating_thermal_resistance")
    )

    decision = _classify_coating_resistance_decision(
        phase_10c3_complete=phase_10c3_complete,
        coating_selected=coating_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        coating_k=coating_k,
        coating_t=coating_t,
    )

    applied = decision == "APPLIED_COATING_THERMAL_RESISTANCE"

    coating_r = None
    if applied:
        coating_r = coating_t / coating_k
        results["coating_thermal_resistance"] = coating_r
        results["effective_coating_thermal_resistance"] = coating_r
        results["sourced_coating_thermal_resistance"] = coating_r
        results["coating_thermal_resistance_source"] = (
            "CALCULATED_FROM_OWNED_COATING_THICKNESS_AND_CONDUCTIVITY"
        )
    else:
        coating_r = previous_r
        results["effective_coating_thermal_resistance"] = previous_r
        results["sourced_coating_thermal_resistance"] = previous_r
        results["coating_thermal_resistance_source"] = "UNCHANGED_STATIC_OR_FALLBACK"

    complete = phase_10c3_complete

    status = (
        "PASS_PHASE_10C4_COATING_THERMAL_RESISTANCE_INTEGRATION_OWNER"
        if complete
        else "FAIL_PHASE_10C4_COATING_THERMAL_RESISTANCE_INTEGRATION_OWNER"
    )

    blockers = []
    if _leaf_16u62_is_fail_like(decision):
        blockers.append(decision)

    text = build_coating_thermal_resistance_integration_text(
        status=status,
        complete=complete,
        decision=decision,
        applied=applied,
        coating_selected=coating_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        coating_k=coating_k,
        coating_t=coating_t,
        previous_r=previous_r,
        final_r=_safe_float(results.get("effective_coating_thermal_resistance")),
        blockers=blockers,
    )

    return {
        "phase_10c4_coating_thermal_resistance_integration_owner_complete": complete,
        "phase_10c4_coating_thermal_resistance_integration_owner_status": status,
        "phase_10c4_coating_thermal_resistance_integration_owner_text": text,
        "phase_10c4_coating_thermal_resistance_integration_owner_decision": decision,
        "phase_10c4_coating_thermal_resistance_integration_owner_applied": applied,
        "phase_10c4_coating_thermal_resistance_integration_owner_blockers": blockers,
        "phase_10c4_coating_thermal_conductivity_used": coating_k,
        "phase_10c4_coating_thickness_used": coating_t,
        "phase_10c4_previous_coating_thermal_resistance": previous_r,
        "phase_10c4_final_coating_thermal_resistance": _safe_float(
            results.get("effective_coating_thermal_resistance")
        ),
        "stage_10c_coating_thermal_resistance_integration_complete": complete,
        "stage_10c_coating_thermal_resistance_integration_status": decision,
    }


def _classify_coating_resistance_decision(
        phase_10c3_complete,
        coating_selected,
        coating_mode,
        coating_placeholder,
        coating_k,
        coating_t,
):
    if not phase_10c3_complete:
        return "BLOCKED_PHASE_10C3_INCOMPLETE"

    if not coating_selected:
        return "NO_COATING_SELECTED"

    if coating_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if coating_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if coating_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if coating_mode != "SOURCED_VALIDATION_MODE":
        return "BLOCKED_UNSOURCED_MODE"

    if coating_k is None:
        return "BLOCKED_MISSING_COATING_THERMAL_CONDUCTIVITY"

    if coating_k <= 0:
        return "BLOCKED_INVALID_COATING_THERMAL_CONDUCTIVITY"

    if coating_t is None:
        return "BLOCKED_MISSING_COATING_THICKNESS"

    if coating_t <= 0:
        return "BLOCKED_INVALID_COATING_THICKNESS"

    return "APPLIED_COATING_THERMAL_RESISTANCE"


def _coating_is_selected(results):
    coating_name = str(
        results.get("selected_coating_material")
        or results.get("coating_material")
        or results.get("coating_name")
        or ""
    ).strip().upper()

    thickness = _safe_float(
        results.get("effective_coating_thickness")
        or results.get("coating_thickness")
    )

    if coating_name in ("", "NONE", "NO_COATING", "N/A"):
        return False

    if thickness is not None and thickness > 0:
        return True

    return bool(coating_name)


def build_coating_thermal_resistance_integration_text(
        status,
        complete,
        decision,
        applied,
        coating_selected,
        coating_mode,
        coating_placeholder,
        coating_k,
        coating_t,
        previous_r,
        final_r,
        blockers,
):
    lines = []

    lines.append("PHASE 10C.4 — COATING THERMAL RESISTANCE INTEGRATION OWNER")
    lines.append("==========================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Calculates owned coating thermal resistance.")
    lines.append("- Uses R_coating = t_coating / k_coating.")
    lines.append("- Does not yet alter wall temperature, heat flux, or regen thermal marching.")
    lines.append("- Blocks placeholder and partial-source authority.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Coating selected: {coating_selected}")
    lines.append(f"- Coating validation mode: {coating_mode}")
    lines.append(f"- Coating placeholder: {coating_placeholder}")
    lines.append(f"- Coating thermal conductivity used: {coating_k}")
    lines.append(f"- Coating thickness used: {coating_t}")
    lines.append(f"- Previous coating thermal resistance: {previous_r}")
    lines.append("")
    lines.append("Decision:")
    lines.append(f"- Integration decision: {decision}")
    lines.append(f"- Applied to coating resistance pathway: {applied}")
    lines.append(f"- Final effective_coating_thermal_resistance: {final_r}")
    lines.append("")

    if blockers:
        lines.append("Conservative Blockers:")
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("Conservative Blockers:")
        lines.append("- None.")

    lines.append("")
    lines.append("Conclusion:")
    if applied:
        lines.append("Coating thermal resistance is now available as an owned solver quantity.")
    elif decision == "NO_COATING_SELECTED":
        lines.append("No coating is selected, so coating thermal resistance integration is inactive.")
    else:
        lines.append("Coating thermal resistance was not applied because conservative gating blocked it.")

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None
