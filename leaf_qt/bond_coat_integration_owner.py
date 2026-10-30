
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u50_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u50_is_fail_like(text) or _leaf_16u50_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u50_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u50_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u50_is_fail_like(value):
    return _leaf_16u50_status_severity(value) == "FAIL"


def _leaf_16u50_is_warn_like(value):
    return _leaf_16u50_status_severity(value) == "WARN"


def _leaf_16u50_is_pass_like(value):
    return _leaf_16u50_status_severity(value) == "PASS"


"""
PHASE 10C.6
Bond Coat Integration Owner

Purpose:
    Own the optional bond coat layer in the coating stack.

This phase creates:
    - bond coat selection detection
    - bond coat conductivity
    - bond coat thickness
    - bond coat thermal resistance
    - bond coat temperature limit
    - bond coat margin/pass flag

This phase does NOT yet modify regen wall temperatures, heat flux, or axial marching.
"""


def attach_bond_coat_integration_owner(results):
    if not isinstance(results, dict):
        return results

    audit = apply_bond_coat_integration(results)
    results.update(audit)
    return results


def apply_bond_coat_integration(results):
    results = results if isinstance(results, dict) else {}

    phase_10c5_complete = bool(
        results.get("phase_10c5_coating_temperature_limit_integration_owner_complete", False)
    )

    bond_selected = _bond_coat_is_selected(results)

    coating_mode = str(
        results.get("coating_source_validation_mode")
        or results.get("bond_coat_source_validation_mode")
        or results.get("coating_validation_mode")
        or "UNKNOWN"
    ).upper()

    bond_placeholder = bool(
        results.get("bond_coat_source_is_placeholder", False)
        or results.get("coating_source_is_placeholder", False)
    )

    bond_k = _find_bond_value(
        results,
        direct_keys=(
            "sourced_bond_coat_thermal_conductivity",
            "bond_coat_sourced_thermal_conductivity",
            "bond_coat_thermal_conductivity",
        ),
        interpolation_keys=(
            "thermal_conductivity",
            "bond_coat_thermal_conductivity",
            "conductivity",
            "k",
        ),
    )

    bond_t = _find_bond_value(
        results,
        direct_keys=(
            "sourced_bond_coat_thickness",
            "bond_coat_sourced_thickness",
            "bond_coat_thickness",
        ),
        interpolation_keys=(
            "thickness",
            "bond_coat_thickness",
            "nominal_thickness",
        ),
    )

    bond_limit = _find_bond_value(
        results,
        direct_keys=(
            "sourced_bond_coat_temperature_limit",
            "bond_coat_sourced_temperature_limit",
            "bond_coat_temperature_limit",
            "bond_coat_max_temperature",
        ),
        interpolation_keys=(
            "max_temperature",
            "temperature_limit",
            "bond_coat_temperature_limit",
            "bond_coat_max_temperature",
            "max_service_temperature",
        ),
    )

    bond_temperature = _find_bond_coat_temperature(results)

    decision = _classify_bond_coat_decision(
        phase_10c5_complete=phase_10c5_complete,
        bond_selected=bond_selected,
        coating_mode=coating_mode,
        bond_placeholder=bond_placeholder,
        bond_k=bond_k,
        bond_t=bond_t,
    )

    applied = decision == "APPLIED_BOND_COAT_INTEGRATION"

    bond_r = None
    if applied:
        bond_r = bond_t / bond_k

        results["bond_coat_thermal_conductivity"] = bond_k
        results["bond_coat_thickness"] = bond_t
        results["bond_coat_thermal_resistance"] = bond_r
        results["effective_bond_coat_thermal_resistance"] = bond_r
        results["bond_coat_thermal_resistance_source"] = (
            "CALCULATED_FROM_OWNED_BOND_COAT_THICKNESS_AND_CONDUCTIVITY"
        )

        if bond_limit is not None and bond_limit > 0:
            results["bond_coat_temperature_limit"] = bond_limit
            results["effective_bond_coat_temperature_limit"] = bond_limit
            results["bond_coat_temperature_limit_source"] = "SOURCED_BOND_COAT_TEMPERATURE_LIMIT"
    else:
        results["bond_coat_thermal_resistance_source"] = "UNCHANGED_STATIC_OR_FALLBACK"
        results["bond_coat_temperature_limit_source"] = "UNCHANGED_STATIC_OR_FALLBACK"

    final_limit = _safe_float(results.get("effective_bond_coat_temperature_limit"))

    margin = None
    pass_flag = None

    if bond_temperature is not None and final_limit is not None:
        margin = final_limit - bond_temperature
        pass_flag = 1.0 if margin >= 0 else 0.0

    if not bond_selected:
        pass_flag = None

    if not applied and _leaf_16u50_is_fail_like(decision):
        pass_flag = 0.0

    results["bond_coat_temperature_limit_margin"] = margin
    results["bond_coat_temperature_limit_pass"] = pass_flag
    results["bond_coat_integration_active"] = bool(applied)

    complete = phase_10c5_complete

    status = (
        "PASS_PHASE_10C6_BOND_COAT_INTEGRATION_OWNER"
        if complete
        else "FAIL_PHASE_10C6_BOND_COAT_INTEGRATION_OWNER"
    )

    blockers = []
    if _leaf_16u50_is_fail_like(decision):
        blockers.append(decision)

    text = build_bond_coat_integration_text(
        status=status,
        complete=complete,
        decision=decision,
        applied=applied,
        bond_selected=bond_selected,
        coating_mode=coating_mode,
        bond_placeholder=bond_placeholder,
        bond_k=bond_k,
        bond_t=bond_t,
        bond_r=bond_r,
        bond_limit=final_limit,
        bond_temperature=bond_temperature,
        margin=margin,
        pass_flag=pass_flag,
        blockers=blockers,
    )

    return {
        "phase_10c6_bond_coat_integration_owner_complete": complete,
        "phase_10c6_bond_coat_integration_owner_status": status,
        "phase_10c6_bond_coat_integration_owner_text": text,
        "phase_10c6_bond_coat_integration_owner_decision": decision,
        "phase_10c6_bond_coat_integration_owner_applied": applied,
        "phase_10c6_bond_coat_integration_owner_blockers": blockers,
        "phase_10c6_bond_coat_selected": bond_selected,
        "phase_10c6_bond_coat_thermal_conductivity": bond_k,
        "phase_10c6_bond_coat_thickness": bond_t,
        "phase_10c6_bond_coat_thermal_resistance": bond_r,
        "phase_10c6_bond_coat_temperature_limit": final_limit,
        "phase_10c6_bond_coat_temperature_checked": bond_temperature,
        "phase_10c6_bond_coat_temperature_margin": margin,
        "phase_10c6_bond_coat_temperature_pass": pass_flag,
        "stage_10c_bond_coat_integration_complete": complete,
        "stage_10c_bond_coat_integration_status": decision,
    }


