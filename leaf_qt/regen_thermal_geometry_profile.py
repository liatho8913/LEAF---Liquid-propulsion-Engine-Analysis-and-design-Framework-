from dataclasses import dataclass, asdict
import math


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_PROFILE"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_PROFILE"


@dataclass
class ThermalGeometryPoint:
    axial_position: float
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


def calculate_thermal_margin(max_allowable_wall_temperature, hot_wall_temperature):
    max_allowable_wall_temperature = _safe_float(max_allowable_wall_temperature)
    hot_wall_temperature = _safe_float(hot_wall_temperature)

    if max_allowable_wall_temperature is None or hot_wall_temperature is None:
        return None

    return max_allowable_wall_temperature - hot_wall_temperature


def normalise_thermal_geometry_points(
    points,
    max_allowable_wall_temperature=None,
):
    normalised = []
    errors = []

    for index, point in enumerate(points or []):
        axial_position = _safe_float(point.get("axial_position", point.get("x")))
        heat_flux = _safe_float(point.get("heat_flux"))
        hot_wall_temperature = _safe_float(
            point.get("hot_wall_temperature", point.get("wall_temperature"))
        )
        coolant_temperature = _safe_float(point.get("coolant_temperature"))
        pressure_drop = _safe_float(point.get("pressure_drop"))
        thermal_margin = _safe_float(point.get("thermal_margin"))

        if thermal_margin is None:
            thermal_margin = calculate_thermal_margin(
                max_allowable_wall_temperature,
                hot_wall_temperature,
            )

        if axial_position is None:
            errors.append(f"Point {index}: missing axial position.")
            continue

        if heat_flux is None or heat_flux < 0:
            errors.append(f"Point {index}: invalid heat flux.")
            continue

        if hot_wall_temperature is None or hot_wall_temperature <= 0:
            errors.append(f"Point {index}: invalid hot wall temperature.")
            continue

        if coolant_temperature is None or coolant_temperature <= 0:
            errors.append(f"Point {index}: invalid coolant temperature.")
            continue

        if pressure_drop is None or pressure_drop < 0:
            errors.append(f"Point {index}: invalid pressure drop.")
            continue

        normalised.append(
            ThermalGeometryPoint(
                axial_position=axial_position,
                heat_flux=heat_flux,
                hot_wall_temperature=hot_wall_temperature,
                coolant_temperature=coolant_temperature,
                pressure_drop=pressure_drop,
                thermal_margin=thermal_margin,
            )
        )

    normalised.sort(key=lambda point: point.axial_position)

    return normalised, errors


def _linear_interpolate(x, x0, y0, x1, y1):
    if x1 == x0:
        return y0

    fraction = (x - x0) / (x1 - x0)
    return y0 + fraction * (y1 - y0)


