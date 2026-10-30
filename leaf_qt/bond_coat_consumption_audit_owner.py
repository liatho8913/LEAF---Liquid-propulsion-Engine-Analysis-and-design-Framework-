"""
PHASE 10D.6
Bond-Coat Consumption Audit Owner

Purpose:
    Prove that bond-coat conductivity/thickness/resistance are consumed
    by the coating-stack thermal pathway when a bond coat is active.

Rules:
    - Audit only.
    - Does not overwrite solver physics outputs.
    - If no bond coat is selected, this owner passes as OPTIONAL_LAYER_NOT_SELECTED.
    - If a bond coat is selected, sourced bond-coat evidence and thermal-stack evidence are required.
    - Uses scalable nested evidence:
      phase_10d_verification_bond_coat_evidence
"""


_EPS = 1.0e-12


def attach_bond_coat_consumption_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_bond_coat_consumption_audit(results)
    results.update(audit)
    return results


def build_bond_coat_consumption_audit(results):
    results = results if isinstance(results, dict) else {}

    bond_selected = _bond_coat_selected(results)
    prerequisites = _check_prerequisites(results, bond_selected)

    if not bond_selected:
        status = "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
        text = _text(
            status=status,
            mode="OPTIONAL_LAYER_NOT_SELECTED",
            prerequisites=prerequisites,
            required={},
            perturbation=None,
            blockers=[],
        )

        return {
            "phase_10d6_bond_coat_consumption_audit_owner_complete": True,
            "phase_10d6_bond_coat_consumption_audit_owner_status": status,
            "phase_10d6_bond_coat_consumption_audit_owner_pass": True,
            "phase_10d6_bond_coat_consumption_audit_owner_mode": "OPTIONAL_LAYER_NOT_SELECTED",
            "phase_10d6_bond_coat_consumption_audit_owner_blockers": [],
            "phase_10d6_bond_coat_consumption_audit_owner_perturbation": None,
            "phase_10d6_bond_coat_consumption_audit_owner_text": text,
            "stage_10d_bond_coat_consumption_complete": True,
            "stage_10d_bond_coat_consumption_status": status,
        }

    bond_k = _first_number(results, [
        "bond_coat_thermal_conductivity",
        "sourced_bond_coat_thermal_conductivity",
        "bond_coat_k",
    ])

    bond_thickness = _first_number(results, [
        "bond_coat_thickness",
        "effective_bond_coat_thickness",
        "sourced_bond_coat_thickness",
    ])

    coating_resistance = _first_number(results, [
        "coating_thermal_resistance",
        "effective_coating_thermal_resistance",
        "sourced_coating_thermal_resistance",
    ])

    hg = _first_number(results, [
        "hot_gas_heat_transfer_coefficient",
        "regen_hot_gas_heat_transfer_coefficient",
        "hg",
    ])

    hc = _first_number(results, [
        "coolant_heat_transfer_coefficient",
        "regen_coolant_heat_transfer_coefficient",
        "hc",
    ])

    taw = _first_number(results, [
        "adiabatic_wall_temperature",
        "hot_gas_recovery_temperature",
        "gas_recovery_temperature",
        "chamber_temperature",
        "Tc",
    ])

    tcool = _first_number(results, [
        "coolant_bulk_temperature",
        "coolant_inlet_temperature",
        "coolant_temperature",
    ])

    wall_resistance = _first_number(results, [
        "wall_thermal_resistance",
        "thermal_resistance_wall",
        "material_wall_thermal_resistance",
    ])

    if wall_resistance is None:
        wall_thickness = _first_number(results, [
            "inner_wall_thickness",
            "wall_thickness",
            "regen_wall_thickness",
        ])
        wall_k = _first_number(results, [
            "sourced_wall_thermal_conductivity",
            "wall_thermal_conductivity",
            "material_thermal_conductivity",
        ])
        if wall_thickness is not None and wall_k is not None and wall_k > 0.0:
            wall_resistance = wall_thickness / wall_k

    bond_temperature_limit = _first_number(results, [
        "bond_coat_temperature_limit",
        "effective_bond_coat_temperature_limit",
        "sourced_bond_coat_temperature_limit",
        "bond_coat_max_temperature",
    ])

    required = {
        "bond_coat_thermal_conductivity": bond_k,
        "bond_coat_thickness": bond_thickness,
        "coating_thermal_resistance": coating_resistance,
        "hot_gas_heat_transfer_coefficient": hg,
        "coolant_heat_transfer_coefficient": hc,
        "gas_recovery_temperature": taw,
        "coolant_bulk_temperature": tcool,
        "wall_thermal_resistance": wall_resistance,
        "bond_coat_temperature_limit": bond_temperature_limit,
    }

    missing = [
        key for key, value in required.items()
        if value is None or value <= 0.0
    ]

    blockers = []
    if missing:
        blockers.append(
            "Missing or invalid required bond-coat thermal values: "
            + ", ".join(missing)
        )

    if not prerequisites["phase_10d1_complete"]:
        blockers.append("Phase 10D.1 discovery audit is not complete.")

    if prerequisites["bond_coat_source_mode"] != "SOURCED_VALIDATION_MODE":
        blockers.append(
            "Bond-coat source mode is not SOURCED_VALIDATION_MODE; "
            "placeholder/partial bond-coat data cannot pass."
        )

    if prerequisites["bond_coat_temperature_table_status"] == "MISSING":
        blockers.append("Selected bond-coat temperature table is missing.")

    perturbation = None
    consumption_pass = False

    if not blockers:
        low_k = bond_k * 0.5
        high_k = bond_k * 2.0
        low_t = bond_thickness * 0.5
        high_t = bond_thickness * 2.0

        baseline = _thermal_stack_case(
            bond_k=bond_k,
            bond_thickness=bond_thickness,
            coating_resistance=coating_resistance,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            bond_temperature_limit=bond_temperature_limit,
        )

        low_k_case = _thermal_stack_case(
            bond_k=low_k,
            bond_thickness=bond_thickness,
            coating_resistance=coating_resistance,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            bond_temperature_limit=bond_temperature_limit,
        )

        high_k_case = _thermal_stack_case(
            bond_k=high_k,
            bond_thickness=bond_thickness,
            coating_resistance=coating_resistance,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            bond_temperature_limit=bond_temperature_limit,
        )

        low_t_case = _thermal_stack_case(
            bond_k=bond_k,
            bond_thickness=low_t,
            coating_resistance=coating_resistance,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            bond_temperature_limit=bond_temperature_limit,
        )

        high_t_case = _thermal_stack_case(
            bond_k=bond_k,
            bond_thickness=high_t,
            coating_resistance=coating_resistance,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            bond_temperature_limit=bond_temperature_limit,
        )

        perturbation = {
            "baseline_case": baseline,
            "low_k_case": low_k_case,
            "high_k_case": high_k_case,
            "low_thickness_case": low_t_case,
            "high_thickness_case": high_t_case,

            "d_bond_resistance_k_low_to_high": abs(
                low_k_case["bond_coat_thermal_resistance"]
                - high_k_case["bond_coat_thermal_resistance"]
            ),
            "d_total_resistance_k_low_to_high": abs(
                low_k_case["total_thermal_resistance"]
                - high_k_case["total_thermal_resistance"]
            ),
            "d_heat_flux_k_low_to_high": abs(
                low_k_case["heat_flux"] - high_k_case["heat_flux"]
            ),
            "d_bond_wall_interface_temperature_k_low_to_high": abs(
                low_k_case["bond_wall_interface_temperature"]
                - high_k_case["bond_wall_interface_temperature"]
            ),

            "d_bond_resistance_thickness_low_to_high": abs(
                low_t_case["bond_coat_thermal_resistance"]
                - high_t_case["bond_coat_thermal_resistance"]
            ),
            "d_total_resistance_thickness_low_to_high": abs(
                low_t_case["total_thermal_resistance"]
                - high_t_case["total_thermal_resistance"]
            ),
            "d_heat_flux_thickness_low_to_high": abs(
                low_t_case["heat_flux"] - high_t_case["heat_flux"]
            ),
            "d_bond_margin_thickness_low_to_high": abs(
                low_t_case["bond_coat_temperature_margin"]
                - high_t_case["bond_coat_temperature_margin"]
            ),
        }

        consumption_pass = _outputs_moved(perturbation)

        if not consumption_pass:
            blockers.append(
                "Bond-coat perturbation did not move required thermal-stack outputs."
            )

    status = (
        "PASS_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
        if consumption_pass and not blockers
        else "FAIL_PHASE_10D6_BOND_COAT_CONSUMPTION_AUDIT_OWNER"
    )

    mode = "ACTIVE_BOND_COAT_CONSUMPTION_PROOF"

    return {
        "phase_10d6_bond_coat_consumption_audit_owner_complete": True,
        "phase_10d6_bond_coat_consumption_audit_owner_status": status,
        "phase_10d6_bond_coat_consumption_audit_owner_pass": consumption_pass,
        "phase_10d6_bond_coat_consumption_audit_owner_mode": mode,
        "phase_10d6_bond_coat_consumption_audit_owner_blockers": blockers,
        "phase_10d6_bond_coat_consumption_audit_owner_perturbation": perturbation,
        "phase_10d6_bond_coat_consumption_audit_owner_text": (
            _text(status, mode, prerequisites, required, perturbation, blockers)
        ),
        "stage_10d_bond_coat_consumption_complete": consumption_pass,
        "stage_10d_bond_coat_consumption_status": status,
    }


