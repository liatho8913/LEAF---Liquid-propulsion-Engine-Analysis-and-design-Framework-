
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u58_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u58_is_fail_like(text) or _leaf_16u58_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u58_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u58_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u58_is_fail_like(value):
    return _leaf_16u58_status_severity(value) == "FAIL"


def _leaf_16u58_is_warn_like(value):
    return _leaf_16u58_status_severity(value) == "WARN"


def _leaf_16u58_is_pass_like(value):
    return _leaf_16u58_status_severity(value) == "PASS"


"""
PHASE 10B.6
Material Yield / Strength Limit Integration Owner

Purpose:
    Integrate sourced material yield/strength limits into structural
    survivability validation.

Conservative rules:
    - PLACEHOLDER_MODE must not produce structural PASS.
    - PARTIAL_SOURCE_MODE must not produce structural PASS.
    - Only SOURCED_VALIDATION_MODE may create authoritative structural PASS.
"""


def attach_material_strength_limit_integration_owner(results):
    if not isinstance(results, dict):
        return results

    audit = apply_material_strength_limit_integration(results)
    results.update(audit)
    return results


def apply_material_strength_limit_integration(results):
    results = results if isinstance(results, dict) else {}

    phase_10b5_complete = bool(
        results.get("phase_10b5_material_temperature_limit_integration_owner_complete", False)
    )

    material_mode = str(
        results.get("material_source_validation_mode") or "UNKNOWN"
    ).upper()

    material_placeholder = bool(results.get("material_source_is_placeholder", False))

    sourced_strength = _find_strength_limit(results)

    previous_strength = _safe_float(
        results.get("material_yield_strength")
        or results.get("effective_material_yield_strength")
        or results.get("material_strength_limit")
    )

    wall_stress = _find_wall_stress(results)

    wall_safety_factor = _safe_float(results.get("wall_safety_factor")) or 2.0
    wall_joint_efficiency = _safe_float(results.get("wall_joint_efficiency")) or 1.0

    decision = _classify_strength_limit_decision(
        phase_10b5_complete=phase_10b5_complete,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        sourced_strength=sourced_strength,
    )

    applied = decision == "APPLIED_SOURCED_STRENGTH_LIMIT"

    if applied:
        results["material_yield_strength"] = sourced_strength
        results["effective_material_yield_strength"] = sourced_strength
        results["material_strength_limit_source"] = "SOURCED_MATERIAL_STRENGTH_LIMIT"
    else:
        results["effective_material_yield_strength"] = previous_strength
        results["material_strength_limit_source"] = "UNCHANGED_STATIC_OR_FALLBACK"

    final_strength = _safe_float(results.get("effective_material_yield_strength"))

    allowable_stress = None
    structural_margin = None
    structural_pass = None

    if final_strength is not None:
        allowable_stress = (
            final_strength * wall_joint_efficiency / wall_safety_factor
            if wall_safety_factor > 0
            else None
        )

    if allowable_stress is not None and wall_stress is not None:
        structural_margin = allowable_stress - wall_stress
        structural_pass = 1.0 if structural_margin >= 0 else 0.0

    if not applied and _leaf_16u58_is_fail_like(decision):
        structural_pass = 0.0

    results["material_allowable_wall_stress"] = allowable_stress
    results["material_structural_margin"] = structural_margin
    results["material_structural_pass"] = structural_pass

    complete = phase_10b5_complete

    status = (
        "PASS_PHASE_10B6_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER"
        if complete
        else "FAIL_PHASE_10B6_MATERIAL_STRENGTH_LIMIT_INTEGRATION_OWNER"
    )

    blockers = []
    if _leaf_16u58_is_fail_like(decision):
        blockers.append(decision)

    text = build_material_strength_limit_integration_text(
        status=status,
        complete=complete,
        decision=decision,
        applied=applied,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        previous_strength=previous_strength,
        sourced_strength=sourced_strength,
        final_strength=final_strength,
        wall_stress=wall_stress,
        allowable_stress=allowable_stress,
        structural_margin=structural_margin,
        structural_pass=structural_pass,
        wall_safety_factor=wall_safety_factor,
        wall_joint_efficiency=wall_joint_efficiency,
        blockers=blockers,
    )

    return {
        "phase_10b6_material_strength_limit_integration_owner_complete": complete,
        "phase_10b6_material_strength_limit_integration_owner_status": status,
        "phase_10b6_material_strength_limit_integration_owner_text": text,
        "phase_10b6_material_strength_limit_integration_owner_decision": decision,
        "phase_10b6_material_strength_limit_integration_owner_applied": applied,
        "phase_10b6_material_strength_limit_integration_owner_blockers": blockers,
        "phase_10b6_previous_material_strength_limit": previous_strength,
        "phase_10b6_sourced_material_strength_limit": sourced_strength,
        "phase_10b6_final_material_strength_limit": final_strength,
        "phase_10b6_wall_stress_checked": wall_stress,
        "phase_10b6_allowable_wall_stress": allowable_stress,
        "phase_10b6_material_structural_margin": structural_margin,
        "phase_10b6_material_structural_pass": structural_pass,
        "stage_10b_material_strength_limit_integration_complete": complete,
        "stage_10b_material_strength_limit_integration_status": decision,
    }


