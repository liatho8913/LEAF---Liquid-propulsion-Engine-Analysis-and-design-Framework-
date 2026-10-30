"""
PHASE 16J.2A — Coolant Flow Activation Layer

Purpose:
- Ensure coolant mass flow exists before regen recommendation/candidate/ranking systems.
- Converts coolant_flow_fraction into coolant_mass_flow_rate.
- Defaults coolant name safely when missing.
- Does not rank, solve candidates, mutate, accept/reject, or commit geometry.
"""

import math


def _positive(value):
    try:
        value = float(value)
        if math.isfinite(value) and value > 0.0:
            return value
    except Exception:
        return None
    return None


def _first_positive(results, keys):
    for key in keys:
        value = _positive(results.get(key))
        if value is not None:
            return value
    return None


def _first_text(results, keys):
    for key in keys:
        value = results.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def attach_regen_coolant_flow_activation_layer(results):
    if not isinstance(results, dict):
        return results

    selected_coolant_name = _first_text(results, [
        "selected_coolant_name",
        "coolant_name",
        "fuel_name",
        "fuel",
    ])

    if selected_coolant_name is None:
        selected_coolant_name = "RP-1"

    total_mass_flow = _first_positive(results, [
        "mass_flow_rate",
        "total_mass_flow_rate",
    ])

    fuel_mass_flow = _first_positive(results, [
        "fuel_mass_flow_rate",
    ])

    coolant_fraction = _first_positive(results, [
        "coolant_mass_flow_fraction",
        "coolant_flow_fraction",
        "fuel_coolant_flow_fraction",
    ])

    if coolant_fraction is None:
        coolant_fraction = 0.35

    existing_coolant_mass_flow = _first_positive(results, [
        "coolant_mass_flow_rate",
        "regen_coolant_mass_flow_rate",
    ])

    derived_from = None

    if existing_coolant_mass_flow is not None:
        coolant_mass_flow_rate = existing_coolant_mass_flow
        derived_from = "existing_coolant_mass_flow_rate"
    elif fuel_mass_flow is not None:
        coolant_mass_flow_rate = fuel_mass_flow * coolant_fraction
        derived_from = "fuel_mass_flow_rate * coolant_fraction"
    elif total_mass_flow is not None:
        coolant_mass_flow_rate = total_mass_flow * coolant_fraction
        derived_from = "mass_flow_rate * coolant_fraction"
    else:
        coolant_mass_flow_rate = None
        derived_from = "unavailable"

    complete = coolant_mass_flow_rate is not None and coolant_mass_flow_rate > 0.0

    results["selected_coolant_name"] = selected_coolant_name
    results["coolant_mass_flow_fraction"] = coolant_fraction
    results["coolant_flow_fraction"] = coolant_fraction

    if complete:
        results["coolant_mass_flow_rate"] = coolant_mass_flow_rate
        results["regen_coolant_mass_flow_rate"] = coolant_mass_flow_rate

    results["regen_coolant_flow_activation_layer_complete"] = True
    results["phase_16j2a_complete"] = True
    results["regen_coolant_flow_activation_layer_status"] = (
        "PASS_REGEN_COOLANT_FLOW_ACTIVATION_LAYER_PHASE_16J2A"
        if complete else
        "FAIL_REGEN_COOLANT_FLOW_ACTIVATION_LAYER_PHASE_16J2A"
    )
    results["phase_16j2a_status"] = results["regen_coolant_flow_activation_layer_status"]
    results["regen_coolant_flow_activation_layer_selected_coolant"] = selected_coolant_name
    results["regen_coolant_flow_activation_layer_fraction"] = coolant_fraction
    results["regen_coolant_flow_activation_layer_mass_flow_rate"] = coolant_mass_flow_rate
    results["regen_coolant_flow_activation_layer_derived_from"] = derived_from

    if complete and results.get("recommended_geometry_status") == "BLOCKED_NO_COOLANT_FLOW":
        results["recommended_geometry_status_previous"] = "BLOCKED_NO_COOLANT_FLOW"
        results["recommended_geometry_status"] = "COOLANT_FLOW_AVAILABLE_RECALC_REQUIRED"
        results["recommended_geometry_reason"] = (
            "Coolant mass flow is now available from the coolant flow activation layer. "
            "Recommended geometry requires recalculation after this attachment stage."
        )

    results["phase_16j2b_candidate_generation_recheck_allowed"] = complete

    return results
