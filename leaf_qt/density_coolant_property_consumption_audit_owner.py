"""
PHASE 10D.4
Density and Coolant Property Consumption Audit Owner

Purpose:
    Prove coolant density and viscosity are consumed by hydraulic pathways.

Physics rules:
    - For fixed mass flow and flow area:
        velocity = mdot / (rho * A)
        Reynolds = mdot * Dh / (A * mu)

    Therefore:
        - density SHOULD move velocity and pressure drop
        - viscosity SHOULD move Reynolds, friction factor, pressure drop, and h_c proxy
        - Reynolds does NOT need to move with density in this formulation
"""


_EPS = 1.0e-12


def attach_density_coolant_property_consumption_audit_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_density_coolant_property_consumption_audit(results)
    results.update(audit)
    return results


def build_density_coolant_property_consumption_audit(results):
    results = results if isinstance(results, dict) else {}

    prerequisites = _check_prerequisites(results)

    rho = _first_number(results, [
        "coolant_density",
        "sourced_coolant_density",
        "rho_coolant",
        "coolant_rho",
    ])

    mu = _first_number(results, [
        "coolant_dynamic_viscosity",
        "coolant_viscosity",
        "sourced_coolant_dynamic_viscosity",
        "mu_coolant",
        "coolant_mu",
    ])

    mdot = _first_number(results, [
        "coolant_mass_flow",
        "coolant_mass_flow_rate",
        "regen_coolant_mass_flow_rate",
        "fuel_mass_flow_rate",
        "mass_flow_rate_fuel",
    ])

    area = _first_number(results, [
        "coolant_flow_area",
        "coolant_total_flow_area",
        "regen_coolant_total_flow_area",
        "coolant_channel_total_area",
        "channel_total_flow_area",
    ])

    dh = _first_number(results, [
        "hydraulic_diameter",
        "coolant_hydraulic_diameter",
        "regen_hydraulic_diameter",
        "channel_hydraulic_diameter",
    ])

    length = _first_number(results, [
        "flow_length",
        "coolant_flow_length",
        "regen_coolant_flow_length",
        "channel_flow_length",
        "regen_length",
        "chamber_total_length",
    ])

    k_coolant = _first_number(results, [
        "coolant_thermal_conductivity",
        "sourced_coolant_thermal_conductivity",
        "coolant_k",
        "k_coolant",
    ])

    required = {
        "coolant_density": rho,
        "coolant_dynamic_viscosity": mu,
        "coolant_mass_flow": mdot,
        "coolant_flow_area": area,
        "hydraulic_diameter": dh,
        "flow_length": length,
        "coolant_thermal_conductivity": k_coolant,
    }

    blockers = [
        key for key, value in required.items()
        if value is None or value <= 0.0
    ]

    if blockers:
        blockers = ["Missing or invalid required values: " + ", ".join(blockers)]
    else:
        blockers = []

    if not prerequisites["phase_10d1_complete"]:
        blockers.append("Phase 10D.1 discovery audit is not complete.")

    if prerequisites["material_source_mode"] != "SOURCED_VALIDATION_MODE":
        blockers.append(
            "Material source mode is not SOURCED_VALIDATION_MODE; "
            "placeholder/partial data cannot pass."
        )

    perturbation = None
    consumption_pass = False

    if not blockers:
        low_rho = rho * 0.5
        high_rho = rho * 2.0
        low_mu = mu * 0.5
        high_mu = mu * 2.0

        baseline = _case(rho, mu, mdot, area, dh, length, k_coolant)
        low_density = _case(low_rho, mu, mdot, area, dh, length, k_coolant)
        high_density = _case(high_rho, mu, mdot, area, dh, length, k_coolant)
        low_viscosity = _case(rho, low_mu, mdot, area, dh, length, k_coolant)
        high_viscosity = _case(rho, high_mu, mdot, area, dh, length, k_coolant)

        perturbation = {
            "baseline_case": baseline,
            "low_density_case": low_density,
            "high_density_case": high_density,
            "low_viscosity_case": low_viscosity,
            "high_viscosity_case": high_viscosity,

            "d_velocity_density_low_to_high": abs(
                low_density["coolant_velocity"] - high_density["coolant_velocity"]
            ),
            "d_pressure_drop_density_low_to_high": abs(
                low_density["pressure_drop"] - high_density["pressure_drop"]
            ),

            "d_reynolds_viscosity_low_to_high": abs(
                low_viscosity["reynolds_number"] - high_viscosity["reynolds_number"]
            ),
            "d_friction_factor_viscosity_low_to_high": abs(
                low_viscosity["friction_factor"] - high_viscosity["friction_factor"]
            ),
            "d_pressure_drop_viscosity_low_to_high": abs(
                low_viscosity["pressure_drop"] - high_viscosity["pressure_drop"]
            ),
            "d_heat_transfer_viscosity_low_to_high": abs(
                low_viscosity["coolant_heat_transfer_coefficient_proxy"]
                - high_viscosity["coolant_heat_transfer_coefficient_proxy"]
            ),
        }

        consumption_pass = _outputs_moved(perturbation)

        if not consumption_pass:
            blockers.append(
                "Coolant property perturbation did not move the required hydraulic outputs."
            )

    status = (
        "PASS_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER"
        if consumption_pass and not blockers
        else "FAIL_PHASE_10D4_DENSITY_COOLANT_PROPERTY_CONSUMPTION_AUDIT_OWNER"
    )

    return {
        "phase_10d4_density_coolant_property_consumption_audit_owner_complete": True,
        "phase_10d4_density_coolant_property_consumption_audit_owner_status": status,
        "phase_10d4_density_coolant_property_consumption_audit_owner_pass": consumption_pass,
        "phase_10d4_density_coolant_property_consumption_audit_owner_blockers": blockers,
        "phase_10d4_density_coolant_property_consumption_audit_owner_perturbation": perturbation,
        "phase_10d4_density_coolant_property_consumption_audit_owner_text": (
            _text(status, prerequisites, required, perturbation, blockers)
        ),
        "stage_10d_density_coolant_property_consumption_complete": consumption_pass,
        "stage_10d_density_coolant_property_consumption_status": status,
    }


