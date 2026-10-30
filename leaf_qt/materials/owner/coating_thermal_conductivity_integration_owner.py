
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
PHASE 10C.2
Coating Thermal Conductivity Integration Owner

Purpose:
    Integrate sourced/interpolated coating thermal conductivity into an owned
    coating conductivity solver pathway.

This phase does NOT yet calculate coating thermal resistance.
That comes later.
"""


def attach_coating_thermal_conductivity_integration_owner(results):
    if not isinstance(results, dict):
        return results

    audit = apply_coating_thermal_conductivity_integration(results)
    results.update(audit)
    return results


def apply_coating_thermal_conductivity_integration(results):
    results = results if isinstance(results, dict) else {}

    phase_10c1_complete = bool(
        results.get("phase_10c1_coating_property_consumption_audit_owner_complete", False)
    )

    coating_selected = _coating_is_selected(results)

    coating_mode = str(
        results.get("coating_source_validation_mode")
        or results.get("coating_validation_mode")
        or "UNKNOWN"
    ).upper()

    coating_placeholder = bool(results.get("coating_source_is_placeholder", False))

    sourced_k = _find_coating_conductivity(results)

    previous_k = _safe_float(
        results.get("coating_thermal_conductivity")
        or results.get("coating_conductivity")
    )

    decision = _classify_coating_k_decision(
        phase_10c1_complete=phase_10c1_complete,
        coating_selected=coating_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        sourced_k=sourced_k,
    )

    applied = decision == "APPLIED_SOURCED_COATING_KT"

    if applied:
        results["coating_thermal_conductivity"] = sourced_k
        results["sourced_coating_thermal_conductivity"] = sourced_k
        results["coating_thermal_conductivity_source"] = (
            "SOURCED_INTERPOLATED_COATING_KT"
        )
    else:
        results["sourced_coating_thermal_conductivity"] = sourced_k
        results["coating_thermal_conductivity_source"] = (
            "UNCHANGED_STATIC_OR_FALLBACK"
        )

    complete = phase_10c1_complete

    status = (
        "PASS_PHASE_10C2_COATING_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER"
        if complete
        else "FAIL_PHASE_10C2_COATING_THERMAL_CONDUCTIVITY_INTEGRATION_OWNER"
    )

    blockers = []
    if _leaf_16u62_is_fail_like(decision):
        blockers.append(decision)

    text = build_coating_thermal_conductivity_integration_text(
        status=status,
        complete=complete,
        decision=decision,
        applied=applied,
        coating_selected=coating_selected,
        coating_mode=coating_mode,
        coating_placeholder=coating_placeholder,
        previous_k=previous_k,
        sourced_k=sourced_k,
        final_k=_safe_float(results.get("coating_thermal_conductivity")),
        blockers=blockers,
    )

    return {
        "phase_10c2_coating_thermal_conductivity_integration_owner_complete": complete,
        "phase_10c2_coating_thermal_conductivity_integration_owner_status": status,
        "phase_10c2_coating_thermal_conductivity_integration_owner_text": text,
        "phase_10c2_coating_thermal_conductivity_integration_owner_decision": decision,
        "phase_10c2_coating_thermal_conductivity_integration_owner_applied": applied,
        "phase_10c2_coating_thermal_conductivity_integration_owner_blockers": blockers,
        "phase_10c2_previous_coating_thermal_conductivity": previous_k,
        "phase_10c2_sourced_coating_thermal_conductivity": sourced_k,
        "phase_10c2_final_coating_thermal_conductivity": _safe_float(
            results.get("coating_thermal_conductivity")
        ),
        "stage_10c_coating_thermal_conductivity_integration_complete": complete,
        "stage_10c_coating_thermal_conductivity_integration_status": decision,
    }


def _find_coating_conductivity(results):
    direct_candidates = (
        "sourced_coating_thermal_conductivity",
        "coating_sourced_thermal_conductivity",
        "coating_thermal_conductivity_sourced",
        "coating_conductivity_sourced",
    )

    for key in direct_candidates:
        value = _safe_float(results.get(key))
        if value is not None and value > 0:
            return value

    interpolation_results = results.get("coating_property_interpolation_results", {})
    if not isinstance(interpolation_results, dict):
        interpolation_results = {}

    possible_entries = (
        "thermal_conductivity",
        "coating_thermal_conductivity",
        "conductivity",
        "k",
        "k_coating",
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


def _coating_is_selected(results):
    coating_name = str(
        results.get("selected_coating_material")
        or results.get("coating_material")
        or results.get("coating_name")
        or ""
    ).strip().upper()

    thickness = _safe_float(results.get("coating_thickness"))

    if coating_name in ("", "NONE", "NO_COATING", "N/A"):
        return False

    if thickness is not None and thickness > 0:
        return True

    return bool(coating_name)


def _classify_coating_k_decision(
        phase_10c1_complete,
        coating_selected,
        coating_mode,
        coating_placeholder,
        sourced_k,
):
    if not phase_10c1_complete:
        return "BLOCKED_PHASE_10C1_INCOMPLETE"

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

    if sourced_k is None:
        return "BLOCKED_MISSING_SOURCED_COATING_KT"

    if sourced_k <= 0:
        return "BLOCKED_INVALID_SOURCED_COATING_KT"

    return "APPLIED_SOURCED_COATING_KT"


def build_coating_thermal_conductivity_integration_text(
        status,
        complete,
        decision,
        applied,
        coating_selected,
        coating_mode,
        coating_placeholder,
        previous_k,
        sourced_k,
        final_k,
        blockers,
):
    lines = []

    lines.append("PHASE 10C.2 — COATING THERMAL CONDUCTIVITY INTEGRATION OWNER")
    lines.append("============================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Complete: {complete}")
    lines.append("")
    lines.append("Scope:")
    lines.append("- Integrates sourced/interpolated coating k(T).")
    lines.append("- Does not yet calculate coating thermal resistance.")
    lines.append("- Does not yet alter wall temperature or heat flux.")
    lines.append("- Blocks placeholder and partial-source authority.")
    lines.append("")
    lines.append("Inputs:")
    lines.append(f"- Coating selected: {coating_selected}")
    lines.append(f"- Coating validation mode: {coating_mode}")
    lines.append(f"- Coating placeholder: {coating_placeholder}")
    lines.append(f"- Previous coating thermal conductivity: {previous_k}")
    lines.append(f"- Sourced/interpolated coating k(T): {sourced_k}")
    lines.append("")
    lines.append("Decision:")
    lines.append(f"- Integration decision: {decision}")
    lines.append(f"- Applied to coating conductivity pathway: {applied}")
    lines.append(f"- Final coating_thermal_conductivity: {final_k}")
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
        lines.append("Sourced coating k(T) is now available in the coating solver pathway.")
    elif decision == "NO_COATING_SELECTED":
        lines.append("No coating is selected, so coating conductivity integration is inactive.")
    else:
        lines.append("Sourced coating k(T) was not applied because conservative gating blocked it.")

    return "\n".join(lines)


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None
