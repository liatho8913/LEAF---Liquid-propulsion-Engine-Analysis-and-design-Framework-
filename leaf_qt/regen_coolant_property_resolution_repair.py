"""
POST-16F.5 — Coolant Property Resolution Repair

Purpose:
- Resolve missing coolant mass flow and basic coolant properties.
- Allow recommended geometry / candidate generation to receive usable coolant data.
- Does not change core regen physics.
- Does not generate or accept candidates directly.
"""

import math


DEFAULT_COOLANT_PROPERTIES = {
    "RP-1": {
        "density": 810.0,
        "dynamic_viscosity": 0.0016,
        "specific_heat_cp": 2100.0,
        "thermal_conductivity": 0.145,
        "inlet_temperature": 298.0,
    },
    "RP-1 / KEROSENE": {
        "density": 810.0,
        "dynamic_viscosity": 0.0016,
        "specific_heat_cp": 2100.0,
        "thermal_conductivity": 0.145,
        "inlet_temperature": 298.0,
    },
    "KEROSENE": {
        "density": 810.0,
        "dynamic_viscosity": 0.0016,
        "specific_heat_cp": 2100.0,
        "thermal_conductivity": 0.145,
        "inlet_temperature": 298.0,
    },
    "LOX": {
        "density": 1141.0,
        "dynamic_viscosity": 0.00020,
        "specific_heat_cp": 1700.0,
        "thermal_conductivity": 0.15,
        "inlet_temperature": 90.0,
    },
    "O2": {
        "density": 1141.0,
        "dynamic_viscosity": 0.00020,
        "specific_heat_cp": 1700.0,
        "thermal_conductivity": 0.15,
        "inlet_temperature": 90.0,
    },
    "METHANE": {
        "density": 422.0,
        "dynamic_viscosity": 0.00012,
        "specific_heat_cp": 3500.0,
        "thermal_conductivity": 0.20,
        "inlet_temperature": 111.0,
    },
    "CH4": {
        "density": 422.0,
        "dynamic_viscosity": 0.00012,
        "specific_heat_cp": 3500.0,
        "thermal_conductivity": 0.20,
        "inlet_temperature": 111.0,
    },
    "LH2": {
        "density": 70.8,
        "dynamic_viscosity": 0.000013,
        "specific_heat_cp": 9700.0,
        "thermal_conductivity": 0.10,
        "inlet_temperature": 20.0,
    },
    "HYDROGEN": {
        "density": 70.8,
        "dynamic_viscosity": 0.000013,
        "specific_heat_cp": 9700.0,
        "thermal_conductivity": 0.10,
        "inlet_temperature": 20.0,
    },
}


def _finite_positive(value):
    try:
        value = float(value)
        if math.isfinite(value) and value > 0.0:
            return value
    except Exception:
        return None
    return None


def _normalise_name(value):
    if value is None:
        return ""
    return str(value).strip().upper()


def _first_value(results, keys):
    for key in keys:
        value = results.get(key)
        if value is not None and value != "":
            return value
    return None


def _choose_coolant_name(results):
    for key in (
        "selected_coolant_name",
        "coolant_name",
        "fuel",
        "fuel_name",
        "selected_fuel_name",
    ):
        value = results.get(key)
        if value is not None and value != "":
            return str(value)
    return "RP-1 / Kerosene"


def _lookup_properties(name):
    n = _normalise_name(name)

    if n in DEFAULT_COOLANT_PROPERTIES:
        return DEFAULT_COOLANT_PROPERTIES[n]

    if "RP" in n or "KEROSENE" in n:
        return DEFAULT_COOLANT_PROPERTIES["RP-1 / KEROSENE"]

    if "METHANE" in n or "CH4" in n:
        return DEFAULT_COOLANT_PROPERTIES["CH4"]

    if "HYDROGEN" in n or "LH2" in n or "H2" in n:
        return DEFAULT_COOLANT_PROPERTIES["LH2"]

    if "LOX" in n or n == "O2" or "OXYGEN" in n:
        return DEFAULT_COOLANT_PROPERTIES["LOX"]

    return DEFAULT_COOLANT_PROPERTIES["RP-1 / KEROSENE"]


