"""
LEAF Regen Scalability Constraint Owner
=======================================

Stage V.1 owner for scalability constraint logic.

This layer must not be stricter than Stage U for normal foundation verification.
It blocks only explicit scalability failures.

Missing optional visibility is reported as evidence/review information, not as
a hard Stage V failure.
"""
import math

from regen_scalability_profile import classify_engine_scale


VALUE_ALIASES = {
    "chamber_pressure": (
        "chamber_pressure",
        "Pc",
        "pc",
        "p_c",
    ),
    "mass_flow_rate": (
        "mass_flow_rate",
        "mdot",
        "m_dot",
        "mass_flow",
    ),
    "throat_area": (
        "throat_area",
        "At",
        "a_t",
        "throat_area_m2",
    ),
    "regen_coolant_velocity": (
        "regen_coolant_velocity",
        "coolant_velocity",
        "coolant_velocity_m_s",
        "mean_coolant_velocity",
    ),
    "regen_pressure_drop": (
        "regen_pressure_drop",
        "pressure_drop",
        "coolant_pressure_drop",
        "delta_p_coolant",
    ),
    "regen_heat_flux": (
        "regen_heat_flux",
        "heat_flux",
        "hot_gas_heat_flux",
        "wall_heat_flux",
    ),
    "hot_gas_side_wall_temperature": (
        "hot_gas_side_wall_temperature",
        "wall_temperature",
        "hot_wall_temperature",
        "T_wall_hot",
    ),
}


