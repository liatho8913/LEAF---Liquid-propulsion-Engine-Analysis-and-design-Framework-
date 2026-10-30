
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
PHASE 10B.2
Material Thermal Conductivity k(T) Integration Owner

Purpose:
    Integrate sourced/interpolated material thermal conductivity into the regen
    wall conductivity pathway.

Conservative rules:
    - PLACEHOLDER_MODE must not override solver conductivity.
    - PARTIAL_SOURCE_MODE must not override solver conductivity.
    - Only SOURCED_VALIDATION_MODE may override wall_thermal_conductivity.
    - Integration must be auditable.
"""


def attach_material_thermal_conductivity_integration_owner(results):
    if not isinstance(results, dict):
        return results

    audit = apply_material_thermal_conductivity_integration(results)
    results.update(audit)
    return results


def apply_material_thermal_conductivity_integration(results):
    results = results if isinstance(results, dict) else {}

    phase_10b1_complete = bool(
        results.get("phase_10b1_material_property_consumption_audit_owner_complete", False)
    )

    material_mode = str(
        results.get("material_source_validation_mode") or "UNKNOWN"
    ).upper()

    material_placeholder = bool(
        results.get("material_source_is_placeholder", False)
    )

    interpolation_results = results.get("material_property_interpolation_results", {})
    if not isinstance(interpolation_results, dict):
        interpolation_results = {}

    conductivity_entry = interpolation_results.get("thermal_conductivity", {})
    if not isinstance(conductivity_entry, dict):
        conductivity_entry = {}

    sourced_k = _safe_float(conductivity_entry.get("value"))
    source_temperature = _safe_float(
        results.get("material_property_interpolation_query_temperature")
    )

    previous_k = _safe_float(results.get("wall_thermal_conductivity"))

    decision = _classify_k_integration_decision(
        phase_10b1_complete=phase_10b1_complete,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        sourced_k=sourced_k,
    )

    applied = decision == "APPLIED_SOURCED_KT"

    if applied:
        results["wall_thermal_conductivity"] = sourced_k
        results["material_thermal_conductivity"] = sourced_k
        results["sourced_wall_thermal_conductivity"] = sourced_k
        results["wall_thermal_conductivity_source"] = "SOURCED_INTERPOLATED_MATERIAL_KT"
    else:
        results["sourced_wall_thermal_conductivity"] = sourced_k
        results["wall_thermal_conductivity_source"] = "UNCHANGED_STATIC_OR_FALLBACK"

    complete = phase_10b1_complete

    status = (
        "PASS_PHASE_10B2_MATERIAL_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER"
        if complete
        else "FAIL_PHASE_10B2_MATERIAL_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER"
    )

    blockers = []
    if _leaf_16u62_is_fail_like(decision):
        blockers.append(decision)

    text = build_material_thermal_conductivity_integration_text(
        status=status,
        complete=complete,
        decision=decision,
        applied=applied,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        previous_k=previous_k,
        sourced_k=sourced_k,
        final_k=_safe_float(results.get("wall_thermal_conductivity")),
        source_temperature=source_temperature,
        blockers=blockers,
    )

    return {
        "phase_10b2_material_thermal_conductivity_integration_owner_complete": complete,
        "phase_10b2_material_thermal_conductivity_integration_owner_status": status,
        "phase_10b2_material_thermal_conductivity_integration_owner_text": text,
        "phase_10b2_material_thermal_conductivity_integration_owner_decision": decision,
        "phase_10b2_material_thermal_conductivity_integration_owner_applied": applied,
        "phase_10b2_material_thermal_conductivity_integration_owner_blockers": blockers,
        "phase_10b2_previous_wall_thermal_conductivity": previous_k,
        "phase_10b2_sourced_wall_thermal_conductivity": sourced_k,
        "phase_10b2_final_wall_thermal_conductivity": _safe_float(
            results.get("wall_thermal_conductivity")
        ),
        "phase_10b2_material_property_query_temperature": source_temperature,
        "stage_10b_material_thermal_conductivity_integration_complete": complete,
        "stage_10b_material_thermal_conductivity_integration_status": decision,
    }


def _classify_k_integration_decision(
        phase_10b1_complete,
        material_mode,
        material_placeholder,
        sourced_k,
):
    if not phase_10b1_complete:
        return "BLOCKED_PHASE_10B1_INCOMPLETE"

    if material_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if material_mode != "SOURCED_VALIDATION_MODE":
        return "BLOCKED_UNSOURCED_MODE"

    if sourced_k is None:
        return "BLOCKED_MISSING_SOURCED_KT"

    if sourced_k <= 0:
        return "BLOCKED_INVALID_SOURCED_KT"

    return "APPLIED_SOURCED_KT"


def build_material_thermal_conductivity_integration_text(
        status,
        complete,
        decision,
        applied,
        material_mode,
        material_placeholder,
        previous_k,
        sourced_k,
        final_k,
        source_temperature,
        blockers,
):
    lines = []

    lines.append("PHASE 10B.2 — MATERIAL THERMAL CONDUCTIVITY k(T) INTEGRATION OWNER")
    lines.append("===================================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Integrates sourced/interpolated material k(T) into wall_thermal_conductivity.")
    lines.append("- Does not integrate Cp(T), rho(T), temperature limits, or yield limits.")
    lines.append("- Does not allow placeholder or partial-source values to override solver values.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Material validation mode: {material_mode}")
    lines.append(f"- Material placeholder: {material_placeholder}")
    lines.append(f"- Previous wall_thermal_conductivity: {previous_k}")
    lines.append(f"- Sourced/interpolated k(T): {sourced_k}")
    lines.append(f"- Source temperature: {source_temperature}")
    lines.append("")
    lines.append("Decision:")
    lines.append(f"- Integration decision: {decision}")
    lines.append(f"- Applied to solver pathway: {applied}")
    lines.append(f"- Final wall_thermal_conductivity: {final_k}")
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
        lines.append(
            "Sourced material k(T) has been applied to the regen wall conductivity pathway."
        )
    else:
        lines.append(
            "Sourced material k(T) was not applied because conservative gating blocked it."
        )

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None