def interpolate_thermal_geometry_profile(
    profile_points,
    axial_position,
    max_allowable_wall_temperature=None,
):
    axial_position = _safe_float(axial_position)

    if axial_position is None:
        return None

    points, errors = normalise_thermal_geometry_points(
        profile_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    if errors or not points:
        return None

    if axial_position <= points[0].axial_position:
        return asdict(points[0])

    if axial_position >= points[-1].axial_position:
        return asdict(points[-1])

    for left, right in zip(points[:-1], points[1:]):
        if left.axial_position <= axial_position <= right.axial_position:
            return {
                "axial_position": axial_position,
                "heat_flux": _linear_interpolate(
                    axial_position,
                    left.axial_position,
                    left.heat_flux,
                    right.axial_position,
                    right.heat_flux,
                ),
                "hot_wall_temperature": _linear_interpolate(
                    axial_position,
                    left.axial_position,
                    left.hot_wall_temperature,
                    right.axial_position,
                    right.hot_wall_temperature,
                ),
                "coolant_temperature": _linear_interpolate(
                    axial_position,
                    left.axial_position,
                    left.coolant_temperature,
                    right.axial_position,
                    right.coolant_temperature,
                ),
                "pressure_drop": _linear_interpolate(
                    axial_position,
                    left.axial_position,
                    left.pressure_drop,
                    right.axial_position,
                    right.pressure_drop,
                ),
                "thermal_margin": (
                    None
                    if left.thermal_margin is None or right.thermal_margin is None
                    else _linear_interpolate(
                        axial_position,
                        left.axial_position,
                        left.thermal_margin,
                        right.axial_position,
                        right.thermal_margin,
                    )
                ),
            }

    return None


def build_thermal_geometry_profile(
    profile_points,
    max_allowable_wall_temperature=None,
):
    points, errors = normalise_thermal_geometry_points(
        profile_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    duplicate_positions = set()
    seen_positions = set()

    for point in points:
        if point.axial_position in seen_positions:
            duplicate_positions.add(point.axial_position)
        seen_positions.add(point.axial_position)

    if duplicate_positions:
        errors.append(
            f"Duplicate axial positions found: {sorted(duplicate_positions)}"
        )

    pass_state = len(errors) == 0 and len(points) >= 2

    heat_flux_values = [point.heat_flux for point in points]
    wall_temperature_values = [point.hot_wall_temperature for point in points]
    coolant_temperature_values = [point.coolant_temperature for point in points]
    pressure_drop_values = [point.pressure_drop for point in points]
    thermal_margin_values = [
        point.thermal_margin for point in points if point.thermal_margin is not None
    ]

    return {
        "regen_thermal_geometry_profile_status": (
            PASS_STATUS if pass_state else FAIL_STATUS
        ),
        "regen_thermal_geometry_profile_pass": pass_state,
        "point_count": len(points),
        "points": [asdict(point) for point in points],
        "minimum_axial_position": points[0].axial_position if points else None,
        "maximum_axial_position": points[-1].axial_position if points else None,
        "maximum_heat_flux": max(heat_flux_values) if heat_flux_values else None,
        "maximum_hot_wall_temperature": (
            max(wall_temperature_values) if wall_temperature_values else None
        ),
        "maximum_coolant_temperature": (
            max(coolant_temperature_values) if coolant_temperature_values else None
        ),
        "total_pressure_drop": (
            sum(pressure_drop_values) if pressure_drop_values else None
        ),
        "minimum_thermal_margin": (
            min(thermal_margin_values) if thermal_margin_values else None
        ),
        "errors": errors,
        "warnings": [],
    }


def sample_thermal_geometry_profile(
    profile_points,
    sample_positions,
    max_allowable_wall_temperature=None,
):
    profile = build_thermal_geometry_profile(
        profile_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    samples = []

    if not profile.get("regen_thermal_geometry_profile_pass", False):
        return {
            "regen_thermal_geometry_sampling_status": "FAIL_REGEN_THERMAL_GEOMETRY_SAMPLING",
            "regen_thermal_geometry_sampling_pass": False,
            "profile": profile,
            "samples": samples,
            "errors": ["Thermal geometry profile failed before sampling."],
            "warnings": [],
        }

    for axial_position in sample_positions or []:
        sample = interpolate_thermal_geometry_profile(
            profile.get("points", []),
            axial_position,
            max_allowable_wall_temperature=max_allowable_wall_temperature,
        )

        if sample is not None:
            samples.append(sample)

    pass_state = len(samples) == len(sample_positions or [])

    return {
        "regen_thermal_geometry_sampling_status": (
            "PASS_REGEN_THERMAL_GEOMETRY_SAMPLING"
            if pass_state
            else "FAIL_REGEN_THERMAL_GEOMETRY_SAMPLING"
        ),
        "regen_thermal_geometry_sampling_pass": pass_state,
        "profile": profile,
        "sample_count": len(samples),
        "samples": samples,
        "errors": [] if pass_state else ["One or more requested thermal samples failed."],
        "warnings": [],
    }


def flatten_thermal_geometry_profile_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_thermal_geometry_profile_status": result.get(
            "regen_thermal_geometry_profile_status"
        ),
        f"{prefix}_regen_thermal_geometry_profile_pass": (
            1.0 if result.get("regen_thermal_geometry_profile_pass") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_profile_point_count": float(
            result.get("point_count", 0)
        ),
        f"{prefix}_regen_thermal_geometry_profile_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_profile_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_thermal_geometry_profile_min_x": result.get(
            "minimum_axial_position"
        ),
        f"{prefix}_regen_thermal_geometry_profile_max_x": result.get(
            "maximum_axial_position"
        ),
        f"{prefix}_regen_thermal_geometry_maximum_heat_flux": result.get(
            "maximum_heat_flux"
        ),
        f"{prefix}_regen_thermal_geometry_maximum_hot_wall_temperature": result.get(
            "maximum_hot_wall_temperature"
        ),
        f"{prefix}_regen_thermal_geometry_maximum_coolant_temperature": result.get(
            "maximum_coolant_temperature"
        ),
        f"{prefix}_regen_thermal_geometry_total_pressure_drop": result.get(
            "total_pressure_drop"
        ),
        f"{prefix}_regen_thermal_geometry_minimum_thermal_margin": result.get(
            "minimum_thermal_margin"
        ),
    }

    for index, point in enumerate(result.get("points", [])):
        point_prefix = f"{prefix}_regen_thermal_geometry_point_{index + 1}"
        flat.update(
            {
                f"{point_prefix}_x": point.get("axial_position"),
                f"{point_prefix}_heat_flux": point.get("heat_flux"),
                f"{point_prefix}_hot_wall_temperature": point.get(
                    "hot_wall_temperature"
                ),
                f"{point_prefix}_coolant_temperature": point.get(
                    "coolant_temperature"
                ),
                f"{point_prefix}_pressure_drop": point.get("pressure_drop"),
                f"{point_prefix}_thermal_margin": point.get("thermal_margin"),
            }
        )

    return flat