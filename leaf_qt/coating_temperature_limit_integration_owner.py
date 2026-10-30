
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u54_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u54_is_fail_like(text) or _leaf_16u54_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u54_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u54_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u54_is_fail_like(value):
    return _leaf_16u54_status_severity(value) == "FAIL"


def _leaf_16u54_is_warn_like(value):
    return _leaf_16u54_status_severity(value) == "WARN"


def _leaf_16u54_is_pass_like(value):
    return _leaf_16u54_status_severity(value) == "PASS"


"""
PHASE 10C.5
Coating Temperature Limit Integration Owner

Purpose:
    Integrate sourced coating temperature limits into an owned coating
    survivability pathway.

This phase does NOT yet modify wall temperature, heat flux, or regen marching.
It only creates coating temperature limit authority and pass/fail ownership.
"""


def attach_coating_temperature_limit_integration_owner(results):
    if not isinstance(results, dict):
        return results

    audit = apply_coating_temperature_limit_integration(results)
    results.update(audit)
    return results


def apply_coating_temperature_limit_integration(results):
    results = results if isinstance(results, dict) else {}

    phase_10c4_complete = bool(
        results.get("phase_10c4_coating_thermal_resistance_integration_owner_complete", False)
    )

    coating_selected = _coating_is_selected(results)

    coating_mode = str(
        results.get("coating_source_validation_mode")
        or results.get("coating_validation_mode")
        or "UNKNOWN"
    ).upper()

    coating_placeholder = bool(results.get("coating_source_is_placeholder", False))

    sourced_limit = _find_coating_temperature_limit(results)

    previous_limit = _safe_float(
        results.get("effective_coating_temperature_limit")
        or results.get("coating_max_temperature")
        or results.get("coating_temperature_limit")
    )

    coating_temperature = _find_representative_coating_temperature(results)

    decision = _classify_coating_temperature_limit_decision(
        phase_10c4_complete=phase_10c4_complete,
        coating_selected=coating_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        sourced_limit=sourced_limit,
    )

    applied = decision == "APPLIED_SOURCED_COATING_TEMPERATURE_LIMIT"

    if applied:
        results["effective_coating_temperature_limit"] = sourced_limit
        results["coating_max_temperature"] = sourced_limit
        results["sourced_coating_temperature_limit"] = sourced_limit
        results["coating_temperature_limit_source"] = "SOURCED_COATING_TEMPERATURE_LIMIT"
    else:
        results["effective_coating_temperature_limit"] = previous_limit
        results["sourced_coating_temperature_limit"] = sourced_limit
        results["coating_temperature_limit_source"] = "UNCHANGED_STATIC_OR_FALLBACK"

    final_limit = _safe_float(results.get("effective_coating_temperature_limit"))

    margin = None
    pass_flag = None

    if coating_temperature is not None and final_limit is not None:
        margin = final_limit - coating_temperature
        pass_flag = 1.0 if margin >= 0 else 0.0

    if not coating_selected:
        pass_flag = None

    if not applied and _leaf_16u54_is_fail_like(decision):
        pass_flag = 0.0

    results["coating_temperature_limit_margin"] = margin
    results["coating_temperature_limit_pass"] = pass_flag

    complete = phase_10c4_complete

    status = (
        "PASS_PHASE_10C5_COATING_TEMPERATURE_LIMIT_INTEGRATION_OWNER"
        if complete
        else "FAIL_PHASE_10C5_COATING_TEMPERATURE_LIMIT_INTEGRATION_OWNER"
    )

    blockers = []
    if _leaf_16u54_is_fail_like(decision):
        blockers.append(decision)

    text = build_coating_temperature_limit_integration_text(
        status=status,
        complete=complete,
        decision=decision,
        applied=applied,
        coating_selected=coating_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        previous_limit=previous_limit,
        sourced_limit=sourced_limit,
        final_limit=final_limit,
        coating_temperature=coating_temperature,
        margin=margin,
        pass_flag=pass_flag,
        blockers=blockers,
    )

    return {
        "phase_10c5_coating_temperature_limit_integration_owner_complete": complete,
        "phase_10c5_coating_temperature_limit_integration_owner_status": status,
        "phase_10c5_coating_temperature_limit_integration_owner_text": text,
        "phase_10c5_coating_temperature_limit_integration_owner_decision": decision,
        "phase_10c5_coating_temperature_limit_integration_owner_applied": applied,
        "phase_10c5_coating_temperature_limit_integration_owner_blockers": blockers,
        "phase_10c5_previous_coating_temperature_limit": previous_limit,
        "phase_10c5_sourced_coating_temperature_limit": sourced_limit,
        "phase_10c5_final_coating_temperature_limit": final_limit,
        "phase_10c5_coating_temperature_checked": coating_temperature,
        "phase_10c5_coating_temperature_limit_margin": margin,
        "phase_10c5_coating_temperature_limit_pass": pass_flag,
        "stage_10c_coating_temperature_limit_integration_complete": complete,
        "stage_10c_coating_temperature_limit_integration_status": decision,
    }


