import math

try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u66_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u66_is_fail_like(text) or _leaf_16u66_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u66_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u66_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u66_is_fail_like(value):
    return _leaf_16u66_status_severity(value) == "FAIL"


def _leaf_16u66_is_warn_like(value):
    return _leaf_16u66_status_severity(value) == "WARN"


def _leaf_16u66_is_pass_like(value):
    return _leaf_16u66_status_severity(value) == "PASS"


"""
PHASE 10B.5
Material Temperature Limit Integration Owner

Purpose:
    Integrate sourced material temperature limits into the material survivability
    validation pathway.

Conservative rules:
    - PLACEHOLDER_MODE must not produce final thermal PASS.
    - PARTIAL_SOURCE_MODE must not produce final thermal PASS.
    - Only SOURCED_VALIDATION_MODE may create authoritative material temperature PASS.
"""


def _evaluate_material_temperature_limit_margin(
    wall_temperature,
    material_temperature_limit,
):
    wall_temperature = _safe_float(
        wall_temperature
    )

    material_temperature_limit = _safe_float(
        material_temperature_limit
    )

    if (
        wall_temperature is None
        or material_temperature_limit is None
    ):
        return None, None

    margin = (
        material_temperature_limit
        -
        wall_temperature
    )

    pass_flag = (
        1.0
        if margin >= 0.0
        else 0.0
    )

    return margin, pass_flag


def build_material_temperature_limit_precheck(results):
    results = (
        results
        if isinstance(results, dict)
        else {}
    )

    wall_temperature = (
        _find_representative_wall_temperature(
            results
        )
    )

    material_temperature_limit = _safe_float(
        results.get(
            "effective_material_temperature_limit"
        )
        or
        results.get(
            "material_max_wall_temperature"
        )
        or
        results.get(
            "material_temperature_limit"
        )
    )

    margin, pass_flag = (
        _evaluate_material_temperature_limit_margin(
            wall_temperature,
            material_temperature_limit,
        )
    )

    complete = (
        wall_temperature is not None
        and
        material_temperature_limit is not None
        and
        margin is not None
        and
        pass_flag is not None
    )

    if not complete:
        status = (
            "FAIL_MATERIAL_TEMPERATURE_LIMIT_PRECHECK_INCOMPLETE"
        )

    elif pass_flag >= 1.0:
        status = (
            "PASS_MATERIAL_TEMPERATURE_LIMIT_PRECHECK"
        )

    else:
        status = (
            "FAIL_MATERIAL_TEMPERATURE_LIMIT_PRECHECK_EXCEEDED"
        )

    return {
        "material_temperature_limit_precheck_status":
            status,

        "material_temperature_limit_precheck_complete":
            complete,

        "material_temperature_limit_precheck_pass":
            (
                True
                if complete and pass_flag >= 1.0
                else False
            ),

        "material_temperature_limit_precheck_wall_temperature":
            wall_temperature,

        "material_temperature_limit_precheck_limit":
            material_temperature_limit,

        "material_temperature_limit_precheck_margin":
            margin,
    }


def attach_material_temperature_limit_precheck(results):
    if not isinstance(results, dict):
        return results

    payload = (
        build_material_temperature_limit_precheck(
            results
        )
    )

    results.update(
        payload
    )

    return results


def attach_material_temperature_limit_integration_owner(results):
    if not isinstance(results, dict):
        return results

    audit = apply_material_temperature_limit_integration(results)
    results.update(audit)
    return results


def apply_material_temperature_limit_integration(results):
    results = results if isinstance(results, dict) else {}

    phase_10b4_complete = bool(
        results.get("phase_10b4_material_density_integration_owner_complete", False)
    )

    material_mode = str(
        results.get("material_source_validation_mode") or "UNKNOWN"
    ).upper()

    material_placeholder = bool(results.get("material_source_is_placeholder", False))

    sourced_limit = _find_temperature_limit(results)

    previous_limit = _safe_float(
        results.get("effective_material_temperature_limit")
        or results.get("material_max_wall_temperature")
        or results.get("material_temperature_limit")
    )

    wall_temperature = _find_representative_wall_temperature(results)

    decision = _classify_temperature_limit_decision(
        phase_10b4_complete=phase_10b4_complete,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        sourced_limit=sourced_limit,
    )

    applied = decision == "APPLIED_SOURCED_TEMPERATURE_LIMIT"

    if applied:
        results["effective_material_temperature_limit"] = sourced_limit
        results["material_max_wall_temperature"] = sourced_limit
        results["material_temperature_limit_source"] = "SOURCED_MATERIAL_TEMPERATURE_LIMIT"
    else:
        results["effective_material_temperature_limit"] = previous_limit
        results["material_temperature_limit_source"] = "UNCHANGED_STATIC_OR_FALLBACK"

    final_limit = _safe_float(results.get("effective_material_temperature_limit"))

    margin, pass_flag = (
        _evaluate_material_temperature_limit_margin(
            wall_temperature,
            final_limit,
        )
    )

    if not applied:
        pass_flag = 0.0 if _leaf_16u66_is_fail_like(decision) else pass_flag

    results["material_temperature_limit_margin"] = margin
    results["material_temperature_limit_pass"] = pass_flag

    complete = phase_10b4_complete

    status = (
        "PASS_PHASE_10B5_MATERIAL_TEMPERATURE_LIMIT_INTEGRATION_OWNER"
        if complete
        else "FAIL_PHASE_10B5_MATERIAL_TEMPERATURE_LIMIT_INTEGRATION_OWNER"
    )

    blockers = []
    if _leaf_16u66_is_fail_like(decision):
        blockers.append(decision)

    text = build_material_temperature_limit_integration_text(
        status=status,
        complete=complete,
        decision=decision,
        applied=applied,
        material_mode=material_mode,
        material_placeholder=material_placeholder,
        previous_limit=previous_limit,
        sourced_limit=sourced_limit,
        final_limit=final_limit,
        wall_temperature=wall_temperature,
        margin=margin,
        pass_flag=pass_flag,
        blockers=blockers,
    )

    return {
        "phase_10b5_material_temperature_limit_integration_owner_complete": complete,
        "phase_10b5_material_temperature_limit_integration_owner_status": status,
        "phase_10b5_material_temperature_limit_integration_owner_text": text,
        "phase_10b5_material_temperature_limit_integration_owner_decision": decision,
        "phase_10b5_material_temperature_limit_integration_owner_applied": applied,
        "phase_10b5_material_temperature_limit_integration_owner_blockers": blockers,
        "phase_10b5_previous_material_temperature_limit": previous_limit,
        "phase_10b5_sourced_material_temperature_limit": sourced_limit,
        "phase_10b5_final_material_temperature_limit": final_limit,
        "phase_10b5_wall_temperature_checked": wall_temperature,
        "phase_10b5_material_temperature_limit_margin": margin,
        "phase_10b5_material_temperature_limit_pass": pass_flag,
        "stage_10b_material_temperature_limit_integration_complete": complete,
        "stage_10b_material_temperature_limit_integration_status": decision,
    }


