"""
PHASE 10D.2
Material Conductivity Consumption Audit Owner

Purpose:
    Prove that material thermal conductivity is not merely stored, but is
    actually consumed by the regen thermal-resistance chain.

Rules:
    - Audit only.
    - Does not overwrite solver physics outputs.
    - Fails conservatively if required thermal-chain evidence is missing.
    - Placeholder or partial-source material modes cannot pass final consumption proof.
"""


def attach_material_conductivity_consumption_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_material_conductivity_consumption_audit(results)
    results.update(audit)
    return results


def build_material_conductivity_consumption_audit(results):
    results = results if isinstance(results, dict) else {}

    prerequisites = _check_prerequisites(results)

    baseline_k = _first_number(
        results,
        [
            "sourced_wall_thermal_conductivity",
            "wall_thermal_conductivity",
            "material_thermal_conductivity",
        ],
    )

    wall_thickness = _first_number(
        results,
        [
            "inner_wall_thickness",
            "wall_thickness",
            "regen_wall_thickness",
            "chamber_wall_thickness",
        ],
    )

    hg = _first_number(
        results,
        [
            "hot_gas_heat_transfer_coefficient",
            "regen_hot_gas_heat_transfer_coefficient",
            "hg",
        ],
    )

    hc = _first_number(
        results,
        [
            "coolant_heat_transfer_coefficient",
            "regen_coolant_heat_transfer_coefficient",
            "hc",
        ],
    )

    gas_recovery_temperature = _first_number(
        results,
        [
            "adiabatic_wall_temperature",
            "hot_gas_recovery_temperature",
            "recovery_temperature",
            "gas_recovery_temperature",
            "chamber_temperature",
            "Tc",
        ],
    )

    coolant_bulk_temperature = _first_number(
        results,
        [
            "coolant_bulk_temperature",
            "coolant_temperature",
            "coolant_inlet_temperature",
            "regen_coolant_temperature",
        ],
    )

    coating_resistance = _first_number(
        results,
        [
            "coating_thermal_resistance",
            "effective_coating_thermal_resistance",
            "explicit_coating_liner_thermal_resistance",
        ],
        default=0.0,
    )

    bond_resistance = _first_number(
        results,
        [
            "bond_coat_thermal_resistance",
            "effective_bond_coat_thermal_resistance",
        ],
        default=0.0,
    )

    required_values = {
        "baseline_k": baseline_k,
        "wall_thickness": wall_thickness,
        "hg": hg,
        "hc": hc,
        "gas_recovery_temperature": gas_recovery_temperature,
        "coolant_bulk_temperature": coolant_bulk_temperature,
    }

    missing_required = [
        key for key, value in required_values.items()
        if value is None or value <= 0
    ]

    perturbation = None
    consumption_pass = False
    blockers = []

    if missing_required:
        blockers.append(
            "Missing required thermal-chain values: "
            + ", ".join(missing_required)
        )

    if not prerequisites["phase_10d1_complete"]:
        blockers.append("Phase 10D.1 discovery audit is not complete.")

    if prerequisites["material_source_mode"] != "SOURCED_VALIDATION_MODE":
        blockers.append(
            "Material source mode is not SOURCED_VALIDATION_MODE; "
            "placeholder/partial data cannot pass."
        )

    thermal_chain_evidence_present = (
            baseline_k is not None
            and wall_thickness is not None
            and hg is not None
            and hc is not None
            and gas_recovery_temperature is not None
            and coolant_bulk_temperature is not None
    )

    if not blockers and thermal_chain_evidence_present:
        low_k = baseline_k * 0.5
        high_k = baseline_k * 2.0

        baseline_case = _thermal_chain_case(
            k=baseline_k,
            wall_thickness=wall_thickness,
            hg=hg,
            hc=hc,
            taw=gas_recovery_temperature,
            tcool=coolant_bulk_temperature,
            coating_resistance=coating_resistance,
            bond_resistance=bond_resistance,
        )

        low_case = _thermal_chain_case(
            k=low_k,
            wall_thickness=wall_thickness,
            hg=hg,
            hc=hc,
            taw=gas_recovery_temperature,
            tcool=coolant_bulk_temperature,
            coating_resistance=coating_resistance,
            bond_resistance=bond_resistance,
        )

        high_case = _thermal_chain_case(
            k=high_k,
            wall_thickness=wall_thickness,
            hg=hg,
            hc=hc,
            taw=gas_recovery_temperature,
            tcool=coolant_bulk_temperature,
            coating_resistance=coating_resistance,
            bond_resistance=bond_resistance,
        )

        perturbation = {
            "low_k": low_k,
            "baseline_k": baseline_k,
            "high_k": high_k,
            "low_case": low_case,
            "baseline_case": baseline_case,
            "high_case": high_case,
            "d_wall_resistance_low_to_high": abs(
                low_case["wall_resistance"] - high_case["wall_resistance"]
            ),
            "d_heat_flux_low_to_high": abs(
                low_case["heat_flux"] - high_case["heat_flux"]
            ),
            "d_twg_low_to_high": abs(
                low_case["hot_gas_side_wall_temperature"]
                - high_case["hot_gas_side_wall_temperature"]
            ),
            "d_twc_low_to_high": abs(
                low_case["coolant_side_wall_temperature"]
                - high_case["coolant_side_wall_temperature"]
            ),
        }

        consumption_pass = _perturbation_outputs_moved(perturbation)

        if not consumption_pass:
            blockers.append(
                "Changing material conductivity did not move the required thermal-chain outputs."
            )

    status = (
        "PASS_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER"
        if consumption_pass and not blockers
        else "FAIL_PHASE_10D2_MATERIAL_CONDUCTIVITY_CONSUMPTION_AUDIT_OWNER"
    )

    text = build_material_conductivity_consumption_audit_text(
        status=status,
        prerequisites=prerequisites,
        required_values=required_values,
        coating_resistance=coating_resistance,
        bond_resistance=bond_resistance,
        perturbation=perturbation,
        blockers=blockers,
    )

    return {
        "phase_10d2_material_conductivity_consumption_audit_owner_complete": True,
        "phase_10d2_material_conductivity_consumption_audit_owner_status": status,
        "phase_10d2_material_conductivity_consumption_audit_owner_pass": consumption_pass,
        "phase_10d2_material_conductivity_consumption_audit_owner_blockers": blockers,
        "phase_10d2_material_conductivity_consumption_audit_owner_perturbation": perturbation,
        "phase_10d2_material_conductivity_consumption_audit_owner_text": text,
        "stage_10d_material_conductivity_consumption_complete": consumption_pass,
        "stage_10d_material_conductivity_consumption_status": status,
    }