def _bond_coat_is_selected(results):
    name = str(
        results.get("selected_bond_coat_material")
        or results.get("bond_coat_material")
        or results.get("bond_coat_name")
        or ""
    ).strip().upper()

    enabled = results.get("bond_coat_enabled", None)

    if isinstance(enabled, bool):
        if not enabled:
            return False
        if enabled:
            return True

    thickness = _safe_float(results.get("bond_coat_thickness"))

    if name in ("", "NONE", "NO_BOND_COAT", "NO_BONDCOAT", "N/A"):
        return False

    if thickness is not None and thickness > 0:
        return True

    return bool(name)


def _find_bond_value(results, direct_keys, interpolation_keys):
    for key in direct_keys:
        value = _safe_float(results.get(key))
        if value is not None and value > 0:
            return value

    interpolation_results = (
        results.get("bond_coat_property_interpolation_results")
        or results.get("coating_property_interpolation_results")
        or {}
    )

    if not isinstance(interpolation_results, dict):
        interpolation_results = {}

    bond_section = interpolation_results.get("bond_coat", {})
    search_spaces = []

    if isinstance(bond_section, dict):
        search_spaces.append(bond_section)

    search_spaces.append(interpolation_results)

    for space in search_spaces:
        for key in interpolation_keys:
            entry = space.get(key)

            if isinstance(entry, dict):
                value = _safe_float(entry.get("value"))
            else:
                value = _safe_float(entry)

            if value is not None and value > 0:
                return value

    return None


