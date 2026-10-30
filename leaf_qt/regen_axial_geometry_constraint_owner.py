import math


PASS_STATUS = "PASS_REGEN_AXIAL_GEOMETRY_CONSTRAINT_OWNER"
FAIL_STATUS = "FAIL_REGEN_AXIAL_GEOMETRY_CONSTRAINT_OWNER"


def _is_number(value):
    try:
        if value is None:
            return False
        value = float(value)
        return not math.isnan(value) and not math.isinf(value)
    except Exception:
        return False


def _as_float(value, default=None):
    try:
        if value is None:
            return default
        value = float(value)
        if math.isnan(value) or math.isinf(value):
            return default
        return value
    except Exception:
        return default


def _candidate_value(candidate, *keys):
    for key in keys:
        if key in candidate:
            return candidate.get(key)
    return None


def validate_axial_station_constraints(station_result, index=None):
    errors = []
    warnings = []

    station_id = station_result.get("station_id", f"station_{index}")
    station_name = station_result.get("station_name", station_id)

    local_radius = _as_float(station_result.get("local_radius"))
    axial_position = _as_float(station_result.get("axial_position"))

    if not _is_number(axial_position):
        errors.append("Missing or invalid axial position.")

    if not _is_number(local_radius) or local_radius <= 0:
        errors.append("Missing or invalid local radius.")

    candidate = station_result.get("best_candidate") or {}

    if not candidate:
        errors.append("Missing best regen geometry candidate.")
        return {
            "station_id": station_id,
            "station_name": station_name,
            "station_constraint_pass": False,
            "station_constraint_status": "FAIL_REGEN_AXIAL_STATION_CONSTRAINTS",
            "errors": errors,
            "warnings": warnings,
        }

    channel_count = _as_float(_candidate_value(candidate, "channel_count"))
    channel_width = _as_float(_candidate_value(candidate, "channel_width"))
    channel_height = _as_float(_candidate_value(candidate, "channel_height"))
    rib_width = _as_float(_candidate_value(candidate, "rib_width"))
    hydraulic_diameter = _as_float(_candidate_value(candidate, "hydraulic_diameter"))
    coolant_velocity = _as_float(_candidate_value(candidate, "coolant_velocity"))
    reynolds_number = _as_float(_candidate_value(candidate, "reynolds_number"))
    pressure_drop = _as_float(
        _candidate_value(candidate, "estimated_pressure_drop", "pressure_drop")
    )
    coverage = _as_float(
        _candidate_value(candidate, "circumferential_coverage", "coverage")
    )

    if not _is_number(channel_count) or channel_count <= 0:
        errors.append("Invalid channel count.")

    if not _is_number(channel_width) or channel_width <= 0:
        errors.append("Invalid channel width.")

    if not _is_number(channel_height) or channel_height <= 0:
        errors.append("Invalid channel height.")

    if not _is_number(rib_width) or rib_width <= 0:
        errors.append("Invalid rib width.")

    if not _is_number(hydraulic_diameter) or hydraulic_diameter <= 0:
        errors.append("Invalid hydraulic diameter.")

    if _is_number(coolant_velocity) and coolant_velocity <= 0:
        errors.append("Invalid coolant velocity.")

    if _is_number(reynolds_number) and reynolds_number < 2300:
        warnings.append("Coolant Reynolds number is laminar or transitional.")

    if _is_number(pressure_drop) and pressure_drop < 0:
        errors.append("Negative pressure drop is invalid.")

    if _is_number(coverage) and not (0 <= coverage <= 1.0):
        errors.append("Cooling coverage must be between 0 and 1.")

    if (
        _is_number(local_radius)
        and _is_number(channel_count)
        and _is_number(channel_width)
        and _is_number(rib_width)
    ):
        circumference = 2.0 * math.pi * local_radius
        required_pitch_circumference = channel_count * (channel_width + rib_width)

        if required_pitch_circumference > circumference * 1.000001:
            errors.append(
                "Channel pitch does not fit local circumference."
            )

    station_pass = len(errors) == 0

    return {
        "station_id": station_id,
        "station_name": station_name,
        "station_constraint_pass": station_pass,
        "station_constraint_status": (
            "PASS_REGEN_AXIAL_STATION_CONSTRAINTS"
            if station_pass
            else "FAIL_REGEN_AXIAL_STATION_CONSTRAINTS"
        ),
        "errors": errors,
        "warnings": warnings,
    }