def _thermal_chain_case(
        k,
        wall_thickness,
        hg,
        hc,
        taw,
        tcool,
        coating_resistance=0.0,
        bond_resistance=0.0,
):
    gas_film_resistance = 1.0 / hg
    coolant_film_resistance = 1.0 / hc
    wall_resistance = wall_thickness / k

    total_resistance = (
        gas_film_resistance
        + coating_resistance
        + bond_resistance
        + wall_resistance
        + coolant_film_resistance
    )

    heat_flux = (taw - tcool) / total_resistance

    hot_gas_side_wall_temperature = (
        taw
        - heat_flux * gas_film_resistance
        - heat_flux * coating_resistance
        - heat_flux * bond_resistance
    )

    coolant_side_wall_temperature = tcool + heat_flux * coolant_film_resistance

    return {
        "material_thermal_conductivity": k,
        "gas_film_resistance": gas_film_resistance,
        "coating_resistance": coating_resistance,
        "bond_resistance": bond_resistance,
        "wall_resistance": wall_resistance,
        "coolant_film_resistance": coolant_film_resistance,
        "total_thermal_resistance": total_resistance,
        "heat_flux": heat_flux,
        "hot_gas_side_wall_temperature": hot_gas_side_wall_temperature,
        "coolant_side_wall_temperature": coolant_side_wall_temperature,
    }


def _perturbation_outputs_moved(perturbation):
    if not perturbation:
        return False

    return (
        perturbation["d_wall_resistance_low_to_high"] > 0.0
        and perturbation["d_heat_flux_low_to_high"] > 0.0
        and perturbation["d_twg_low_to_high"] > 0.0
        and perturbation["d_twc_low_to_high"] > 0.0
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
    evidence = results.get("phase_10d_verification_thermal_chain_evidence", {})

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


def build_material_conductivity_consumption_audit_text(
        status,
        prerequisites,
        required_values,
        coating_resistance,
        bond_resistance,
        perturbation,
        blockers,
):
    lines = []
    lines.append("PHASE 10D.2 — MATERIAL CONDUCTIVITY CONSUMPTION AUDIT OWNER")
    lines.append("============================================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Prove that material thermal conductivity k(T) changes the regen thermal chain.")
    lines.append("- Required affected outputs: wall resistance, heat flux, Twg, Twc.")
    lines.append("")
    lines.append("Prerequisites:")
    for key, value in prerequisites.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Required thermal-chain values:")
    for key, value in required_values.items():
        lines.append(f"- {key}: {value}")
    lines.append(f"- coating_resistance: {coating_resistance}")
    lines.append(f"- bond_resistance: {bond_resistance}")
    lines.append("")

    if perturbation:
        lines.append("Perturbation proof:")
        lines.append(f"- low_k: {perturbation['low_k']}")
        lines.append(f"- baseline_k: {perturbation['baseline_k']}")
        lines.append(f"- high_k: {perturbation['high_k']}")
        lines.append(
            f"- Δ wall resistance: {perturbation['d_wall_resistance_low_to_high']}"
        )
        lines.append(
            f"- Δ heat flux: {perturbation['d_heat_flux_low_to_high']}"
        )
        lines.append(
            f"- Δ hot-gas-side wall temperature: {perturbation['d_twg_low_to_high']}"
        )
        lines.append(
            f"- Δ coolant-side wall temperature: {perturbation['d_twc_low_to_high']}"
        )
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
        "PASS means material conductivity is mathematically active in the regen "
        "thermal-resistance pathway. FAIL means the solver foundation must be fixed "
        "before proceeding to Cp, density, coating, or bond-coat consumption audits."
    )

    return "\n".join(lines)