def _find_temperature_limit(results):
    direct_candidates = (
        "sourced_material_temperature_limit",
        "material_sourced_temperature_limit",
        "material_max_service_temperature",
        "material_max_wall_temperature_sourced",
    )

    for key in direct_candidates:
        value = _safe_float(results.get(key))
        if value is not None and value > 0:
            return value

    interpolation_results = results.get("material_property_interpolation_results", {})
    if not isinstance(interpolation_results, dict):
        interpolation_results = {}

    possible_entries = (
        "max_temperature",
        "maximum_temperature",
        "temperature_limit",
        "max_service_temperature",
        "max_wall_temperature",
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


def _find_representative_wall_temperature(results):
    candidates = (
        "maximum_hot_gas_wall_temperature",
        "max_hot_gas_wall_temperature",
        "max_wall_temperature",
        "hot_gas_side_wall_temperature",
        "selected_gas_side_recovery_temperature",
    )

    for key in candidates:
        value = _safe_float(results.get(key))
        if value is not None:
            return value

    profiles = (
        results.get("variable_geometry_thermal_profile"),
        results.get("regen_axial_profile"),
    )

    max_seen = None

    for profile in profiles:
        if not isinstance(profile, list):
            continue

        for station in profile:
            if not isinstance(station, dict):
                continue

            for key in (
                "hot_gas_side_wall_temperature",
                "Twg",
                "wall_temperature",
                "hot_wall_temperature",
            ):
                value = _safe_float(station.get(key))
                if value is not None:
                    max_seen = value if max_seen is None else max(max_seen, value)

    return max_seen


def _classify_temperature_limit_decision(
        phase_10b4_complete,
        material_mode,
        material_placeholder,
        sourced_limit,
):
    if not phase_10b4_complete:
        return "BLOCKED_PHASE_10B4_INCOMPLETE"

    if material_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if material_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if material_mode != "SOURCED_VALIDATION_MODE":
        return "BLOCKED_UNSOURCED_MODE"

    if sourced_limit is None:
        return "BLOCKED_MISSING_SOURCED_TEMPERATURE_LIMIT"

    if sourced_limit <= 0:
        return "BLOCKED_INVALID_SOURCED_TEMPERATURE_LIMIT"

    return "APPLIED_SOURCED_TEMPERATURE_LIMIT"


def build_material_temperature_limit_integration_text(
        status,
        complete,
        decision,
        applied,
        material_mode,
        material_placeholder,
        previous_limit,
        sourced_limit,
        final_limit,
        wall_temperature,
        margin,
        pass_flag,
        blockers,
):
    lines = []

    lines.append("PHASE 10B.5 — MATERIAL TEMPERATURE LIMIT INTEGRATION OWNER")
    lines.append("==========================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Integrates sourced material temperature limit into survivability validation.")
    lines.append("- Creates margin and pass/fail ownership.")
    lines.append("- Blocks placeholder and partial-source authority.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Material validation mode: {material_mode}")
    lines.append(f"- Material placeholder: {material_placeholder}")
    lines.append(f"- Previous material temperature limit: {previous_limit}")
    lines.append(f"- Sourced material temperature limit: {sourced_limit}")
    lines.append(f"- Wall temperature checked: {wall_temperature}")
    lines.append("")
    lines.append("Decision:")
    lines.append(f"- Integration decision: {decision}")
    lines.append(f"- Applied to solver pathway: {applied}")
    lines.append(f"- Final effective material temperature limit: {final_limit}")
    lines.append(f"- Temperature margin: {margin}")
    lines.append(f"- Temperature limit pass flag: {pass_flag}")
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
        lines.append("Sourced material temperature limit is now the active survivability limit.")
    else:
        lines.append("Sourced material temperature limit was not applied because conservative gating blocked it.")

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        numeric = float(value)
        if not math.isfinite(numeric):
            return None
        return numeric
    except Exception:
        return None