def _find_coating_temperature_limit(results):
    direct_candidates = (
        "sourced_coating_temperature_limit",
        "coating_sourced_temperature_limit",
        "coating_temperature_limit_sourced",
        "coating_max_temperature_sourced",
        "coating_max_service_temperature",
    )

    for key in direct_candidates:
        value = _safe_float(results.get(key))
        if value is not None and value > 0:
            return value

    interpolation_results = results.get("coating_property_interpolation_results", {})
    if not isinstance(interpolation_results, dict):
        interpolation_results = {}

    possible_entries = (
        "max_temperature",
        "maximum_temperature",
        "temperature_limit",
        "max_service_temperature",
        "coating_temperature_limit",
        "coating_max_temperature",
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


def _find_representative_coating_temperature(results):
    candidates = (
        "coating_hot_face_temperature",
        "coating_surface_temperature",
        "hot_gas_side_wall_temperature",
        "max_hot_gas_wall_temperature",
        "maximum_hot_gas_wall_temperature",
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
                "coating_hot_face_temperature",
                "coating_surface_temperature",
                "hot_gas_side_wall_temperature",
                "Twg",
                "wall_temperature",
                "hot_wall_temperature",
            ):
                value = _safe_float(station.get(key))
                if value is not None:
                    max_seen = value if max_seen is None else max(max_seen, value)

    return max_seen


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


def _classify_coating_temperature_limit_decision(
        phase_10c4_complete,
        coating_selected,
        coating_mode,
        coating_placeholder,
        sourced_limit,
):
    if not phase_10c4_complete:
        return "BLOCKED_PHASE_10C4_INCOMPLETE"

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

    if sourced_limit is None:
        return "BLOCKED_MISSING_SOURCED_COATING_TEMPERATURE_LIMIT"

    if sourced_limit <= 0:
        return "BLOCKED_INVALID_SOURCED_COATING_TEMPERATURE_LIMIT"

    return "APPLIED_SOURCED_COATING_TEMPERATURE_LIMIT"


def build_coating_temperature_limit_integration_text(
        status,
        complete,
        decision,
        applied,
        coating_selected,
        coating_mode,
        coating_placeholder,
        previous_limit,
        sourced_limit,
        final_limit,
        coating_temperature,
        margin,
        pass_flag,
        blockers,
):
    lines = []

    lines.append("PHASE 10C.5 — COATING TEMPERATURE LIMIT INTEGRATION OWNER")
    lines.append("=========================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Integrates sourced coating temperature limit.")
    lines.append("- Creates coating temperature margin and pass/fail ownership.")
    lines.append("- Does not yet modify wall temperature, heat flux, or regen marching.")
    lines.append("- Blocks placeholder and partial-source authority.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Coating selected: {coating_selected}")
    lines.append(f"- Coating validation mode: {coating_mode}")
    lines.append(f"- Coating placeholder: {coating_placeholder}")
    lines.append(f"- Previous coating temperature limit: {previous_limit}")
    lines.append(f"- Sourced coating temperature limit: {sourced_limit}")
    lines.append(f"- Coating temperature checked: {coating_temperature}")
    lines.append("")
    lines.append("Decision:")
    lines.append(f"- Integration decision: {decision}")
    lines.append(f"- Applied to coating temperature pathway: {applied}")
    lines.append(f"- Final effective_coating_temperature_limit: {final_limit}")
    lines.append(f"- Coating temperature margin: {margin}")
    lines.append(f"- Coating temperature pass flag: {pass_flag}")
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
        lines.append("Sourced coating temperature limit is now the active coating survivability limit.")
    elif decision == "NO_COATING_SELECTED":
        lines.append("No coating is selected, so coating temperature limit integration is inactive.")
    else:
        lines.append("Coating temperature limit was not applied because conservative gating blocked it.")

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None
