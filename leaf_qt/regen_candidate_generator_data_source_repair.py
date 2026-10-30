"""
PHASE 16J.3A — Candidate Generator Data Source Repair

Purpose:
- Repair the data source chain feeding regen_candidate_generator.py.
- Ensure manual regen geometry, coolant fraction, coolant properties, coolant flow,
  and channel radius are exposed under the keys expected by candidate generation.
- Does not generate candidates itself.
- Does not score, rank, mutate, accept, reject, or commit geometry.
"""

import math


DEFAULT_COOLANT_PROPERTIES = {
    "RP-1": {
        "density": 810.0,
        "dynamic_viscosity": 0.0016,
    },
    "KEROSENE": {
        "density": 810.0,
        "dynamic_viscosity": 0.0016,
    },
    "LOX": {
        "density": 1141.0,
        "dynamic_viscosity": 0.00020,
    },
    "METHANE": {
        "density": 422.0,
        "dynamic_viscosity": 0.00012,
    },
    "CH4": {
        "density": 422.0,
        "dynamic_viscosity": 0.00012,
    },
    "LH2": {
        "density": 70.8,
        "dynamic_viscosity": 0.000013,
    },
    "HYDROGEN": {
        "density": 70.8,
        "dynamic_viscosity": 0.000013,
    },
}


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


def _coolant_defaults(name):
    name_u = str(name or "").upper()

    if "RP" in name_u or "KEROSENE" in name_u:
        return DEFAULT_COOLANT_PROPERTIES["RP-1"]
    if "LOX" in name_u or "OXYGEN" in name_u:
        return DEFAULT_COOLANT_PROPERTIES["LOX"]
    if "METHANE" in name_u or "CH4" in name_u:
        return DEFAULT_COOLANT_PROPERTIES["CH4"]
    if "LH2" in name_u or "HYDROGEN" in name_u or name_u == "H2":
        return DEFAULT_COOLANT_PROPERTIES["LH2"]

    return DEFAULT_COOLANT_PROPERTIES["RP-1"]


def _radius_from_area(area):
    area = _positive(area)
    if area is None:
        return None
    return math.sqrt(area / math.pi)


def _derive_channel_mid_radius(results):
    existing = _first_positive(results, [
        "channel_mid_radius",
        "regen_channel_mid_radius",
        "recommended_tightest_gas_radius",
    ])
    if existing is not None:
        return existing

    throat_radius = _first_positive(results, ["throat_radius"])
    exit_radius = _first_positive(results, ["exit_radius"])

    if throat_radius is None:
        throat_radius = _radius_from_area(results.get("throat_area"))

    if exit_radius is None:
        exit_area = results.get("exit_area")
        if _positive(exit_area) is None:
            throat_area = _positive(results.get("throat_area"))
            expansion_ratio = _positive(results.get("expansion_ratio"))
            if throat_area is not None and expansion_ratio is not None:
                exit_area = throat_area * expansion_ratio
        exit_radius = _radius_from_area(exit_area)

    wall = _first_positive(results, ["hot_gas_wall_thickness"])
    channel_height = _first_positive(results, ["coolant_channel_height"])

    if throat_radius is not None:
        offset = 0.0
        if wall is not None:
            offset += wall
        if channel_height is not None:
            offset += 0.5 * channel_height
        return throat_radius + offset

    if exit_radius is not None:
        return exit_radius

    profile = results.get("rao_nozzle_profile")
    if isinstance(profile, list) and profile:
        radii = []
        for station in profile:
            if isinstance(station, dict):
                radius = _positive(station.get("radius"))
                if radius is not None:
                    radii.append(radius)
        if radii:
            return min(radii)

    return None