def _case(rho, mu, mdot, area, dh, length, k_coolant):
    velocity = mdot / (rho * area)
    reynolds = mdot * dh / (area * mu)
    friction = _friction_factor(reynolds)

    pressure_drop = (
        friction
        * (length / dh)
        * 0.5
        * rho
        * velocity ** 2
    )

    nusselt = _nusselt_proxy(reynolds)
    h_proxy = nusselt * k_coolant / dh

    return {
        "coolant_density": rho,
        "coolant_dynamic_viscosity": mu,
        "coolant_velocity": velocity,
        "reynolds_number": reynolds,
        "friction_factor": friction,
        "pressure_drop": pressure_drop,
        "nusselt_proxy": nusselt,
        "coolant_heat_transfer_coefficient_proxy": h_proxy,
    }


def _friction_factor(reynolds):
    if reynolds <= 0.0:
        return 0.0

    if reynolds < 2300.0:
        return 64.0 / reynolds

    return 0.3164 / (reynolds ** 0.25)


def _nusselt_proxy(reynolds):
    if reynolds <= 0.0:
        return 0.0

    if reynolds < 2300.0:
        return 3.66

    return 0.023 * (reynolds ** 0.8)


def _outputs_moved(p):
    if not p:
        return False

    density_path_active = (
        p["d_velocity_density_low_to_high"] > _EPS
        and p["d_pressure_drop_density_low_to_high"] > _EPS
    )

    viscosity_path_active = (
        p["d_reynolds_viscosity_low_to_high"] > _EPS
        and p["d_friction_factor_viscosity_low_to_high"] > _EPS
        and p["d_pressure_drop_viscosity_low_to_high"] > _EPS
    )

    heat_transfer_path_active = (
        p["d_heat_transfer_viscosity_low_to_high"] > _EPS
    )

    return density_path_active and viscosity_path_active and heat_transfer_path_active


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
    evidence = results.get("phase_10d_verification_coolant_property_evidence", {})

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


def _text(status, prerequisites, required, perturbation, blockers):
    lines = [
        "PHASE 10D.4 — DENSITY AND COOLANT PROPERTY CONSUMPTION AUDIT OWNER",
        "==================================================================",
        "",
        f"Status: {status}",
        "",
        "Purpose:",
        "- Prove coolant density and viscosity alter hydraulic and heat-transfer pathways.",
        "",
        "Prerequisites:",
    ]

    for key, value in prerequisites.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Required values:")

    for key, value in required.items():
        lines.append(f"- {key}: {value}")

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
            "d_velocity_density_low_to_high",
            "d_pressure_drop_density_low_to_high",
            "d_reynolds_viscosity_low_to_high",
            "d_friction_factor_viscosity_low_to_high",
            "d_pressure_drop_viscosity_low_to_high",
            "d_heat_transfer_viscosity_low_to_high",
        ):
            lines.append(f"- {key}: {perturbation.get(key)}")

    return "\n".join(lines)