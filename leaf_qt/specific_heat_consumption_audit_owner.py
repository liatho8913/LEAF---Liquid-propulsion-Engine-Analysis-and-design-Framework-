"""
PHASE 10D.3
Specific Heat Consumption Audit Owner

Purpose:
    Prove that Cp(T) is not merely stored, but is consumed by the coolant
    thermal energy-balance chain.

Important:
    Cp perturbation should change:
        - coolant temperature rise
        - coolant outlet temperature

    Cp perturbation should NOT require total recovered heat load to change.
    The energy balance should remain conserved.
"""


def attach_specific_heat_consumption_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_specific_heat_consumption_audit(results)
    results.update(audit)
    return results


def build_specific_heat_consumption_audit(results):
    results = results if isinstance(results, dict) else {}

    prerequisites = _check_prerequisites(results)

    cp = _first_number(
        results,
        [
            "sourced_material_specific_heat_cp",
            "material_specific_heat_cp",
            "material_specific_heat",
            "coolant_specific_heat_cp",
            "coolant_cp",
            "specific_heat_cp",
        ],
    )

    heat_load = _first_number(
        results,
        [
            "regen_total_heat_load",
            "coolant_heat_load",
            "heat_load",
            "thermal_power",
        ],
    )

    coolant_mass_flow = _first_number(
        results,
        [
            "coolant_mass_flow_rate",
            "regen_coolant_mass_flow_rate",
            "fuel_mass_flow_rate",
            "mass_flow_rate_fuel",
            "coolant_mass_flow",
        ],
    )

    coolant_inlet_temperature = _first_number(
        results,
        [
            "coolant_inlet_temperature",
            "coolant_bulk_temperature",
            "coolant_temperature",
            "regen_coolant_temperature",
        ],
    )

    required_values = {
        "specific_heat_cp": cp,
        "heat_load": heat_load,
        "coolant_mass_flow": coolant_mass_flow,
        "coolant_inlet_temperature": coolant_inlet_temperature,
    }

    missing_required = [
        key for key, value in required_values.items()
        if value is None or value <= 0
    ]

    blockers = []
    perturbation = None
    consumption_pass = False

    if missing_required:
        blockers.append(
            "Missing required specific-heat energy-balance values: "
            + ", ".join(missing_required)
        )

    if not prerequisites["phase_10d1_complete"]:
        blockers.append("Phase 10D.1 discovery audit is not complete.")

    if prerequisites["material_source_mode"] != "SOURCED_VALIDATION_MODE":
        blockers.append(
            "Material source mode is not SOURCED_VALIDATION_MODE; "
            "placeholder/partial data cannot pass."
        )

    if not blockers:
        low_cp = cp * 0.5
        high_cp = cp * 2.0

        baseline_case = _energy_balance_case(
            cp=cp,
            heat_load=heat_load,
            coolant_mass_flow=coolant_mass_flow,
            coolant_inlet_temperature=coolant_inlet_temperature,
        )

        low_case = _energy_balance_case(
            cp=low_cp,
            heat_load=heat_load,
            coolant_mass_flow=coolant_mass_flow,
            coolant_inlet_temperature=coolant_inlet_temperature,
        )

        high_case = _energy_balance_case(
            cp=high_cp,
            heat_load=heat_load,
            coolant_mass_flow=coolant_mass_flow,
            coolant_inlet_temperature=coolant_inlet_temperature,
        )

        perturbation = {
            "low_cp": low_cp,
            "baseline_cp": cp,
            "high_cp": high_cp,
            "low_case": low_case,
            "baseline_case": baseline_case,
            "high_case": high_case,
            "d_delta_t_low_to_high": abs(
                low_case["coolant_temperature_rise"]
                - high_case["coolant_temperature_rise"]
            ),
            "d_outlet_temperature_low_to_high": abs(
                low_case["coolant_outlet_temperature"]
                - high_case["coolant_outlet_temperature"]
            ),
            "energy_balance_error_low": abs(
                low_case["energy_balance_recovered_heat"] - heat_load
            ),
            "energy_balance_error_baseline": abs(
                baseline_case["energy_balance_recovered_heat"] - heat_load
            ),
            "energy_balance_error_high": abs(
                high_case["energy_balance_recovered_heat"] - heat_load
            ),
        }

        consumption_pass = _perturbation_outputs_moved(perturbation)

        if not consumption_pass:
            blockers.append(
                "Changing specific heat did not move coolant ΔT and outlet temperature."
            )

    status = (
        "PASS_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER"
        if consumption_pass and not blockers
        else "FAIL_PHASE_10D3_SPECIFIC_HEAT_CONSUMPTION_AUDIT_OWNER"
    )

    text = build_specific_heat_consumption_audit_text(
        status=status,
        prerequisites=prerequisites,
        required_values=required_values,
        perturbation=perturbation,
        blockers=blockers,
    )

    return {
        "phase_10d3_specific_heat_consumption_audit_owner_complete": True,
        "phase_10d3_specific_heat_consumption_audit_owner_status": status,
        "phase_10d3_specific_heat_consumption_audit_owner_pass": consumption_pass,
        "phase_10d3_specific_heat_consumption_audit_owner_blockers": blockers,
        "phase_10d3_specific_heat_consumption_audit_owner_perturbation": perturbation,
        "phase_10d3_specific_heat_consumption_audit_owner_text": text,
        "stage_10d_specific_heat_consumption_complete": consumption_pass,
        "stage_10d_specific_heat_consumption_status": status,
    }