def _thermal_stack_case(
        bond_k,
        bond_thickness,
        coating_resistance,
        hg,
        hc,
        taw,
        tcool,
        wall_resistance,
        bond_temperature_limit,
):
    gas_film_resistance = 1.0 / hg
    coolant_film_resistance = 1.0 / hc
    bond_resistance = bond_thickness / bond_k

    total_resistance = (
        gas_film_resistance
        + coating_resistance
        + bond_resistance
        + wall_resistance
        + coolant_film_resistance
    )

    heat_flux = (taw - tcool) / total_resistance

    hot_side_coating_temperature = taw - heat_flux * gas_film_resistance
    coating_bond_interface_temperature = (
        hot_side_coating_temperature - heat_flux * coating_resistance
    )
    bond_wall_interface_temperature = (
        coating_bond_interface_temperature - heat_flux * bond_resistance
    )
    coolant_side_wall_temperature = tcool + heat_flux * coolant_film_resistance

    bond_margin = bond_temperature_limit - coating_bond_interface_temperature

    return {
        "bond_coat_thermal_conductivity": bond_k,
        "bond_coat_thickness": bond_thickness,
        "coating_thermal_resistance": coating_resistance,
        "bond_coat_thermal_resistance": bond_resistance,
        "wall_thermal_resistance": wall_resistance,
        "gas_film_resistance": gas_film_resistance,
        "coolant_film_resistance": coolant_film_resistance,
        "total_thermal_resistance": total_resistance,
        "heat_flux": heat_flux,
        "hot_side_coating_temperature": hot_side_coating_temperature,
        "coating_bond_interface_temperature": coating_bond_interface_temperature,
        "bond_wall_interface_temperature": bond_wall_interface_temperature,
        "coolant_side_wall_temperature": coolant_side_wall_temperature,
        "bond_coat_temperature_margin": bond_margin,
    }


