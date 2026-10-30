from dataclasses import dataclass, asdict
import math

try:
    from regen_variable_geometry_profile import (
        build_variable_geometry_profile,
        interpolate_variable_geometry_profile,
    )
    from regen_thermal_geometry_profile import (
        build_thermal_geometry_profile,
        interpolate_thermal_geometry_profile,
    )
except Exception:
    from leaf_qt.regen_variable_geometry_profile import (
        build_variable_geometry_profile,
        interpolate_variable_geometry_profile,
    )
    from leaf_qt.regen_thermal_geometry_profile import (
        build_thermal_geometry_profile,
        interpolate_thermal_geometry_profile,
    )


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_COUPLING"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_COUPLING"


@dataclass
class CoupledThermalGeometryPoint:
    axial_position: float

    channel_width: float
    channel_height: float
    rib_width: float
    hydraulic_diameter: float

    heat_flux: float
    hot_wall_temperature: float
    coolant_temperature: float
    pressure_drop: float
    thermal_margin: float | None = None


def _safe_float(value, default=None):
    try:
        if value is None:
            return default
        value = float(value)
        if math.isnan(value) or math.isinf(value):
            return default
        return value
    except Exception:
        return default


def _unique_sorted_positions(*position_lists):
    values = []

    for positions in position_lists:
        for value in positions or []:
            value = _safe_float(value)
            if value is not None:
                values.append(value)

    return sorted(set(values))


def _extract_positions(profile_result):
    return [
        point.get("axial_position")
        for point in profile_result.get("points", [])
        if point.get("axial_position") is not None
    ]


def build_coupled_thermal_geometry_profile(
    variable_geometry_points,
    thermal_geometry_points,
    sample_positions=None,
    max_allowable_wall_temperature=900.0,
):
    errors = []
    warnings = []

    variable_profile = build_variable_geometry_profile(variable_geometry_points)
    thermal_profile = build_thermal_geometry_profile(
        thermal_geometry_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    if not variable_profile.get("regen_variable_geometry_profile_pass", False):
        errors.append("Variable geometry profile failed before coupling.")
        errors.extend(variable_profile.get("errors", []))

    if not thermal_profile.get("regen_thermal_geometry_profile_pass", False):
        errors.append("Thermal geometry profile failed before coupling.")
        errors.extend(thermal_profile.get("errors", []))

    if sample_positions is None:
        sample_positions = _unique_sorted_positions(
            _extract_positions(variable_profile),
            _extract_positions(thermal_profile),
        )

    coupled_points = []

    if not errors:
        for axial_position in sample_positions:
            geometry_sample = interpolate_variable_geometry_profile(
                variable_profile.get("points", []),
                axial_position,
            )
            thermal_sample = interpolate_thermal_geometry_profile(
                thermal_profile.get("points", []),
                axial_position,
                max_allowable_wall_temperature=max_allowable_wall_temperature,
            )

            if geometry_sample is None:
                errors.append(f"Failed to sample variable geometry at x={axial_position}.")
                continue

            if thermal_sample is None:
                errors.append(f"Failed to sample thermal geometry at x={axial_position}.")
                continue

            coupled_points.append(
                CoupledThermalGeometryPoint(
                    axial_position=axial_position,
                    channel_width=geometry_sample.get("channel_width"),
                    channel_height=geometry_sample.get("channel_height"),
                    rib_width=geometry_sample.get("rib_width"),
                    hydraulic_diameter=geometry_sample.get("hydraulic_diameter"),
                    heat_flux=thermal_sample.get("heat_flux"),
                    hot_wall_temperature=thermal_sample.get("hot_wall_temperature"),
                    coolant_temperature=thermal_sample.get("coolant_temperature"),
                    pressure_drop=thermal_sample.get("pressure_drop"),
                    thermal_margin=thermal_sample.get("thermal_margin"),
                )
            )

    pass_state = (
        len(errors) == 0
        and len(coupled_points) > 0
        and len(coupled_points) == len(sample_positions or [])
    )

    return {
        "regen_thermal_geometry_coupling_status": (
            PASS_STATUS if pass_state else FAIL_STATUS
        ),
        "regen_thermal_geometry_coupling_pass": pass_state,
        "variable_profile": variable_profile,
        "thermal_profile": thermal_profile,
        "coupled_point_count": len(coupled_points),
        "coupled_points": [asdict(point) for point in coupled_points],
        "sample_positions": list(sample_positions or []),
        "errors": errors,
        "warnings": warnings,
    }


def flatten_coupled_thermal_geometry_profile_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_thermal_geometry_coupling_status": result.get(
            "regen_thermal_geometry_coupling_status"
        ),
        f"{prefix}_regen_thermal_geometry_coupling_pass": (
            1.0 if result.get("regen_thermal_geometry_coupling_pass") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_coupled_point_count": float(
            result.get("coupled_point_count", 0)
        ),
        f"{prefix}_regen_thermal_geometry_coupling_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_coupling_warning_count": float(
            len(result.get("warnings", []))
        ),
    }

    for index, point in enumerate(result.get("coupled_points", [])):
        point_prefix = f"{prefix}_regen_thermal_geometry_coupled_point_{index + 1}"

        flat.update(
            {
                f"{point_prefix}_x": point.get("axial_position"),
                f"{point_prefix}_channel_width": point.get("channel_width"),
                f"{point_prefix}_channel_height": point.get("channel_height"),
                f"{point_prefix}_rib_width": point.get("rib_width"),
                f"{point_prefix}_hydraulic_diameter": point.get("hydraulic_diameter"),
                f"{point_prefix}_heat_flux": point.get("heat_flux"),
                f"{point_prefix}_hot_wall_temperature": point.get("hot_wall_temperature"),
                f"{point_prefix}_coolant_temperature": point.get("coolant_temperature"),
                f"{point_prefix}_pressure_drop": point.get("pressure_drop"),
                f"{point_prefix}_thermal_margin": point.get("thermal_margin"),
            }
        )

    return flat