from dataclasses import dataclass, asdict
import math


PASS_STATUS = "PASS_REGEN_VARIABLE_GEOMETRY_PROFILE"
FAIL_STATUS = "FAIL_REGEN_VARIABLE_GEOMETRY_PROFILE"


@dataclass
class VariableGeometryPoint:
    axial_position: float
    channel_width: float
    channel_height: float
    rib_width: float
    hydraulic_diameter: float | None = None


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


def calculate_rectangular_hydraulic_diameter(width, height):
    width = _safe_float(width)
    height = _safe_float(height)

    if width is None or height is None:
        return None

    if width <= 0 or height <= 0:
        return None

    return (2.0 * width * height) / (width + height)


def normalise_variable_geometry_points(points):
    normalised = []
    errors = []

    for index, point in enumerate(points or []):
        axial_position = _safe_float(point.get("axial_position", point.get("x")))
        channel_width = _safe_float(point.get("channel_width"))
        channel_height = _safe_float(point.get("channel_height"))
        rib_width = _safe_float(point.get("rib_width"))
        hydraulic_diameter = _safe_float(point.get("hydraulic_diameter"))

        if hydraulic_diameter is None:
            hydraulic_diameter = calculate_rectangular_hydraulic_diameter(
                channel_width,
                channel_height,
            )

        if axial_position is None:
            errors.append(f"Point {index}: missing axial position.")
            continue

        if channel_width is None or channel_width <= 0:
            errors.append(f"Point {index}: invalid channel width.")
            continue

        if channel_height is None or channel_height <= 0:
            errors.append(f"Point {index}: invalid channel height.")
            continue

        if rib_width is None or rib_width <= 0:
            errors.append(f"Point {index}: invalid rib width.")
            continue

        if hydraulic_diameter is None or hydraulic_diameter <= 0:
            errors.append(f"Point {index}: invalid hydraulic diameter.")
            continue

        normalised.append(
            VariableGeometryPoint(
                axial_position=axial_position,
                channel_width=channel_width,
                channel_height=channel_height,
                rib_width=rib_width,
                hydraulic_diameter=hydraulic_diameter,
            )
        )

    normalised.sort(key=lambda point: point.axial_position)

    return normalised, errors


def _linear_interpolate(x, x0, y0, x1, y1):
    if x1 == x0:
        return y0

    fraction = (x - x0) / (x1 - x0)
    return y0 + fraction * (y1 - y0)


def interpolate_variable_geometry_profile(profile_points, axial_position):
    axial_position = _safe_float(axial_position)

    if axial_position is None:
        return None

    points, errors = normalise_variable_geometry_points(profile_points)

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
                "channel_width": _linear_interpolate(
                    axial_position,
                    left.axial_position,
                    left.channel_width,
                    right.axial_position,
                    right.channel_width,
                ),
                "channel_height": _linear_interpolate(
                    axial_position,
                    left.axial_position,
                    left.channel_height,
                    right.axial_position,
                    right.channel_height,
                ),
                "rib_width": _linear_interpolate(
                    axial_position,
                    left.axial_position,
                    left.rib_width,
                    right.axial_position,
                    right.rib_width,
                ),
                "hydraulic_diameter": _linear_interpolate(
                    axial_position,
                    left.axial_position,
                    left.hydraulic_diameter,
                    right.axial_position,
                    right.hydraulic_diameter,
                ),
            }

    return None


def build_variable_geometry_profile(profile_points):
    points, errors = normalise_variable_geometry_points(profile_points)

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

    return {
        "regen_variable_geometry_profile_status": (
            PASS_STATUS if pass_state else FAIL_STATUS
        ),
        "regen_variable_geometry_profile_pass": pass_state,
        "point_count": len(points),
        "points": [asdict(point) for point in points],
        "minimum_axial_position": points[0].axial_position if points else None,
        "maximum_axial_position": points[-1].axial_position if points else None,
        "errors": errors,
        "warnings": [],
    }


def sample_variable_geometry_profile(profile_points, sample_positions):
    profile = build_variable_geometry_profile(profile_points)

    samples = []

    if not profile.get("regen_variable_geometry_profile_pass", False):
        return {
            "regen_variable_geometry_sampling_status": "FAIL_REGEN_VARIABLE_GEOMETRY_SAMPLING",
            "regen_variable_geometry_sampling_pass": False,
            "profile": profile,
            "samples": samples,
            "errors": ["Variable geometry profile failed before sampling."],
            "warnings": [],
        }

    for axial_position in sample_positions or []:
        sample = interpolate_variable_geometry_profile(
            profile.get("points", []),
            axial_position,
        )

        if sample is not None:
            samples.append(sample)

    pass_state = len(samples) == len(sample_positions or [])

    return {
        "regen_variable_geometry_sampling_status": (
            "PASS_REGEN_VARIABLE_GEOMETRY_SAMPLING"
            if pass_state
            else "FAIL_REGEN_VARIABLE_GEOMETRY_SAMPLING"
        ),
        "regen_variable_geometry_sampling_pass": pass_state,
        "profile": profile,
        "sample_count": len(samples),
        "samples": samples,
        "errors": [] if pass_state else ["One or more requested samples failed."],
        "warnings": [],
    }


def flatten_variable_geometry_profile_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_variable_geometry_profile_status": result.get(
            "regen_variable_geometry_profile_status"
        ),
        f"{prefix}_regen_variable_geometry_profile_pass": (
            1.0 if result.get("regen_variable_geometry_profile_pass") else 0.0
        ),
        f"{prefix}_regen_variable_geometry_profile_point_count": float(
            result.get("point_count", 0)
        ),
        f"{prefix}_regen_variable_geometry_profile_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_variable_geometry_profile_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_variable_geometry_profile_min_x": result.get(
            "minimum_axial_position"
        ),
        f"{prefix}_regen_variable_geometry_profile_max_x": result.get(
            "maximum_axial_position"
        ),
    }

    for index, point in enumerate(result.get("points", [])):
        point_prefix = f"{prefix}_regen_variable_geometry_point_{index + 1}"
        flat.update(
            {
                f"{point_prefix}_x": point.get("axial_position"),
                f"{point_prefix}_channel_width": point.get("channel_width"),
                f"{point_prefix}_channel_height": point.get("channel_height"),
                f"{point_prefix}_rib_width": point.get("rib_width"),
                f"{point_prefix}_hydraulic_diameter": point.get("hydraulic_diameter"),
            }
        )

    return flat