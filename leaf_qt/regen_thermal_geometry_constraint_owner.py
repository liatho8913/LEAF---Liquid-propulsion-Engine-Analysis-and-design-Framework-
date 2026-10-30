import math

try:
    from regen_thermal_geometry_profile import build_thermal_geometry_profile
except Exception:
    from leaf_qt.regen_thermal_geometry_profile import build_thermal_geometry_profile


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_CONSTRAINT_OWNER"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_CONSTRAINT_OWNER"


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


def validate_thermal_geometry_point_constraints(
    point,
    index,
    maximum_hot_wall_temperature=900.0,
    maximum_coolant_temperature=500.0,
    maximum_pressure_drop=2.0e6,
    minimum_thermal_margin=0.0,
):
    errors = []
    warnings = []

    heat_flux = _safe_float(point.get("heat_flux"))
    wall_temp = _safe_float(point.get("hot_wall_temperature"))
    coolant_temp = _safe_float(point.get("coolant_temperature"))
    pressure_drop = _safe_float(point.get("pressure_drop"))
    thermal_margin = _safe_float(point.get("thermal_margin"))

    if heat_flux is None or heat_flux < 0:
        errors.append(f"Point {index}: invalid heat flux.")

    if wall_temp is None or wall_temp <= 0:
        errors.append(f"Point {index}: invalid hot wall temperature.")
    elif wall_temp > maximum_hot_wall_temperature:
        errors.append(f"Point {index}: hot wall temperature exceeds limit.")

    if coolant_temp is None or coolant_temp <= 0:
        errors.append(f"Point {index}: invalid coolant temperature.")
    elif coolant_temp > maximum_coolant_temperature:
        errors.append(f"Point {index}: coolant temperature exceeds limit.")

    if pressure_drop is None or pressure_drop < 0:
        errors.append(f"Point {index}: invalid pressure drop.")
    elif pressure_drop > maximum_pressure_drop:
        errors.append(f"Point {index}: pressure drop exceeds limit.")

    if thermal_margin is not None and thermal_margin < minimum_thermal_margin:
        errors.append(f"Point {index}: thermal margin below minimum.")

    return {
        "point_index": index,
        "axial_position": point.get("axial_position"),
        "thermal_point_constraint_pass": len(errors) == 0,
        "thermal_point_constraint_status": (
            "PASS_REGEN_THERMAL_GEOMETRY_POINT_CONSTRAINTS"
            if len(errors) == 0
            else "FAIL_REGEN_THERMAL_GEOMETRY_POINT_CONSTRAINTS"
        ),
        "errors": errors,
        "warnings": warnings,
    }


def validate_thermal_geometry_gradient_constraints(
    points,
    max_wall_temperature_jump=250.0,
    max_coolant_temperature_jump=150.0,
    max_heat_flux_jump_fraction=3.0,
):
    errors = []
    warnings = []

    previous = None

    for current in points:
        if previous is None:
            previous = current
            continue

        previous_x = _safe_float(previous.get("axial_position"))
        current_x = _safe_float(current.get("axial_position"))

        if previous_x is None or current_x is None:
            errors.append("Missing axial position in thermal gradient validation.")
            previous = current
            continue

        if current_x <= previous_x:
            errors.append("Thermal profile axial positions must strictly increase.")
            previous = current
            continue

        old_wall = _safe_float(previous.get("hot_wall_temperature"))
        new_wall = _safe_float(current.get("hot_wall_temperature"))

        if old_wall is not None and new_wall is not None:
            if abs(new_wall - old_wall) > max_wall_temperature_jump:
                warnings.append(
                    {
                        "from_x": previous_x,
                        "to_x": current_x,
                        "parameter": "hot_wall_temperature",
                        "jump": abs(new_wall - old_wall),
                        "limit": max_wall_temperature_jump,
                        "message": "Hot wall temperature changes sharply between adjacent thermal points.",
                    }
                )

        old_coolant = _safe_float(previous.get("coolant_temperature"))
        new_coolant = _safe_float(current.get("coolant_temperature"))

        if old_coolant is not None and new_coolant is not None:
            if abs(new_coolant - old_coolant) > max_coolant_temperature_jump:
                warnings.append(
                    {
                        "from_x": previous_x,
                        "to_x": current_x,
                        "parameter": "coolant_temperature",
                        "jump": abs(new_coolant - old_coolant),
                        "limit": max_coolant_temperature_jump,
                        "message": "Coolant temperature changes sharply between adjacent thermal points.",
                    }
                )

        old_heat_flux = _safe_float(previous.get("heat_flux"))
        new_heat_flux = _safe_float(current.get("heat_flux"))

        if (
            old_heat_flux is not None
            and new_heat_flux is not None
            and old_heat_flux > 0
            and new_heat_flux > 0
        ):
            ratio = max(old_heat_flux, new_heat_flux) / min(old_heat_flux, new_heat_flux)

            if ratio > max_heat_flux_jump_fraction:
                warnings.append(
                    {
                        "from_x": previous_x,
                        "to_x": current_x,
                        "parameter": "heat_flux",
                        "jump_ratio": ratio,
                        "limit": max_heat_flux_jump_fraction,
                        "message": "Heat flux changes sharply between adjacent thermal points.",
                    }
                )

        previous = current

    return {
        "thermal_gradient_constraint_pass": len(errors) == 0,
        "thermal_gradient_constraint_status": (
            "PASS_REGEN_THERMAL_GEOMETRY_GRADIENT_CONSTRAINTS"
            if len(errors) == 0
            else "FAIL_REGEN_THERMAL_GEOMETRY_GRADIENT_CONSTRAINTS"
        ),
        "errors": errors,
        "warnings": warnings,
    }


