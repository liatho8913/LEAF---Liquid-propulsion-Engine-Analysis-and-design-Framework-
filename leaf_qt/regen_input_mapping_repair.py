"""
POST-16F.3 — Regen Input Mapping Repair

Purpose:
- Repair the bridge between solved/manual regen values and candidate generation.
- Does not change physics.
- Does not generate candidates by itself.
- Does not accept/reject geometry.
"""

import math


def _first_value(results, keys):
    for key in keys:
        value = results.get(key)
        if value is not None and value != "":
            return value
    return None


def _positive_float(value):
    try:
        value = float(value)
        if math.isfinite(value) and value > 0.0:
            return value
    except Exception:
        return None
    return None


def _nonnegative_float(value):
    try:
        value = float(value)
        if math.isfinite(value) and value >= 0.0:
            return value
    except Exception:
        return None
    return None


def _positive_int(value):
    try:
        value = int(float(value))
        if value > 0:
            return value
    except Exception:
        return None
    return None


def attach_regen_input_mapping_repair(results):
    if not isinstance(results, dict):
        return results

    mapped = {}
    missing = []

    channel_count = _positive_int(_first_value(results, [
        "number_of_coolant_channels",
        "coolant_channel_count",
        "channel_count",
        "manual_channel_count",
    ]))

    channel_width = _positive_float(_first_value(results, [
        "coolant_channel_width",
        "channel_width",
        "manual_channel_width",
    ]))

    channel_height = _positive_float(_first_value(results, [
        "coolant_channel_height",
        "channel_height",
        "manual_channel_height",
    ]))

    rib_width = _nonnegative_float(_first_value(results, [
        "rib_width",
        "requested_rib_width",
        "manual_rib_width",
    ]))

    wall_thickness = _positive_float(_first_value(results, [
        "hot_gas_wall_thickness",
        "minimum_wall_thickness",
        "pressure_required_wall_thickness",
        "conduction_required_wall_thickness",
    ]))

    coolant_flow_fraction = _positive_float(_first_value(results, [
        "coolant_mass_flow_fraction",
        "coolant_flow_fraction",
        "fuel_coolant_flow_fraction",
    ]))

    if coolant_flow_fraction is None:
        coolant_mass = _positive_float(results.get("coolant_mass_flow_rate"))
        total_mass = _positive_float(results.get("mass_flow_rate"))
        if coolant_mass is not None and total_mass is not None:
            coolant_flow_fraction = coolant_mass / total_mass

    channel_mid_radius = _positive_float(_first_value(results, [
        "channel_mid_radius",
        "regen_channel_mid_radius",
    ]))

    if channel_mid_radius is None:
        throat_radius = _positive_float(results.get("throat_radius"))
        wall = wall_thickness
        height = channel_height
        if throat_radius is not None and wall is not None and height is not None:
            channel_mid_radius = throat_radius + wall + 0.5 * height

    coolant_density = _positive_float(_first_value(results, [
        "coolant_density",
        "coolant_rho",
    ]))

    coolant_dynamic_viscosity = _positive_float(_first_value(results, [
        "coolant_dynamic_viscosity",
        "coolant_viscosity",
        "coolant_mu",
    ]))

    coolant_mass_flow_rate = _positive_float(_first_value(results, [
        "coolant_mass_flow_rate",
        "regen_coolant_mass_flow_rate",
    ]))

    if coolant_mass_flow_rate is None:
        total_mass = _positive_float(results.get("mass_flow_rate"))
        if total_mass is not None and coolant_flow_fraction is not None:
            coolant_mass_flow_rate = total_mass * coolant_flow_fraction

    values = {
        "number_of_coolant_channels": channel_count,
        "coolant_channel_width": channel_width,
        "coolant_channel_height": channel_height,
        "rib_width": rib_width,
        "hot_gas_wall_thickness": wall_thickness,
        "coolant_mass_flow_fraction": coolant_flow_fraction,
        "channel_mid_radius": channel_mid_radius,
        "coolant_density": coolant_density,
        "coolant_dynamic_viscosity": coolant_dynamic_viscosity,
        "coolant_mass_flow_rate": coolant_mass_flow_rate,
    }

    for key, value in values.items():
        if value is None:
            missing.append(key)
        else:
            mapped[key] = value
            results[key] = value

    complete = len(missing) == 0

    results["regen_input_mapping_repair_complete"] = True
    results["regen_input_mapping_repair_status"] = (
        "PASS_REGEN_INPUT_MAPPING_REPAIR_POST16F3"
        if complete else
        "PARTIAL_REGEN_INPUT_MAPPING_REPAIR_POST16F3"
    )
    results["regen_input_mapping_repair_mapped_values"] = mapped
    results["regen_input_mapping_repair_missing_keys"] = missing
    results["regen_input_mapping_repair_base_geometry_complete"] = complete

    if isinstance(results.get("regen_candidate_generator_base_geometry"), dict):
        base = dict(results["regen_candidate_generator_base_geometry"])
        base.update(mapped)
        base["base_geometry_complete"] = complete
        results["regen_candidate_generator_base_geometry"] = base

    return results
