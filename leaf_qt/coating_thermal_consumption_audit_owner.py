"""
PHASE 10D.5
Coating Thermal Consumption Audit Owner

Purpose:
    Prove that coating thermal conductivity/thickness/resistance are consumed
    by the thermal resistance stack when a coating is selected.

Rules:
    - Audit only.
    - Does not overwrite solver physics outputs.
    - If no coating is selected, this owner passes as OPTIONAL_LAYER_NOT_SELECTED.
    - If a coating is selected, sourced coating data and thermal-stack evidence are required.
    - Uses scalable nested evidence:
      phase_10d_verification_coating_thermal_evidence
"""


_EPS = 1.0e-12


def attach_coating_thermal_consumption_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_coating_thermal_consumption_audit(results)
    results.update(audit)
    return results


def build_coating_thermal_consumption_audit(results):
    results = results if isinstance(results, dict) else {}

    coating_selected = _coating_selected(results)
    prerequisites = _check_prerequisites(results, coating_selected)

    if not coating_selected:
        status = "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
        text = _text(
            status=status,
            mode="OPTIONAL_LAYER_NOT_SELECTED",
            prerequisites=prerequisites,
            required={},
            perturbation=None,
            blockers=[],
        )
        return {
            "phase_10d5_coating_thermal_consumption_audit_owner_complete": True,
            "phase_10d5_coating_thermal_consumption_audit_owner_status": status,
            "phase_10d5_coating_thermal_consumption_audit_owner_pass": True,
            "phase_10d5_coating_thermal_consumption_audit_owner_mode": "OPTIONAL_LAYER_NOT_SELECTED",
            "phase_10d5_coating_thermal_consumption_audit_owner_blockers": [],
            "phase_10d5_coating_thermal_consumption_audit_owner_perturbation": None,
            "phase_10d5_coating_thermal_consumption_audit_owner_text": text,
            "stage_10d_coating_thermal_consumption_complete": True,
            "stage_10d_coating_thermal_consumption_status": status,
        }

    coating_k = _first_number(results, [
        "coating_thermal_conductivity",
        "sourced_coating_thermal_conductivity",
        "coating_k",
    ])

    coating_thickness = _first_number(results, [
        "effective_coating_thickness",
        "sourced_coating_thickness",
        "coating_thickness",
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
        if wall_thickness is not None and wall_k is not None and wall_k > 0:
            wall_resistance = wall_thickness / wall_k

    coating_temperature_limit = _first_number(results, [
        "effective_coating_temperature_limit",
        "coating_max_temperature",
        "sourced_coating_temperature_limit",
        "coating_temperature_limit",
    ])

    required = {
        "coating_thermal_conductivity": coating_k,
        "coating_thickness": coating_thickness,
        "hot_gas_heat_transfer_coefficient": hg,
        "coolant_heat_transfer_coefficient": hc,
        "gas_recovery_temperature": taw,
        "coolant_bulk_temperature": tcool,
        "wall_thermal_resistance": wall_resistance,
        "coating_temperature_limit": coating_temperature_limit,
    }

    blockers = [
        key for key, value in required.items()
        if value is None or value <= 0.0
    ]

    if blockers:
        blockers = ["Missing or invalid required coating thermal values: " + ", ".join(blockers)]
    else:
        blockers = []

    if not prerequisites["phase_10d1_complete"]:
        blockers.append("Phase 10D.1 discovery audit is not complete.")

    if prerequisites["coating_source_mode"] != "SOURCED_VALIDATION_MODE":
        blockers.append(
            "Coating source mode is not SOURCED_VALIDATION_MODE; "
            "placeholder/partial coating data cannot pass."
        )

    if prerequisites["coating_temperature_table_status"] == "MISSING":
        blockers.append("Selected coating temperature table is missing.")

    perturbation = None
    consumption_pass = False

    if not blockers:
        low_k = coating_k * 0.5
        high_k = coating_k * 2.0
        low_t = coating_thickness * 0.5
        high_t = coating_thickness * 2.0

        baseline = _thermal_stack_case(
            coating_k=coating_k,
            coating_thickness=coating_thickness,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            coating_temperature_limit=coating_temperature_limit,
        )

        low_k_case = _thermal_stack_case(
            coating_k=low_k,
            coating_thickness=coating_thickness,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            coating_temperature_limit=coating_temperature_limit,
        )

        high_k_case = _thermal_stack_case(
            coating_k=high_k,
            coating_thickness=coating_thickness,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            coating_temperature_limit=coating_temperature_limit,
        )

        low_t_case = _thermal_stack_case(
            coating_k=coating_k,
            coating_thickness=low_t,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            coating_temperature_limit=coating_temperature_limit,
        )

        high_t_case = _thermal_stack_case(
            coating_k=coating_k,
            coating_thickness=high_t,
            hg=hg,
            hc=hc,
            taw=taw,
            tcool=tcool,
            wall_resistance=wall_resistance,
            coating_temperature_limit=coating_temperature_limit,
        )

        perturbation = {
            "baseline_case": baseline,
            "low_k_case": low_k_case,
            "high_k_case": high_k_case,
            "low_thickness_case": low_t_case,
            "high_thickness_case": high_t_case,

            "d_coating_resistance_k_low_to_high": abs(
                low_k_case["coating_thermal_resistance"]
                - high_k_case["coating_thermal_resistance"]
            ),
            "d_total_resistance_k_low_to_high": abs(
                low_k_case["total_thermal_resistance"]
                - high_k_case["total_thermal_resistance"]
            ),
            "d_heat_flux_k_low_to_high": abs(
                low_k_case["heat_flux"] - high_k_case["heat_flux"]
            ),
            "d_protected_wall_temperature_k_low_to_high": abs(
                low_k_case["protected_wall_temperature"]
                - high_k_case["protected_wall_temperature"]
            ),

            "d_coating_resistance_thickness_low_to_high": abs(
                low_t_case["coating_thermal_resistance"]
                - high_t_case["coating_thermal_resistance"]
            ),
            "d_total_resistance_thickness_low_to_high": abs(
                low_t_case["total_thermal_resistance"]
                - high_t_case["total_thermal_resistance"]
            ),
            "d_heat_flux_thickness_low_to_high": abs(
                low_t_case["heat_flux"] - high_t_case["heat_flux"]
            ),
            "d_coating_margin_thickness_low_to_high": abs(
                low_t_case["coating_temperature_margin"]
                - high_t_case["coating_temperature_margin"]
            ),
        }

        consumption_pass = _outputs_moved(perturbation)

        if not consumption_pass:
            blockers.append(
                "Coating perturbation did not move the required thermal-stack outputs."
            )

    status = (
        "PASS_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
        if consumption_pass and not blockers
        else "FAIL_PHASE_10D5_COATING_THERMAL_CONSUMPTION_AUDIT_OWNER"
    )

    mode = "ACTIVE_COATING_CONSUMPTION_PROOF"

    return {
        "phase_10d5_coating_thermal_consumption_audit_owner_complete": True,
        "phase_10d5_coating_thermal_consumption_audit_owner_status": status,
        "phase_10d5_coating_thermal_consumption_audit_owner_pass": consumption_pass,
        "phase_10d5_coating_thermal_consumption_audit_owner_mode": mode,
        "phase_10d5_coating_thermal_consumption_audit_owner_blockers": blockers,
        "phase_10d5_coating_thermal_consumption_audit_owner_perturbation": perturbation,
        "phase_10d5_coating_thermal_consumption_audit_owner_text": (
            _text(status, mode, prerequisites, required, perturbation, blockers)
        ),
        "stage_10d_coating_thermal_consumption_complete": consumption_pass,
        "stage_10d_coating_thermal_consumption_status": status,
    }


def _thermal_stack_case(
        coating_k,
        coating_thickness,
        hg,
        hc,
        taw,
        tcool,
        wall_resistance,
        coating_temperature_limit,
):
    gas_film_resistance = 1.0 / hg
    coolant_film_resistance = 1.0 / hc
    coating_resistance = coating_thickness / coating_k

    total_resistance = (
        gas_film_resistance
        + coating_resistance
        + wall_resistance
        + coolant_film_resistance
    )

    heat_flux = (taw - tcool) / total_resistance

    hot_side_coating_temperature = taw - heat_flux * gas_film_resistance
    protected_wall_temperature = hot_side_coating_temperature - heat_flux * coating_resistance
    coolant_side_wall_temperature = tcool + heat_flux * coolant_film_resistance

    coating_temperature_margin = coating_temperature_limit - hot_side_coating_temperature

    return {
        "coating_thermal_conductivity": coating_k,
        "coating_thickness": coating_thickness,
        "coating_thermal_resistance": coating_resistance,
        "gas_film_resistance": gas_film_resistance,
        "wall_thermal_resistance": wall_resistance,
        "coolant_film_resistance": coolant_film_resistance,
        "total_thermal_resistance": total_resistance,
        "heat_flux": heat_flux,
        "hot_side_coating_temperature": hot_side_coating_temperature,
        "protected_wall_temperature": protected_wall_temperature,
        "coolant_side_wall_temperature": coolant_side_wall_temperature,
        "coating_temperature_margin": coating_temperature_margin,
    }


def _outputs_moved(p):
    if not p:
        return False

    conductivity_path_active = (
        p["d_coating_resistance_k_low_to_high"] > _EPS
        and p["d_total_resistance_k_low_to_high"] > _EPS
        and p["d_heat_flux_k_low_to_high"] > _EPS
        and p["d_protected_wall_temperature_k_low_to_high"] > _EPS
    )

    thickness_path_active = (
        p["d_coating_resistance_thickness_low_to_high"] > _EPS
        and p["d_total_resistance_thickness_low_to_high"] > _EPS
        and p["d_heat_flux_thickness_low_to_high"] > _EPS
        and p["d_coating_margin_thickness_low_to_high"] > _EPS
    )

    return conductivity_path_active and thickness_path_active


def _coating_selected(results):
    name = str(
        results.get("coating_name")
        or results.get("selected_coating")
        or "NONE"
    ).strip().upper()

    return name not in ("", "NONE", "NO_COATING", "N/A", "NA", "NULL")


def _check_prerequisites(results, coating_selected):
    return {
        "coating_selected": coating_selected,
        "phase_10d1_complete": bool(
            results.get("phase_10d1_temperature_dependency_discovery_audit_owner_complete")
        ),
        "phase_10d1_status": results.get(
            "phase_10d1_temperature_dependency_discovery_audit_owner_status"
        ),
        "coating_source_mode": str(
            results.get("coating_source_validation_mode")
            or "NONE"
        ).upper(),
        "coating_temperature_table_status": str(
            results.get("coating_temperature_table_status")
            or "UNKNOWN"
        ).upper(),
    }


def _first_number(results, keys, default=None):
    evidence = results.get("phase_10d_verification_coating_thermal_evidence", {})

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
        "PHASE 10D.5 — COATING THERMAL CONSUMPTION AUDIT OWNER",
        "=======================================================",
        "",
        f"Status: {status}",
        f"Mode: {mode}",
        "",
        "Purpose:",
        "- Prove active coating conductivity/thickness alter the thermal resistance stack.",
        "- If no coating is selected, this audit passes as an optional inactive layer.",
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
        lines.append("- None required because no coating is selected.")

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
            "d_coating_resistance_k_low_to_high",
            "d_total_resistance_k_low_to_high",
            "d_heat_flux_k_low_to_high",
            "d_protected_wall_temperature_k_low_to_high",
            "d_coating_resistance_thickness_low_to_high",
            "d_total_resistance_thickness_low_to_high",
            "d_heat_flux_thickness_low_to_high",
            "d_coating_margin_thickness_low_to_high",
        ):
            lines.append(f"- {key}: {perturbation.get(key)}")

    return "\n".join(lines)