def _find_strength_limit(results):
    direct_candidates = (
        "sourced_material_yield_strength",
        "material_sourced_yield_strength",
        "material_yield_strength_sourced",
        "sourced_material_strength_limit",
        "material_strength_limit_sourced",
    )

    for key in direct_candidates:
        value = _safe_float(results.get(key))
        if value is not None and value > 0:
            return value

    interpolation_results = results.get("material_property_interpolation_results", {})
    if not isinstance(interpolation_results, dict):
        interpolation_results = {}

    possible_entries = (
        "yield_strength",
        "yield_strength_pa",
        "material_yield_strength",
        "strength_limit",
        "ultimate_strength",
    )

    for key in possible_entries:
        entry = interpolation_results.get(key)

        if isinstance(entry, dict):
            value = _safe_float(entry.get("value"))
        else:
            value = _safe_float(entry)

        if value is not None and value > 0:
            return value

    return None


def _find_wall_stress(results):
    candidates = (
        "hot_gas_wall_stress",
        "wall_stress",
        "pressure_wall_stress",
        "material_wall_stress",
        "regen_wall_stress",
    )

    for key in candidates:
        value = _safe_float(results.get(key))
        if value is not None:
            return value

    pressure = _safe_float(
        results.get("static_pressure")
        or results.get("chamber_pressure")
    )

    radius = _safe_float(
        results.get("throat_radius")
        or results.get("local_wall_radius")
    )

    thickness = _safe_float(
        results.get("hot_gas_wall_thickness")
        or results.get("minimum_wall_thickness")
    )

    if (
        pressure is not None
        and radius is not None
        and thickness is not None
        and thickness > 0
    ):
        return pressure * radius / thickness

    return None


def _classify_strength_limit_decision(
        phase_10b5_complete,
        material_mode,
        material_placeholder,
        sourced_strength,
):
    if not phase_10b5_complete:
        return "BLOCKED_PHASE_10B5_INCOMPLETE"

    if material_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if material_mode != "SOURCED_VALIDATION_MODE":
        return "BLOCKED_UNSOURCED_MODE"

    if sourced_strength is None:
        return "BLOCKED_MISSING_SOURCED_STRENGTH_LIMIT"

    if sourced_strength <= 0:
        return "BLOCKED_INVALID_SOURCED_STRENGTH_LIMIT"

    return "APPLIED_SOURCED_STRENGTH_LIMIT"


def build_material_strength_limit_integration_text(
        status,
        complete,
        decision,
        applied,
        material_mode,
        material_placeholder,
        previous_strength,
        sourced_strength,
        final_strength,
        wall_stress,
        allowable_stress,
        structural_margin,
        structural_pass,
        wall_safety_factor,
        wall_joint_efficiency,
        blockers,
):
    lines = []

    lines.append("PHASE 10B.6 — MATERIAL YIELD / STRENGTH LIMIT INTEGRATION OWNER")
    lines.append("================================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Integrates sourced material yield/strength limits.")
    lines.append("- Calculates allowable wall stress.")
    lines.append("- Creates structural margin and pass/fail ownership.")
    lines.append("- Blocks placeholder and partial-source authority.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Material validation mode: {material_mode}")
    lines.append(f"- Material placeholder: {material_placeholder}")
    lines.append(f"- Previous material strength limit: {previous_strength}")
    lines.append(f"- Sourced material strength limit: {sourced_strength}")
    lines.append(f"- Wall stress checked: {wall_stress}")
    lines.append(f"- Wall safety factor: {wall_safety_factor}")
    lines.append(f"- Wall joint efficiency: {wall_joint_efficiency}")
    lines.append("")
    lines.append("Decision:")
    lines.append(f"- Integration decision: {decision}")
    lines.append(f"- Applied to solver pathway: {applied}")
    lines.append(f"- Final effective material strength limit: {final_strength}")
    lines.append(f"- Allowable wall stress: {allowable_stress}")
    lines.append(f"- Structural margin: {structural_margin}")
    lines.append(f"- Structural pass flag: {structural_pass}")
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
        lines.append("Sourced material strength limit is now the active structural survivability limit.")
    else:
        lines.append("Sourced material strength limit was not applied because conservative gating blocked it.")

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None