def attach_regen_scalability_constraint_owner(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_regen_scalability_constraints(results)
    results.update(audit)
    return results


def evaluate_regen_scalability_constraints(results):
    results = results if isinstance(results, dict) else {}

    scale_class = (
        results.get("regen_scalability_profile_scale_class")
        or classify_engine_scale(results)
    )

    values = build_value_snapshot(results)

    blocking_reasons = []
    warning_reasons = []
    evidence = []

    if not results.get("stage_v0_regen_scalability_profile_complete", False):
        blocking_reasons.append(
            "Stage V.0 scalability profile is incomplete."
        )

    if not results.get("stage_u_regen_validation_complete", False):
        blocking_reasons.append(
            "Stage U regen validation is incomplete."
        )

    warning_reasons.extend(
        evaluate_explicit_scalability_warnings(values)
    )

    missing_inputs = [
        key for key, value in values.items()
        if value is None
    ]

    if missing_inputs:
        evidence.append(
            "Some scalability visibility values are missing, but Stage U remains the primary trust gate."
        )

    if not blocking_reasons and not warning_reasons:
        status = "PASS_REGEN_SCALABILITY_CONSTRAINT_OWNER"
        complete = True
    elif blocking_reasons:
        status = "FAIL_REGEN_SCALABILITY_CONSTRAINT_OWNER"
        complete = False
    else:
        status = "WARN_REGEN_SCALABILITY_CONSTRAINT_OWNER_REVIEW_REQUIRED"
        complete = False

    text = build_text(
        status=status,
        complete=complete,
        scale_class=scale_class,
        values=values,
        missing_inputs=missing_inputs,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        evidence=evidence,
        results=results,
    )

    return {
        "regen_scalability_constraint_owner_status": status,
        "regen_scalability_constraint_owner_complete": complete,
        "regen_scalability_constraint_owner_engine_class": scale_class,
        "regen_scalability_constraint_owner_values": values,
        "regen_scalability_constraint_owner_missing_inputs": missing_inputs,
        "regen_scalability_constraint_owner_blocking_reasons": blocking_reasons,
        "regen_scalability_constraint_owner_warning_reasons": warning_reasons,
        "regen_scalability_constraint_owner_evidence": evidence,
        "regen_scalability_constraint_owner_text": text,

        "regen_scalability_framework_status": status,
        "regen_scalability_framework_pass_allowed": complete,
        "regen_scalability_engine_class": scale_class,
        "regen_scalability_blocking_reasons": blocking_reasons,
        "regen_scalability_warning_reasons": warning_reasons,
        "regen_scalability_text": text,
        "stage_v1_regen_scalability_framework_complete": complete,
        "stage_v1_regen_scalability_constraint_owner_complete": complete,
    }


def build_value_snapshot(results):
    return {
        canonical_key: _lookup_number(results, aliases)
        for canonical_key, aliases in VALUE_ALIASES.items()
    }


def evaluate_explicit_scalability_warnings(values):
    warnings = []

    if not isinstance(values, dict):
        return [
            "Scalability warning input container is invalid; expected a dictionary."
        ]

    def valid_numeric(name, value):
        if value is None:
            return False

        try:
            finite = math.isfinite(value)
        except (TypeError, ValueError):
            warnings.append(
                f"Invalid or non-finite numeric value for {name}."
            )
            return False

        if not finite:
            warnings.append(
                f"Invalid or non-finite numeric value for {name}."
            )
            return False

        return True

    coolant_velocity = values.get("regen_coolant_velocity")
    chamber_pressure = values.get("chamber_pressure")
    mass_flow_rate = values.get("mass_flow_rate")
    throat_area = values.get("throat_area")
    pressure_drop = values.get("regen_pressure_drop")
    heat_flux = values.get("regen_heat_flux")
    wall_temperature = values.get("hot_gas_side_wall_temperature")

    if chamber_pressure is not None:
        if valid_numeric("chamber_pressure", chamber_pressure):
            if chamber_pressure <= 0:
                warnings.append("Chamber pressure is non-positive.")

    if mass_flow_rate is not None:
        if valid_numeric("mass_flow_rate", mass_flow_rate):
            if mass_flow_rate <= 0:
                warnings.append("Mass flow rate is non-positive.")

    if throat_area is not None:
        if valid_numeric("throat_area", throat_area):
            if throat_area <= 0:
                warnings.append("Throat area is non-positive.")

    if coolant_velocity is not None:
        if valid_numeric("regen_coolant_velocity", coolant_velocity):
            if coolant_velocity <= 0:
                warnings.append("Coolant velocity is non-positive.")
            elif coolant_velocity < 2:
                warnings.append(
                    "Coolant velocity may be too low for scalable regen cooling."
                )
            elif coolant_velocity > 80:
                warnings.append(
                    "Coolant velocity is very high and may cause excessive pressure loss."
                )

    if pressure_drop is not None:
        if valid_numeric("regen_pressure_drop", pressure_drop):
            if pressure_drop < 0:
                warnings.append("Regen pressure drop is negative.")

    if heat_flux is not None:
        if valid_numeric("regen_heat_flux", heat_flux):
            if heat_flux <= 0:
                warnings.append("Regen heat flux is non-positive.")

    if wall_temperature is not None:
        if valid_numeric("hot_gas_side_wall_temperature", wall_temperature):
            if wall_temperature <= 0:
                warnings.append(
                    "Hot-gas-side wall temperature is non-positive."
                )

    return warnings


def build_text(
    status,
    complete,
    scale_class,
    values,
    missing_inputs,
    blocking_reasons,
    warning_reasons,
    evidence,
    results,
):
    lines = [
        "LEAF STAGE V.1 REGEN SCALABILITY CONSTRAINT OWNER",
        "====================================================",
        "",
        f"Status: {status}",
        f"Complete: {complete}",
        f"Engine scale class: {scale_class}",
        "",
        "Owned By:",
        "- regen_scalability_constraint_owner.py",
        "",
        "Rule:",
        "- Stage V.1 blocks explicit scalability failures.",
        "- Stage U remains the primary regen validation trust gate.",
        "- Missing optional visibility is recorded but does not alone fail Stage V.",
        "",
        "Required Architecture:",
        f"- Stage U complete: {results.get('stage_u_regen_validation_complete', False)}",
        f"- Stage V.0 profile complete: {results.get('stage_v0_regen_scalability_profile_complete', False)}",
        "",
        "Values:",
    ]

    for key, value in values.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Missing Inputs:")
    lines.extend([f"- {item}" for item in missing_inputs] or ["- None."])

    lines.append("")
    lines.append("Blocking Reasons:")
    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Warning Reasons:")
    lines.extend([f"- {item}" for item in warning_reasons] or ["- None."])

    lines.append("")
    lines.append("Evidence:")
    lines.extend([f"- {item}" for item in evidence] or ["- None."])

    return "\n".join(lines)


def _lookup_number(results, aliases):
    for key in aliases:
        if key in results:
            value = _number(results.get(key))
            if value is not None:
                return value

    return None


def _number(value):
    try:
        return float(value)
    except Exception:
        return None