def validate_thermal_geometry_profile_constraints(
    profile_points,
    max_allowable_wall_temperature=900.0,
    maximum_hot_wall_temperature=900.0,
    maximum_coolant_temperature=500.0,
    maximum_total_pressure_drop=2.0e6,
    maximum_point_pressure_drop=2.0e6,
    minimum_thermal_margin=0.0,
    max_wall_temperature_jump=250.0,
    max_coolant_temperature_jump=150.0,
    max_heat_flux_jump_fraction=3.0,
):
    errors = []
    warnings = []

    profile = build_thermal_geometry_profile(
        profile_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    if not profile.get("regen_thermal_geometry_profile_pass", False):
        errors.append("Thermal geometry profile failed before constraint validation.")
        errors.extend(profile.get("errors", []))

    points = profile.get("points", [])

    point_results = []

    for index, point in enumerate(points):
        point_result = validate_thermal_geometry_point_constraints(
            point,
            index=index,
            maximum_hot_wall_temperature=maximum_hot_wall_temperature,
            maximum_coolant_temperature=maximum_coolant_temperature,
            maximum_pressure_drop=maximum_point_pressure_drop,
            minimum_thermal_margin=minimum_thermal_margin,
        )

        point_results.append(point_result)

        errors.extend(point_result.get("errors", []))
        warnings.extend(point_result.get("warnings", []))

    total_pressure_drop = _safe_float(profile.get("total_pressure_drop"))

    if (
        total_pressure_drop is not None
        and total_pressure_drop > maximum_total_pressure_drop
    ):
        errors.append("Total thermal profile pressure drop exceeds limit.")

    minimum_margin = _safe_float(profile.get("minimum_thermal_margin"))

    if minimum_margin is not None and minimum_margin < minimum_thermal_margin:
        errors.append("Minimum profile thermal margin is below limit.")

    gradient_result = validate_thermal_geometry_gradient_constraints(
        points,
        max_wall_temperature_jump=max_wall_temperature_jump,
        max_coolant_temperature_jump=max_coolant_temperature_jump,
        max_heat_flux_jump_fraction=max_heat_flux_jump_fraction,
    )

    errors.extend(gradient_result.get("errors", []))
    warnings.extend(gradient_result.get("warnings", []))

    point_fail_count = sum(
        1 for result in point_results
        if not result.get("thermal_point_constraint_pass", False)
    )

    constraint_pass = (
        len(errors) == 0
        and point_fail_count == 0
        and gradient_result.get("thermal_gradient_constraint_pass", False)
    )

    return {
        "regen_thermal_geometry_constraint_owner_status": (
            PASS_STATUS if constraint_pass else FAIL_STATUS
        ),
        "regen_thermal_geometry_constraint_owner_pass": constraint_pass,
        "profile": profile,
        "point_constraint_results": point_results,
        "point_constraint_fail_count": point_fail_count,
        "gradient_constraint_result": gradient_result,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_thermal_geometry_constraint_owner_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_thermal_geometry_constraint_owner_status": result.get(
            "regen_thermal_geometry_constraint_owner_status"
        ),
        f"{prefix}_regen_thermal_geometry_constraint_owner_pass": (
            1.0 if result.get("regen_thermal_geometry_constraint_owner_pass") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_constraint_point_fail_count": float(
            result.get("point_constraint_fail_count", 0)
        ),
        f"{prefix}_regen_thermal_geometry_constraint_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_constraint_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_thermal_geometry_gradient_constraint_status": (
            result.get("gradient_constraint_result", {}).get(
                "thermal_gradient_constraint_status"
            )
        ),
        f"{prefix}_regen_thermal_geometry_gradient_constraint_pass": (
            1.0
            if result.get("gradient_constraint_result", {}).get(
                "thermal_gradient_constraint_pass"
            )
            else 0.0
        ),
    }

    for index, point_result in enumerate(result.get("point_constraint_results", [])):
        point_prefix = f"{prefix}_regen_thermal_geometry_constraint_point_{index + 1}"
        flat.update(
            {
                f"{point_prefix}_status": point_result.get(
                    "thermal_point_constraint_status"
                ),
                f"{point_prefix}_pass": (
                    1.0
                    if point_result.get("thermal_point_constraint_pass")
                    else 0.0
                ),
                f"{point_prefix}_x": point_result.get("axial_position"),
                f"{point_prefix}_error_count": float(
                    len(point_result.get("errors", []))
                ),
                f"{point_prefix}_warning_count": float(
                    len(point_result.get("warnings", []))
                ),
            }
        )

    return flat