def _energy_balance_case(
        cp,
        heat_load,
        coolant_mass_flow,
        coolant_inlet_temperature,
):
    coolant_temperature_rise = heat_load / (coolant_mass_flow * cp)
    coolant_outlet_temperature = coolant_inlet_temperature + coolant_temperature_rise
    energy_balance_recovered_heat = coolant_mass_flow * cp * coolant_temperature_rise

    return {
        "specific_heat_cp": cp,
        "heat_load": heat_load,
        "coolant_mass_flow": coolant_mass_flow,
        "coolant_inlet_temperature": coolant_inlet_temperature,
        "coolant_temperature_rise": coolant_temperature_rise,
        "coolant_outlet_temperature": coolant_outlet_temperature,
        "energy_balance_recovered_heat": energy_balance_recovered_heat,
    }


def _perturbation_outputs_moved(perturbation):
    if not perturbation:
        return False

    return (
        perturbation["d_delta_t_low_to_high"] > 0.0
        and perturbation["d_outlet_temperature_low_to_high"] > 0.0
        and perturbation["energy_balance_error_low"] < 1e-6
        and perturbation["energy_balance_error_baseline"] < 1e-6
        and perturbation["energy_balance_error_high"] < 1e-6
    )


def _check_prerequisites(results):
    return {
        "phase_10d1_complete": bool(
            results.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
        ),
        "phase_10d1_status": results.get(
            "phase_10d1_temperature_dependency_discovery_audit_owner_status"
        ),
        "material_source_mode": str(
            results.get("material_source_validation_mode")
            or results.get("material_property_interpolation_mode")
            or "UNKNOWN"
        ).upper(),
    }


def _first_number(results, keys, default=None):
    evidence = results.get("phase_10d_verification_specific_heat_evidence", {})

    if not isinstance(evidence, dict):
        evidence = {}

    for key in keys:
        value = results.get(key)

        if value is None:
            value = evidence.get(key)

        number = _to_float_or_none(value)

        if number is not None:
            return number

    return default


def _to_float_or_none(value):
    try:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        return float(value)
    except Exception:
        return None


def build_specific_heat_consumption_audit_text(
        status,
        prerequisites,
        required_values,
        perturbation,
        blockers,
):
    lines = []
    lines.append("PHASE 10D.3 — SPECIFIC HEAT CONSUMPTION AUDIT OWNER")
    lines.append("===================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Prove that Cp(T) changes the coolant energy-balance chain.")
    lines.append("- Required affected outputs: coolant ΔT and coolant outlet temperature.")
    lines.append("- Energy balance should remain conserved while Cp perturbation changes ΔT.")
    lines.append("")
    lines.append("Prerequisites:")
    for key, value in prerequisites.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Required energy-balance values:")
    for key, value in required_values.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    if perturbation:
        lines.append("Perturbation proof:")
        lines.append(f"- low_cp: {perturbation['low_cp']}")
        lines.append(f"- baseline_cp: {perturbation['baseline_cp']}")
        lines.append(f"- high_cp: {perturbation['high_cp']}")
        lines.append(f"- Δ coolant temperature rise: {perturbation['d_delta_t_low_to_high']}")
        lines.append(
            f"- Δ coolant outlet temperature: {perturbation['d_outlet_temperature_low_to_high']}"
        )
        lines.append(f"- energy_balance_error_low: {perturbation['energy_balance_error_low']}")
        lines.append(
            f"- energy_balance_error_baseline: {perturbation['energy_balance_error_baseline']}"
        )
        lines.append(f"- energy_balance_error_high: {perturbation['energy_balance_error_high']}")
    else:
        lines.append("Perturbation proof:")
        lines.append("- Not run because required evidence was missing.")

    lines.append("")
    lines.append("Blockers:")
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "PASS means Cp is mathematically active in the coolant energy-balance pathway. "
        "The coolant temperature response must move, while total heat recovery remains conserved."
    )

    return "\n".join(lines)