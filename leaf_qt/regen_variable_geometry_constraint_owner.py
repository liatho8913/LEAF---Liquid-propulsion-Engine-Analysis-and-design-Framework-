import math

try:
    from regen_variable_geometry_profile import build_variable_geometry_profile
except Exception:
    from leaf_qt.regen_variable_geometry_profile import build_variable_geometry_profile


PASS_STATUS = "PASS_REGEN_VARIABLE_GEOMETRY_CONSTRAINT_OWNER"
FAIL_STATUS = "FAIL_REGEN_VARIABLE_GEOMETRY_CONSTRAINT_OWNER"


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


def _check_range(value, minimum, maximum, label, errors, warnings):
    value = _safe_float(value)

    if value is None:
        errors.append(f"{label} is missing.")
        return

    if minimum is not None and value < minimum:
        errors.append(f"{label} is below minimum limit.")

    if maximum is not None and value > maximum:
        errors.append(f"{label} is above maximum limit.")


def validate_variable_geometry_point_constraints(
    point,
    index,
    minimum_channel_width=0.0002,
    maximum_channel_width=0.01,
    minimum_channel_height=0.0002,
    maximum_channel_height=0.02,
    minimum_rib_width=0.0002,
    maximum_rib_width=0.01,
    minimum_hydraulic_diameter=0.0002,
    maximum_hydraulic_diameter=0.02,
):
    errors = []
    warnings = []

    _check_range(
        point.get("channel_width"),
        minimum_channel_width,
        maximum_channel_width,
        f"Point {index} channel width",
        errors,
        warnings,
    )

    _check_range(
        point.get("channel_height"),
        minimum_channel_height,
        maximum_channel_height,
        f"Point {index} channel height",
        errors,
        warnings,
    )

    _check_range(
        point.get("rib_width"),
        minimum_rib_width,
        maximum_rib_width,
        f"Point {index} rib width",
        errors,
        warnings,
    )

    _check_range(
        point.get("hydraulic_diameter"),
        minimum_hydraulic_diameter,
        maximum_hydraulic_diameter,
        f"Point {index} hydraulic diameter",
        errors,
        warnings,
    )

    return {
        "point_index": index,
        "axial_position": point.get("axial_position"),
        "point_constraint_pass": len(errors) == 0,
        "point_constraint_status": (
            "PASS_REGEN_VARIABLE_GEOMETRY_POINT_CONSTRAINTS"
            if len(errors) == 0
            else "FAIL_REGEN_VARIABLE_GEOMETRY_POINT_CONSTRAINTS"
        ),
        "errors": errors,
        "warnings": warnings,
    }


def validate_variable_geometry_gradient_constraints(
    points,
    max_channel_width_jump_fraction=1.5,
    max_channel_height_jump_fraction=1.5,
    max_rib_width_jump_fraction=1.5,
    max_hydraulic_diameter_jump_fraction=1.5,
):
    errors = []
    warnings = []

    previous = None

    checks = [
        ("channel_width", max_channel_width_jump_fraction),
        ("channel_height", max_channel_height_jump_fraction),
        ("rib_width", max_rib_width_jump_fraction),
        ("hydraulic_diameter", max_hydraulic_diameter_jump_fraction),
    ]

    for current in points:
        if previous is None:
            previous = current
            continue

        previous_x = _safe_float(previous.get("axial_position"))
        current_x = _safe_float(current.get("axial_position"))

        if previous_x is None or current_x is None:
            errors.append("Missing axial position in gradient validation.")
            previous = current
            continue

        if current_x <= previous_x:
            errors.append("Variable geometry axial positions must strictly increase.")
            previous = current
            continue

        for key, limit in checks:
            old_value = _safe_float(previous.get(key))
            new_value = _safe_float(current.get(key))

            if old_value is None or new_value is None or old_value <= 0 or new_value <= 0:
                errors.append(f"Cannot validate gradient for {key}; invalid value found.")
                continue

            jump_ratio = max(old_value, new_value) / min(old_value, new_value)

            if jump_ratio > limit:
                warnings.append(
                    {
                        "from_x": previous_x,
                        "to_x": current_x,
                        "parameter": key,
                        "jump_ratio": jump_ratio,
                        "limit": limit,
                        "message": f"{key} changes sharply between adjacent profile points.",
                    }
                )

        previous = current

    return {
        "variable_geometry_gradient_constraint_pass": len(errors) == 0,
        "variable_geometry_gradient_constraint_status": (
            "PASS_REGEN_VARIABLE_GEOMETRY_GRADIENT_CONSTRAINTS"
            if len(errors) == 0
            else "FAIL_REGEN_VARIABLE_GEOMETRY_GRADIENT_CONSTRAINTS"
        ),
        "errors": errors,
        "warnings": warnings,
    }