def attach_regen_coolant_property_resolution_repair(results):
    if not isinstance(results, dict):
        return results

    coolant_name = _choose_coolant_name(results)
    properties = _lookup_properties(coolant_name)

    mapped = {}
    warnings = []

    coolant_fraction = _finite_positive(_first_value(results, [
        "coolant_mass_flow_fraction",
        "coolant_flow_fraction",
        "fuel_coolant_flow_fraction",
    ]))

    if coolant_fraction is None:
        coolant_fraction = 0.35
        warnings.append("coolant_mass_flow_fraction defaulted to 0.35")

    total_mass_flow = _finite_positive(results.get("mass_flow_rate"))

    coolant_mass_flow_rate = _finite_positive(_first_value(results, [
        "coolant_mass_flow_rate",
        "regen_coolant_mass_flow_rate",
    ]))

    if coolant_mass_flow_rate is None and total_mass_flow is not None:
        coolant_mass_flow_rate = total_mass_flow * coolant_fraction

    coolant_density = _finite_positive(_first_value(results, [
        "coolant_density",
        "coolant_rho",
    ]))

    if coolant_density is None:
        coolant_density = properties["density"]
        warnings.append(f"coolant_density defaulted from {coolant_name}")

    coolant_dynamic_viscosity = _finite_positive(_first_value(results, [
        "coolant_dynamic_viscosity",
        "coolant_viscosity",
        "coolant_mu",
    ]))

    if coolant_dynamic_viscosity is None:
        coolant_dynamic_viscosity = properties["dynamic_viscosity"]
        warnings.append(f"coolant_dynamic_viscosity defaulted from {coolant_name}")

    coolant_specific_heat_cp = _finite_positive(_first_value(results, [
        "coolant_specific_heat_cp",
        "coolant_cp",
    ]))

    if coolant_specific_heat_cp is None:
        coolant_specific_heat_cp = properties["specific_heat_cp"]
        warnings.append(f"coolant_specific_heat_cp defaulted from {coolant_name}")

    coolant_thermal_conductivity = _finite_positive(_first_value(results, [
        "coolant_thermal_conductivity",
        "coolant_k",
    ]))

    if coolant_thermal_conductivity is None:
        coolant_thermal_conductivity = properties["thermal_conductivity"]
        warnings.append(f"coolant_thermal_conductivity defaulted from {coolant_name}")

    coolant_inlet_temperature = _finite_positive(_first_value(results, [
        "coolant_inlet_temperature",
        "fuel_temp_k",
        "coolant_temperature",
    ]))

    if coolant_inlet_temperature is None:
        coolant_inlet_temperature = properties["inlet_temperature"]
        warnings.append(f"coolant_inlet_temperature defaulted from {coolant_name}")

    values = {
        "selected_coolant_name": coolant_name,
        "coolant_mass_flow_fraction": coolant_fraction,
        "coolant_flow_fraction": coolant_fraction,
        "coolant_mass_flow_rate": coolant_mass_flow_rate,
        "coolant_density": coolant_density,
        "coolant_dynamic_viscosity": coolant_dynamic_viscosity,
        "coolant_specific_heat_cp": coolant_specific_heat_cp,
        "coolant_thermal_conductivity": coolant_thermal_conductivity,
        "coolant_inlet_temperature": coolant_inlet_temperature,
        "coolant_property_temperature": coolant_inlet_temperature,
        "coolant_bulk_temperature": coolant_inlet_temperature,
        "coolant_mean_temperature": coolant_inlet_temperature,
    }

    missing = []

    for key, value in values.items():
        if key == "selected_coolant_name":
            results[key] = value
            mapped[key] = value
            continue

        if _finite_positive(value) is None:
            missing.append(key)
        else:
            results[key] = value
            mapped[key] = value

    complete = len(missing) == 0

    results["regen_coolant_property_resolution_repair_complete"] = True
    results["regen_coolant_property_resolution_repair_status"] = (
        "PASS_REGEN_COOLANT_PROPERTY_RESOLUTION_REPAIR_POST16F5"
        if complete else
        "FAIL_REGEN_COOLANT_PROPERTY_RESOLUTION_REPAIR_POST16F5"
    )
    results["regen_coolant_property_resolution_repair_coolant_name"] = coolant_name
    results["regen_coolant_property_resolution_repair_mapped_values"] = mapped
    results["regen_coolant_property_resolution_repair_missing_keys"] = missing
    results["regen_coolant_property_resolution_repair_warnings"] = warnings

    if complete and results.get("recommended_geometry_status") == "BLOCKED_NO_COOLANT_FLOW":
        results["recommended_geometry_status_previous"] = "BLOCKED_NO_COOLANT_FLOW"
        results["recommended_geometry_status"] = "COOLANT_FLOW_RESOLVED_REQUIRES_REGEN_RECALC"
        results["recommended_geometry_reason"] = (
            "Coolant mass flow and coolant properties are now available. "
            "Recommended geometry requires a follow-up regen geometry calculation."
        )

    return results