def attach_regen_candidate_generator_data_source_repair(results):
    if not isinstance(results, dict):
        return results

    coolant_name = _first_text(results, [
        "selected_coolant_name",
        "coolant_name",
        "fuel_name",
        "fuel",
    ]) or "RP-1"

    defaults = _coolant_defaults(coolant_name)

    coolant_fraction = _first_positive(results, [
        "coolant_mass_flow_fraction",
        "coolant_flow_fraction",
        "fuel_coolant_flow_fraction",
    ])
    if coolant_fraction is None:
        coolant_fraction = 0.35

    fuel_mass_flow = _first_positive(results, ["fuel_mass_flow_rate"])
    total_mass_flow = _first_positive(results, ["mass_flow_rate", "total_mass_flow_rate"])

    coolant_mass_flow_rate = _first_positive(results, [
        "coolant_mass_flow_rate",
        "regen_coolant_mass_flow_rate",
    ])

    if coolant_mass_flow_rate is None and fuel_mass_flow is not None:
        coolant_mass_flow_rate = fuel_mass_flow * coolant_fraction
    elif coolant_mass_flow_rate is None and total_mass_flow is not None:
        coolant_mass_flow_rate = total_mass_flow * coolant_fraction

    coolant_density = _first_positive(results, ["coolant_density", "coolant_rho"])
    if coolant_density is None:
        coolant_density = defaults["density"]

    coolant_dynamic_viscosity = _first_positive(results, [
        "coolant_dynamic_viscosity",
        "coolant_viscosity",
        "coolant_mu",
    ])
    if coolant_dynamic_viscosity is None:
        coolant_dynamic_viscosity = defaults["dynamic_viscosity"]

    channel_mid_radius = _derive_channel_mid_radius(results)

    mapped = {
        "number_of_coolant_channels": _first_positive(results, [
            "number_of_coolant_channels",
            "coolant_channel_count",
            "channel_count",
        ]),
        "coolant_channel_width": _first_positive(results, [
            "coolant_channel_width",
            "channel_width",
        ]),
        "coolant_channel_height": _first_positive(results, [
            "coolant_channel_height",
            "channel_height",
        ]),
        "rib_width": _first_positive(results, [
            "rib_width",
            "coolant_rib_width",
        ]),
        "hot_gas_wall_thickness": _first_positive(results, [
            "hot_gas_wall_thickness",
            "wall_thickness",
            "liner_wall_thickness",
        ]),
        "coolant_mass_flow_fraction": coolant_fraction,
        "coolant_flow_fraction": coolant_fraction,
        "channel_mid_radius": channel_mid_radius,
        "coolant_density": coolant_density,
        "coolant_dynamic_viscosity": coolant_dynamic_viscosity,
        "coolant_mass_flow_rate": coolant_mass_flow_rate,
    }

    missing = []

    for key, value in mapped.items():
        if _positive(value) is None:
            missing.append(key)
        else:
            results[key] = value

    results["selected_coolant_name"] = coolant_name

    if coolant_mass_flow_rate is not None:
        results["regen_coolant_mass_flow_rate"] = coolant_mass_flow_rate

    complete = len(missing) == 0

    results["regen_candidate_generator_data_source_repair_complete"] = True
    results["phase_16j3a_complete"] = True
    results["regen_candidate_generator_data_source_repair_status"] = (
        "PASS_REGEN_CANDIDATE_GENERATOR_DATA_SOURCE_REPAIR_PHASE_16J3A"
        if complete else
        "FAIL_REGEN_CANDIDATE_GENERATOR_DATA_SOURCE_REPAIR_PHASE_16J3A"
    )
    results["phase_16j3a_status"] = results["regen_candidate_generator_data_source_repair_status"]
    results["regen_candidate_generator_data_source_repair_mapped_values"] = mapped
    results["regen_candidate_generator_data_source_repair_missing_keys"] = missing
    results["regen_candidate_generator_data_source_repair_base_geometry_complete"] = complete

    results["regen_candidate_generator_base_geometry"] = {
        "base_geometry_complete": complete,
        **mapped,
    }

    results["phase_16j3b_candidate_generation_execution_recheck_allowed"] = complete

    return results
