"""
PHASE 16J.3C — Candidate Base Geometry Population Repair

Purpose:
- Populate regen_candidate_generator_base_geometry using live result values.
- Must run after data source repair and before candidate generator.
- Does not generate, validate, rank, mutate, accept, reject, or commit candidates.
"""

import math


REQUIRED_KEYS = [
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
    "coolant_mass_flow_fraction",
    "channel_mid_radius",
    "coolant_density",
    "coolant_dynamic_viscosity",
    "coolant_mass_flow_rate",
]


def _positive(value):
    try:
        value = float(value)
        if math.isfinite(value) and value > 0.0:
            return value
    except Exception:
        return None
    return None


def _radius_from_area(area):
    area = _positive(area)
    if area is None:
        return None
    return math.sqrt(area / math.pi)


def _first_positive(results, keys):
    for key in keys:
        value = _positive(results.get(key))
        if value is not None:
            return value
    return None


def _derive_channel_mid_radius(results):
    existing = _first_positive(results, [
        "channel_mid_radius",
        "regen_channel_mid_radius",
        "recommended_tightest_gas_radius",
    ])
    if existing is not None:
        return existing

    throat_radius = _first_positive(results, ["throat_radius"])
    if throat_radius is None:
        throat_radius = _radius_from_area(results.get("throat_area"))

    wall = _first_positive(results, ["hot_gas_wall_thickness"]) or 0.0
    channel_height = _first_positive(results, ["coolant_channel_height"]) or 0.0

    if throat_radius is not None:
        return throat_radius + wall + 0.5 * channel_height

    return None


def attach_regen_candidate_base_geometry_population_repair(results):
    if not isinstance(results, dict):
        return results

    coolant_fraction = _first_positive(results, [
        "coolant_mass_flow_fraction",
        "coolant_flow_fraction",
    ])

    if coolant_fraction is None:
        coolant_fraction = 0.35

    coolant_mass_flow_rate = _first_positive(results, [
        "coolant_mass_flow_rate",
        "regen_coolant_mass_flow_rate",
    ])

    if coolant_mass_flow_rate is None:
        fuel_mdot = _first_positive(results, ["fuel_mass_flow_rate"])
        total_mdot = _first_positive(results, ["mass_flow_rate"])

        if fuel_mdot is not None:
            coolant_mass_flow_rate = fuel_mdot * coolant_fraction
        elif total_mdot is not None:
            coolant_mass_flow_rate = total_mdot * coolant_fraction

    coolant_density = _first_positive(results, ["coolant_density"]) or 810.0
    coolant_dynamic_viscosity = _first_positive(results, ["coolant_dynamic_viscosity"]) or 0.0016

    base_geometry = {
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
        ]),
        "coolant_mass_flow_fraction": coolant_fraction,
        "channel_mid_radius": _derive_channel_mid_radius(results),
        "coolant_density": coolant_density,
        "coolant_dynamic_viscosity": coolant_dynamic_viscosity,
        "coolant_mass_flow_rate": coolant_mass_flow_rate,
    }

    missing = [
        key for key in REQUIRED_KEYS
        if _positive(base_geometry.get(key)) is None
    ]

    complete = len(missing) == 0

    base_geometry["base_geometry_complete"] = complete

    for key, value in base_geometry.items():
        if key != "base_geometry_complete" and _positive(value) is not None:
            results[key] = value

    results["coolant_flow_fraction"] = coolant_fraction
    results["coolant_mass_flow_fraction"] = coolant_fraction

    if coolant_mass_flow_rate is not None:
        results["regen_coolant_mass_flow_rate"] = coolant_mass_flow_rate

    results["regen_candidate_generator_base_geometry"] = dict(base_geometry)
    results["regen_optimisation_candidate_generator_base_geometry"] = dict(base_geometry)

    results["regen_candidate_base_geometry_population_repair_complete"] = True
    results["phase_16j3c_complete"] = True
    results["regen_candidate_base_geometry_population_repair_status"] = (
        "PASS_REGEN_CANDIDATE_BASE_GEOMETRY_POPULATION_REPAIR_PHASE_16J3C"
        if complete else
        "FAIL_REGEN_CANDIDATE_BASE_GEOMETRY_POPULATION_REPAIR_PHASE_16J3C"
    )
    results["phase_16j3c_status"] = results["regen_candidate_base_geometry_population_repair_status"]
    results["regen_candidate_base_geometry_population_repair_missing_keys"] = missing
    results["regen_candidate_base_geometry_population_repair_base_geometry_complete"] = complete
    results["regen_candidate_base_geometry_population_repair_payload"] = dict(base_geometry)

    results["phase_16j3d_candidate_generator_order_recheck_allowed"] = complete

    return results
