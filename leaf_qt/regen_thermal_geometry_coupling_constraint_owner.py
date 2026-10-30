import math

try:
    from regen_thermal_geometry_coupling import build_coupled_thermal_geometry_profile
except Exception:
    from leaf_qt.regen_thermal_geometry_coupling import build_coupled_thermal_geometry_profile


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_CONSTRAINT_OWNER"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_COUPLING_CONSTRAINT_OWNER"


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


def validate_coupled_station_constraints(
    point,
    index,
    minimum_channel_width=0.0002,
    minimum_channel_height=0.0002,
    minimum_rib_width=0.0002,
    minimum_hydraulic_diameter=0.0002,
    maximum_hot_wall_temperature=900.0,
    maximum_coolant_temperature=500.0,
    maximum_point_pressure_drop=2.0e6,
    minimum_thermal_margin=0.0,
):
    errors = []
    warnings = []

    channel_width = _safe_float(point.get("channel_width"))
    channel_height = _safe_float(point.get("channel_height"))
    rib_width = _safe_float(point.get("rib_width"))
    hydraulic_diameter = _safe_float(point.get("hydraulic_diameter"))

    heat_flux = _safe_float(point.get("heat_flux"))
    wall_temperature = _safe_float(point.get("hot_wall_temperature"))
    coolant_temperature = _safe_float(point.get("coolant_temperature"))
    pressure_drop = _safe_float(point.get("pressure_drop"))
    thermal_margin = _safe_float(point.get("thermal_margin"))

    if channel_width is None or channel_width < minimum_channel_width:
        errors.append(f"Point {index}: channel width below minimum or invalid.")

    if channel_height is None or channel_height < minimum_channel_height:
        errors.append(f"Point {index}: channel height below minimum or invalid.")

    if rib_width is None or rib_width < minimum_rib_width:
        errors.append(f"Point {index}: rib width below minimum or invalid.")

    if hydraulic_diameter is None or hydraulic_diameter < minimum_hydraulic_diameter:
        errors.append(f"Point {index}: hydraulic diameter below minimum or invalid.")

    if heat_flux is None or heat_flux < 0:
        errors.append(f"Point {index}: heat flux invalid.")

    if wall_temperature is None or wall_temperature <= 0:
        errors.append(f"Point {index}: wall temperature invalid.")
    elif wall_temperature > maximum_hot_wall_temperature:
        errors.append(f"Point {index}: wall temperature exceeds limit.")

    if coolant_temperature is None or coolant_temperature <= 0:
        errors.append(f"Point {index}: coolant temperature invalid.")
    elif coolant_temperature > maximum_coolant_temperature:
        errors.append(f"Point {index}: coolant temperature exceeds limit.")

    if pressure_drop is None or pressure_drop < 0:
        errors.append(f"Point {index}: pressure drop invalid.")
    elif pressure_drop > maximum_point_pressure_drop:
        errors.append(f"Point {index}: pressure drop exceeds point limit.")

    if thermal_margin is not None and thermal_margin < minimum_thermal_margin:
        errors.append(f"Point {index}: thermal margin below minimum.")

    if (
        thermal_margin is not None
        and thermal_margin >= minimum_thermal_margin
        and thermal_margin < 25.0
    ):
        warnings.append(f"Point {index}: thermal margin is positive but small.")

    return {
        "point_index": index,
        "axial_position": point.get("axial_position"),
        "coupled_station_constraint_pass": len(errors) == 0,
        "coupled_station_constraint_status": (
            "PASS_REGEN_THERMAL_GEOMETRY_COUPLED_STATION_CONSTRAINTS"
            if len(errors) == 0
            else "FAIL_REGEN_THERMAL_GEOMETRY_COUPLED_STATION_CONSTRAINTS"
        ),
        "errors": errors,
        "warnings": warnings,
    }


def validate_coupled_gradient_constraints(
    coupled_points,
    max_channel_width_jump_fraction=1.5,
    max_channel_height_jump_fraction=1.5,
    max_wall_temperature_jump=250.0,
    max_heat_flux_jump_fraction=3.0,
):
    errors = []
    warnings = []

    previous = None

    for current in coupled_points:
        if previous is None:
            previous = current
            continue

        previous_x = _safe_float(previous.get("axial_position"))
        current_x = _safe_float(current.get("axial_position"))

        if previous_x is None or current_x is None:
            errors.append("Missing axial position in coupled gradient validation.")
            previous = current
            continue

        if current_x <= previous_x:
            errors.append("Coupled thermal-geometry axial positions must strictly increase.")
            previous = current
            continue

        ratio_checks = [
            ("channel_width", max_channel_width_jump_fraction),
            ("channel_height", max_channel_height_jump_fraction),
            ("heat_flux", max_heat_flux_jump_fraction),
        ]

        for key, limit in ratio_checks:
            old_value = _safe_float(previous.get(key))
            new_value = _safe_float(current.get(key))

            if old_value is None or new_value is None or old_value <= 0 or new_value <= 0:
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
                        "message": f"{key} changes sharply between adjacent coupled points.",
                    }
                )

        old_wall = _safe_float(previous.get("hot_wall_temperature"))
        new_wall = _safe_float(current.get("hot_wall_temperature"))

        if old_wall is not None and new_wall is not None:
            jump = abs(new_wall - old_wall)
            if jump > max_wall_temperature_jump:
                warnings.append(
                    {
                        "from_x": previous_x,
                        "to_x": current_x,
                        "parameter": "hot_wall_temperature",
                        "jump": jump,
                        "limit": max_wall_temperature_jump,
                        "message": "Wall temperature changes sharply between adjacent coupled points.",
                    }
                )

        previous = current

    return {
        "coupled_gradient_constraint_pass": len(errors) == 0,
        "coupled_gradient_constraint_status": (
            "PASS_REGEN_THERMAL_GEOMETRY_COUPLED_GRADIENT_CONSTRAINTS"
            if len(errors) == 0
            else "FAIL_REGEN_THERMAL_GEOMETRY_COUPLED_GRADIENT_CONSTRAINTS"
        ),
        "errors": errors,
        "warnings": warnings,
    }