def _find_bond_coat_temperature(results):
    candidates = (
        "bond_coat_temperature",
        "bond_coat_hot_face_temperature",
        "bond_coat_interface_temperature",
        "coating_wall_interface_temperature",
        "coating_surface_temperature",
        "hot_gas_side_wall_temperature",
        "max_hot_gas_wall_temperature",
    )

    for key in candidates:
        value = _safe_float(results.get(key))
        if value is not None:
            return value

    return None


def _classify_bond_coat_decision(
        phase_10c5_complete,
        bond_selected,
        coating_mode,
        bond_placeholder,
        bond_k,
        bond_t,
):
    if not phase_10c5_complete:
        return "BLOCKED_PHASE_10C5_INCOMPLETE"

    if not bond_selected:
        return "NO_BOND_COAT_SELECTED"

    if bond_placeholder:
        return "BLOCKED_PLACEHOLDER"

    if coating_mode == "PLACEHOLDER_MODE":
        return "BLOCKED_PLACEHOLDER"

    if coating_mode == "PARTIAL_SOURCE_MODE":
        return "BLOCKED_PARTIAL_SOURCE"

    if coating_mode != "SOURCED_VALIDATION_MODE":
        return "BLOCKED_UNSOURCED_MODE"

    if bond_k is None:
        return "BLOCKED_MISSING_BOND_COAT_CONDUCTIVITY"

    if bond_k <= 0:
        return "BLOCKED_INVALID_BOND_COAT_CONDUCTIVITY"

    if bond_t is None:
        return "BLOCKED_MISSING_BOND_COAT_THICKNESS"

    if bond_t <= 0:
        return "BLOCKED_INVALID_BOND_COAT_THICKNESS"

    return "APPLIED_BOND_COAT_INTEGRATION"


def build_bond_coat_integration_text(
        status,
        complete,
        decision,
        applied,
        bond_selected,
        coating_mode,
        bond_placeholder,
        bond_k,
        bond_t,
        bond_r,
        bond_limit,
        bond_temperature,
        margin,
        pass_flag,
        blockers,
):
    lines = []

    lines.append("PHASE 10C.6 — BOND COAT INTEGRATION OWNER")
    lines.append("=========================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Integrates optional bond coat layer ownership.")
    lines.append("- Calculates bond coat thermal resistance when selected and sourced.")
    lines.append("- Creates bond coat temperature margin/pass ownership when limit exists.")
    lines.append("- Does not yet alter wall temperature, heat flux, or regen marching.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Bond coat selected: {bond_selected}")
    lines.append(f"- Coating/bond validation mode: {coating_mode}")
    lines.append(f"- Bond/coating placeholder: {bond_placeholder}")
    lines.append(f"- Bond coat conductivity: {bond_k}")
    lines.append(f"- Bond coat thickness: {bond_t}")
    lines.append(f"- Bond coat temperature limit: {bond_limit}")
    lines.append(f"- Bond coat temperature checked: {bond_temperature}")
    lines.append("")
    lines.append("Decision:")
    lines.append(f"- Integration decision: {decision}")
    lines.append(f"- Applied to bond coat pathway: {applied}")
    lines.append(f"- Bond coat thermal resistance: {bond_r}")
    lines.append(f"- Bond coat temperature margin: {margin}")
    lines.append(f"- Bond coat temperature pass flag: {pass_flag}")
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
        lines.append("Bond coat layer is now owned as part of the coating stack.")
    elif decision == "NO_BOND_COAT_SELECTED":
        lines.append("No bond coat is selected, so bond coat integration is inactive.")
    else:
        lines.append("Bond coat integration was blocked by conservative gating.")

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None