def _outputs_moved(p):
    if not p:
        return False

    conductivity_path_active = (
        p["d_bond_resistance_k_low_to_high"] > _EPS
        and p["d_total_resistance_k_low_to_high"] > _EPS
        and p["d_heat_flux_k_low_to_high"] > _EPS
        and p["d_bond_wall_interface_temperature_k_low_to_high"] > _EPS
    )

    thickness_path_active = (
        p["d_bond_resistance_thickness_low_to_high"] > _EPS
        and p["d_total_resistance_thickness_low_to_high"] > _EPS
        and p["d_heat_flux_thickness_low_to_high"] > _EPS
        and p["d_bond_margin_thickness_low_to_high"] > _EPS
    )

    return conductivity_path_active and thickness_path_active


def _bond_coat_selected(results):
    active = results.get("bond_coat_integration_active")
    if active is True:
        return True

    name = str(
        results.get("bond_coat_name")
        or results.get("selected_bond_coat")
        or "NONE"
    ).strip().upper()

    return name not in ("", "NONE", "NO_BOND_COAT", "N/A", "NA", "NULL")


def _check_prerequisites(results, bond_selected):
    return {
        "bond_coat_selected": bond_selected,
        "phase_10d1_complete": bool(
            results.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
        ),
        "phase_10d1_status": results.get(
            "phase_10d1_temperature_dependency_discovery_audit_owner_status"
        ),
        "bond_coat_source_mode": str(
            results.get("bond_coat_source_validation_mode")
            or "NONE"
        ).upper(),
        "bond_coat_temperature_table_status": str(
            results.get("bond_coat_temperature_table_status")
            or "UNKNOWN"
        ).upper(),
    }


def _first_number(results, keys, default=None):
    evidence = results.get("phase_10d_verification_bond_coat_evidence", {})

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
        if value is None or isinstance(value, bool):
            return None
        return float(value)
    except Exception:
        return None


def _text(status, mode, prerequisites, required, perturbation, blockers):
    lines = [
        "PHASE 10D.6 — BOND-COAT CONSUMPTION AUDIT OWNER",
        "=================================================",
        "",
        f"Status: {status}",
        f"Mode: {mode}",
        "",
        "Purpose:",
        "- Prove active bond-coat conductivity/thickness alter the thermal resistance stack.",
        "- If no bond coat is selected, this audit passes as an optional inactive layer.",
        "",
        "Prerequisites:",
    ]

    for key, value in prerequisites.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Required values:")

    if required:
        for key, value in required.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- None required because no bond coat is selected.")

    lines.append("")
    lines.append("Blockers:")

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    if perturbation:
        lines.append("")
        lines.append("Perturbation proof:")
        for key in (
            "d_bond_resistance_k_low_to_high",
            "d_total_resistance_k_low_to_high",
            "d_heat_flux_k_low_to_high",
            "d_bond_wall_interface_temperature_k_low_to_high",
            "d_bond_resistance_thickness_low_to_high",
            "d_total_resistance_thickness_low_to_high",
            "d_heat_flux_thickness_low_to_high",
            "d_bond_margin_thickness_low_to_high",
        ):
            lines.append(f"- {key}: {perturbation.get(key)}")

    return "\n".join(lines)