def validate_coupled_thermal_geometry_constraints(
    variable_geometry_points,
    thermal_geometry_points,
    sample_positions=None,
    max_allowable_wall_temperature=900.0,
    maximum_hot_wall_temperature=900.0,
    maximum_coolant_temperature=500.0,
    maximum_total_pressure_drop=2.0e6,
    maximum_point_pressure_drop=2.0e6,
    minimum_thermal_margin=0.0,
    minimum_channel_width=0.0002,
    minimum_channel_height=0.0002,
    minimum_rib_width=0.0002,
    minimum_hydraulic_diameter=0.0002,
):
    errors = []
    warnings = []

    coupling_result = build_coupled_thermal_geometry_profile(
        variable_geometry_points=variable_geometry_points,
        thermal_geometry_points=thermal_geometry_points,
        sample_positions=sample_positions,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    if not coupling_result.get("regen_thermal_geometry_coupling_pass", False):
        errors.append("Thermal-geometry coupling failed before constraint validation.")
        errors.extend(coupling_result.get("errors", []))

    coupled_points = coupling_result.get("coupled_points", [])

    point_results = []

    for index, point in enumerate(coupled_points):
        point_result = validate_coupled_station_constraints(
            point,
            index=index,
            minimum_channel_width=minimum_channel_width,
            minimum_channel_height=minimum_channel_height,
            minimum_rib_width=minimum_rib_width,
            minimum_hydraulic_diameter=minimum_hydraulic_diameter,
            maximum_hot_wall_temperature=maximum_hot_wall_temperature,
            maximum_coolant_temperature=maximum_coolant_temperature,
            maximum_point_pressure_drop=maximum_point_pressure_drop,
            minimum_thermal_margin=minimum_thermal_margin,
        )

        point_results.append(point_result)
        errors.extend(point_result.get("errors", []))
        warnings.extend(point_result.get("warnings", []))

    total_pressure_drop = sum(
        _safe_float(point.get("pressure_drop"), 0.0)
        for point in coupled_points
    )

    if total_pressure_drop > maximum_total_pressure_drop:
        errors.append("Coupled profile total pressure drop exceeds limit.")

    gradient_result = validate_coupled_gradient_constraints(coupled_points)

    errors.extend(gradient_result.get("errors", []))
    warnings.extend(gradient_result.get("warnings", []))

    point_fail_count = sum(
        1 for result in point_results
        if not result.get("coupled_station_constraint_pass", False)
    )

    constraint_pass = (
        len(errors) == 0
        and point_fail_count == 0
        and gradient_result.get("coupled_gradient_constraint_pass", False)
    )

    return {
        "regen_thermal_geometry_coupling_constraint_owner_status": (
            PASS_STATUS if constraint_pass else FAIL_STATUS
        ),
        "regen_thermal_geometry_coupling_constraint_owner_pass": constraint_pass,
        "coupling_result": coupling_result,
        "point_constraint_results": point_results,
        "point_constraint_fail_count": point_fail_count,
        "gradient_constraint_result": gradient_result,
        "total_pressure_drop": total_pressure_drop,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_coupled_thermal_geometry_constraint_owner_result(
    result,
    prefix="recommended",
):
    flat = {
        f"{prefix}_regen_thermal_geometry_coupling_constraint_owner_status": result.get(
            "regen_thermal_geometry_coupling_constraint_owner_status"
        ),
        f"{prefix}_regen_thermal_geometry_coupling_constraint_owner_pass": (
            1.0
            if result.get("regen_thermal_geometry_coupling_constraint_owner_pass")
            else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_coupling_constraint_point_fail_count": float(
            result.get("point_constraint_fail_count", 0)
        ),
        f"{prefix}_regen_thermal_geometry_coupling_constraint_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_coupling_constraint_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_thermal_geometry_coupling_total_pressure_drop": result.get(
            "total_pressure_drop"
        ),
        f"{prefix}_regen_thermal_geometry_coupling_gradient_constraint_status": (
            result.get("gradient_constraint_result", {}).get(
                "coupled_gradient_constraint_status"
            )
        ),
        f"{prefix}_regen_thermal_geometry_coupling_gradient_constraint_pass": (
            1.0
            if result.get("gradient_constraint_result", {}).get(
                "coupled_gradient_constraint_pass"
            )
            else 0.0
        ),
    }

    for index, point_result in enumerate(result.get("point_constraint_results", [])):
        point_prefix = f"{prefix}_regen_thermal_geometry_coupling_constraint_point_{index + 1}"
        flat.update(
            {
                f"{point_prefix}_status": point_result.get(
                    "coupled_station_constraint_status"
                ),
                f"{point_prefix}_pass": (
                    1.0
                    if point_result.get("coupled_station_constraint_pass")
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