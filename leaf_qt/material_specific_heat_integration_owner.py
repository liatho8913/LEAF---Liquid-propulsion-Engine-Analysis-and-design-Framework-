
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
PHASE 10B.3
Material Specific Heat Cp(T) Integration Owner

Purpose:
    Integrate sourced/interpolated material Cp(T) into the material property
    solver pathway.

This phase does not yet implement full transient thermal inertia.
It creates the owned, validated Cp(T) solver pathway required before that.
"""


def attach_material_specific_heat_integration_owner(results):
    if not isinstance(results, dict):
        return results

    audit = apply_material_specific_heat_integration(results)
    results.update(audit)
    return results


def apply_material_specific_heat_integration(results):
    results = results if isinstance(results, dict) else {}

    phase_10b2_complete = bool(
        results.get("phase_10b2_material_thermal_conductivity_integration_owner_complete", False)
    )

    material_mode = str(
        results.get("material_source_validation_mode") or "UNKNOWN"
    ).upper()

    material_placeholder = bool(results.get("material_source_is_placeholder", False))

    interpolation_results = results.get("material_property_interpolation_results", {})
    if not isinstance(interpolation_results, dict):
        interpolation_results = {}

    cp_entry = (
        interpolation_results.get("specific_heat")
        or interpolation_results.get("specific_heat_cp")
        or interpolation_results.get("cp")
        or {}
    )

    if not isinstance(cp_entry, dict):
        cp_entry = {}

    sourced_cp = _safe_float(cp_entry.get("value"))
    previous_cp = _safe_float(results.get("material_specific_heat_cp"))

    decision = _classify_cp_integration_decision(
        phase_10b2_complete=phase_10b2_complete,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        sourced_cp=sourced_cp,
    )

    applied = decision == "APPLIED_SOURCED_CP"

    if applied:
        results["material_specific_heat_cp"] = sourced_cp
        results["sourced_material_specific_heat_cp"] = sourced_cp
        results["material_specific_heat_cp_source"] = "SOURCED_INTERPOLATED_MATERIAL_CP_T"
    else:
        results["sourced_material_specific_heat_cp"] = sourced_cp
        results["material_specific_heat_cp_source"] = "UNCHANGED_STATIC_OR_FALLBACK"

    complete = phase_10b2_complete

    status = (
        "PASS_PHASE_10B3_MATERIAL_SPECIFIC_HEAT_INTEGRATION_OWNER"
        if complete
        else "FAIL_PHASE_10B3_MATERIAL_SPECIFIC_HEAT_INTEGRATION_OWNER"
    )

    blockers = []
    if _leaf_16u62_is_fail_like(decision):
        blockers.append(decision)

    text = build_material_specific_heat_integration_text(
        status=status,
        complete=complete,
        decision=decision,
        applied=applied,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        previous_cp=previous_cp,
        sourced_cp=sourced_cp,
        final_cp=_safe_float(results.get("material_specific_heat_cp")),
        blockers=blockers,
    )

    return {
        "phase_10b3_material_specific_heat_integration_owner_complete": complete,
        "phase_10b3_material_specific_heat_integration_owner_status": status,
        "phase_10b3_material_specific_heat_integration_owner_text": text,
        "phase_10b3_material_specific_heat_integration_owner_decision": decision,
        "phase_10b3_material_specific_heat_integration_owner_applied": applied,
        "phase_10b3_material_specific_heat_integration_owner_blockers": blockers,
        "phase_10b3_previous_material_specific_heat_cp": previous_cp,
        "phase_10b3_sourced_material_specific_heat_cp": sourced_cp,
        "phase_10b3_final_material_specific_heat_cp": _safe_float(
            results.get("material_specific_heat_cp")
        ),
        "stage_10b_material_specific_heat_integration_complete": complete,
        "stage_10b_material_specific_heat_integration_status": decision,
    }


def _classify_cp_integration_decision(
        phase_10b2_complete,
        material_mode,
        material_placeholder,
        sourced_cp,
):
    if not phase_10b2_complete:
        return "BLOCKED_PHASE_10B2_INCOMPLETE"

    if material_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if material_mode != "SOURCED_VALIDATION_MODE":
        return "BLOCKED_UNSOURCED_MODE"

    if sourced_cp is None:
        return "BLOCKED_MISSING_SOURCED_CP"

    if sourced_cp <= 0:
        return "BLOCKED_INVALID_SOURCED_CP"

    return "APPLIED_SOURCED_CP"


def build_material_specific_heat_integration_text(
        status,
        complete,
        decision,
        applied,
        material_mode,
        material_placeholder,
        previous_cp,
        sourced_cp,
        final_cp,
        blockers,
):
    lines = []

    lines.append("PHASE 10B.3 — MATERIAL SPECIFIC HEAT Cp(T) INTEGRATION OWNER")
    lines.append("============================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Integrates sourced/interpolated material Cp(T).")
    lines.append("- Does not yet implement full transient thermal inertia.")
    lines.append("- Does not allow placeholder or partial-source values to override solver values.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Material validation mode: {material_mode}")
    lines.append(f"- Material placeholder: {material_placeholder}")
    lines.append(f"- Previous material_specific_heat_cp: {previous_cp}")
    lines.append(f"- Sourced/interpolated Cp(T): {sourced_cp}")
    lines.append("")
    lines.append("Decision:")
    lines.append(f"- Integration decision: {decision}")
    lines.append(f"- Applied to solver pathway: {applied}")
    lines.append(f"- Final material_specific_heat_cp: {final_cp}")
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
        lines.append("Sourced material Cp(T) has been applied to the owned material Cp pathway.")
    else:
        lines.append("Sourced material Cp(T) was not applied because conservative gating blocked it.")

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None