def validate_axial_position_order(station_results):
    errors = []
    warnings = []

    previous_position = None
    previous_station = None

    for station in station_results:
        position = _as_float(station.get("axial_position"))
        station_id = station.get("station_id")

        if position is None:
            errors.append(f"{station_id}: missing axial position.")
            continue

        if previous_position is not None and position < previous_position:
            errors.append(
                f"{station_id}: axial position is behind previous station {previous_station}."
            )

        if previous_position is not None and position == previous_position:
            warnings.append(
                f"{station_id}: axial position is identical to previous station {previous_station}."
            )

        previous_position = position
        previous_station = station_id

    return {
        "axial_position_order_pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_axial_continuity(
    station_results,
    max_channel_width_jump_fraction=1.50,
    max_channel_height_jump_fraction=1.50,
    max_rib_width_jump_fraction=1.50,
):
    warnings = []
    errors = []

    previous = None

    for current in station_results:
        if previous is None:
            previous = current
            continue

        previous_candidate = previous.get("best_candidate") or {}
        current_candidate = current.get("best_candidate") or {}

        checks = [
            (
                "channel_width",
                max_channel_width_jump_fraction,
                "Channel width jump is large between adjacent stations.",
            ),
            (
                "channel_height",
                max_channel_height_jump_fraction,
                "Channel height jump is large between adjacent stations.",
            ),
            (
                "rib_width",
                max_rib_width_jump_fraction,
                "Rib width jump is large between adjacent stations.",
            ),
        ]

        for key, limit, message in checks:
            old_value = _as_float(previous_candidate.get(key))
            new_value = _as_float(current_candidate.get(key))

            if old_value is None or new_value is None or old_value <= 0 or new_value <= 0:
                continue

            ratio = max(old_value, new_value) / min(old_value, new_value)

            if ratio > limit:
                warnings.append(
                    {
                        "from_station": previous.get("station_id"),
                        "to_station": current.get("station_id"),
                        "parameter": key,
                        "jump_ratio": ratio,
                        "message": message,
                    }
                )

        previous = current

    return {
        "axial_continuity_pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def validate_regen_axial_geometry_constraints(axial_geometry_result):
    errors = []
    warnings = []

    station_results = axial_geometry_result.get("station_results", [])

    if not station_results:
        errors.append("No axial station results were provided.")

    profile = axial_geometry_result.get("axial_station_profile", {})

    if profile and not profile.get("axial_station_profile_pass", False):
        errors.append("Axial station profile failed before constraint validation.")

    station_constraint_results = []

    for index, station_result in enumerate(station_results):
        station_constraint = validate_axial_station_constraints(
            station_result=station_result,
            index=index,
        )
        station_constraint_results.append(station_constraint)

        for error in station_constraint.get("errors", []):
            errors.append(f"{station_constraint['station_id']}: {error}")

        for warning in station_constraint.get("warnings", []):
            warnings.append(f"{station_constraint['station_id']}: {warning}")

    order_check = validate_axial_position_order(station_results)
    continuity_check = validate_axial_continuity(station_results)

    errors.extend(order_check.get("errors", []))
    warnings.extend(order_check.get("warnings", []))
    errors.extend(continuity_check.get("errors", []))
    warnings.extend(continuity_check.get("warnings", []))

    station_fail_count = sum(
        1 for result in station_constraint_results
        if not result.get("station_constraint_pass")
    )

    constraint_pass = len(errors) == 0 and station_fail_count == 0

    return {
        "regen_axial_constraint_owner_status": (
            PASS_STATUS if constraint_pass else FAIL_STATUS
        ),
        "regen_axial_constraint_owner_pass": constraint_pass,
        "station_constraint_results": station_constraint_results,
        "station_constraint_fail_count": station_fail_count,
        "axial_position_order_check": order_check,
        "axial_continuity_check": continuity_check,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_regen_axial_constraint_owner_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_axial_constraint_owner_status": result.get(
            "regen_axial_constraint_owner_status"
        ),
        f"{prefix}_regen_axial_constraint_owner_pass": (
            1.0 if result.get("regen_axial_constraint_owner_pass") else 0.0
        ),
        f"{prefix}_regen_axial_constraint_station_fail_count": float(
            result.get("station_constraint_fail_count", 0)
        ),
        f"{prefix}_regen_axial_constraint_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_axial_constraint_warning_count": float(
            len(result.get("warnings", []))
        ),
    }

    for index, station_result in enumerate(result.get("station_constraint_results", [])):
        station_prefix = f"{prefix}_regen_axial_constraint_station_{index + 1}"

        flat.update(
            {
                f"{station_prefix}_id": station_result.get("station_id"),
                f"{station_prefix}_name": station_result.get("station_name"),
                f"{station_prefix}_status": station_result.get("station_constraint_status"),
                f"{station_prefix}_pass": (
                    1.0 if station_result.get("station_constraint_pass") else 0.0
                ),
                f"{station_prefix}_error_count": float(
                    len(station_result.get("errors", []))
                ),
                f"{station_prefix}_warning_count": float(
                    len(station_result.get("warnings", []))
                ),
            }
        )

    return flat