def validate_variable_geometry_profile_constraints(profile_points, **limits):
    errors = []
    warnings = []

    profile = build_variable_geometry_profile(profile_points)

    if not profile.get("regen_variable_geometry_profile_pass", False):
        errors.append("Variable geometry profile failed before constraint validation.")
        errors.extend(profile.get("errors", []))

    points = profile.get("points", [])

    point_results = []

    for index, point in enumerate(points):
        point_result = validate_variable_geometry_point_constraints(
            point,
            index=index,
            minimum_channel_width=limits.get("minimum_channel_width", 0.0002),
            maximum_channel_width=limits.get("maximum_channel_width", 0.01),
            minimum_channel_height=limits.get("minimum_channel_height", 0.0002),
            maximum_channel_height=limits.get("maximum_channel_height", 0.02),
            minimum_rib_width=limits.get("minimum_rib_width", 0.0002),
            maximum_rib_width=limits.get("maximum_rib_width", 0.01),
            minimum_hydraulic_diameter=limits.get("minimum_hydraulic_diameter", 0.0002),
            maximum_hydraulic_diameter=limits.get("maximum_hydraulic_diameter", 0.02),
        )

        point_results.append(point_result)

        for error in point_result.get("errors", []):
            errors.append(error)

        for warning in point_result.get("warnings", []):
            warnings.append(warning)

    gradient_result = validate_variable_geometry_gradient_constraints(
        points,
        max_channel_width_jump_fraction=limits.get("max_channel_width_jump_fraction", 1.5),
        max_channel_height_jump_fraction=limits.get("max_channel_height_jump_fraction", 1.5),
        max_rib_width_jump_fraction=limits.get("max_rib_width_jump_fraction", 1.5),
        max_hydraulic_diameter_jump_fraction=limits.get("max_hydraulic_diameter_jump_fraction", 1.5),
    )

    errors.extend(gradient_result.get("errors", []))
    warnings.extend(gradient_result.get("warnings", []))

    point_fail_count = sum(
        1 for result in point_results
        if not result.get("point_constraint_pass", False)
    )

    constraint_pass = (
        len(errors) == 0
        and point_fail_count == 0
        and gradient_result.get("variable_geometry_gradient_constraint_pass", False)
    )

    return {
        "regen_variable_geometry_constraint_owner_status": (
            PASS_STATUS if constraint_pass else FAIL_STATUS
        ),
        "regen_variable_geometry_constraint_owner_pass": constraint_pass,
        "profile": profile,
        "point_constraint_results": point_results,
        "point_constraint_fail_count": point_fail_count,
        "gradient_constraint_result": gradient_result,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_variable_geometry_constraint_owner_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_variable_geometry_constraint_owner_status": result.get(
            "regen_variable_geometry_constraint_owner_status"
        ),
        f"{prefix}_regen_variable_geometry_constraint_owner_pass": (
            1.0 if result.get("regen_variable_geometry_constraint_owner_pass") else 0.0
        ),
        f"{prefix}_regen_variable_geometry_constraint_point_fail_count": float(
            result.get("point_constraint_fail_count", 0)
        ),
        f"{prefix}_regen_variable_geometry_constraint_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_variable_geometry_constraint_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_variable_geometry_gradient_constraint_status": (
            result.get("gradient_constraint_result", {}).get(
                "variable_geometry_gradient_constraint_status"
            )
        ),
        f"{prefix}_regen_variable_geometry_gradient_constraint_pass": (
            1.0
            if result.get("gradient_constraint_result", {}).get(
                "variable_geometry_gradient_constraint_pass"
            )
            else 0.0
        ),
    }

    for index, point_result in enumerate(result.get("point_constraint_results", [])):
        point_prefix = f"{prefix}_regen_variable_geometry_constraint_point_{index + 1}"
        flat.update(
            {
                f"{point_prefix}_status": point_result.get("point_constraint_status"),
                f"{point_prefix}_pass": (
                    1.0 if point_result.get("point_constraint_pass") else 0.0
                ),
                f"{point_prefix}_x": point_result.get("axial_position"),
                f"{point_prefix}_error_count": float(len(point_result.get("errors", []))),
                f"{point_prefix}_warning_count": float(len(point_result.get("warnings", []))),
            }
        )

    return flat