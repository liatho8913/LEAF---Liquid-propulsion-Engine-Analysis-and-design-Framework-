try:
    from regen_thermal_geometry_profile import build_thermal_geometry_profile
    from regen_thermal_geometry_constraint_owner import (
        validate_thermal_geometry_profile_constraints,
    )
except Exception:
    from leaf_qt.regen_thermal_geometry_profile import build_thermal_geometry_profile
    from leaf_qt.regen_thermal_geometry_constraint_owner import (
        validate_thermal_geometry_profile_constraints,
    )


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_REPORT_OWNER"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_REPORT_OWNER"


def _fmt(value, unit="", digits=6):
    try:
        if value is None:
            return "N/A"
        return f"{float(value):.{digits}g}{unit}"
    except Exception:
        return str(value)


def generate_thermal_geometry_profile_report(
    profile_points,
    constraint_result=None,
    max_allowable_wall_temperature=900.0,
):
    errors = []
    warnings = []

    profile = build_thermal_geometry_profile(
        profile_points,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    if constraint_result is None:
        constraint_result = validate_thermal_geometry_profile_constraints(
            profile_points,
            max_allowable_wall_temperature=max_allowable_wall_temperature,
        )

    lines = []

    lines.append("LEAF THERMAL REGEN GEOMETRY PROFILE REPORT")
    lines.append("=" * 54)
    lines.append("")
    lines.append("Thermal Profile Summary")
    lines.append("-" * 54)
    lines.append(f"Profile Status: {profile.get('regen_thermal_geometry_profile_status')}")
    lines.append(f"Profile Pass: {profile.get('regen_thermal_geometry_profile_pass')}")
    lines.append(f"Point Count: {profile.get('point_count')}")
    lines.append(f"Minimum Axial Position: {_fmt(profile.get('minimum_axial_position'), ' m')}")
    lines.append(f"Maximum Axial Position: {_fmt(profile.get('maximum_axial_position'), ' m')}")
    lines.append(f"Maximum Heat Flux: {_fmt(profile.get('maximum_heat_flux'), ' W/m^2')}")
    lines.append(
        f"Maximum Hot Wall Temperature: "
        f"{_fmt(profile.get('maximum_hot_wall_temperature'), ' K')}"
    )
    lines.append(
        f"Maximum Coolant Temperature: "
        f"{_fmt(profile.get('maximum_coolant_temperature'), ' K')}"
    )
    lines.append(f"Total Pressure Drop: {_fmt(profile.get('total_pressure_drop'), ' Pa')}")
    lines.append(f"Minimum Thermal Margin: {_fmt(profile.get('minimum_thermal_margin'), ' K')}")

    lines.append("")
    lines.append("Constraint Summary")
    lines.append("-" * 54)
    lines.append(
        f"Constraint Owner Status: "
        f"{constraint_result.get('regen_thermal_geometry_constraint_owner_status')}"
    )
    lines.append(
        f"Constraint Owner Pass: "
        f"{constraint_result.get('regen_thermal_geometry_constraint_owner_pass')}"
    )
    lines.append(
        f"Thermal Point Fail Count: "
        f"{constraint_result.get('point_constraint_fail_count')}"
    )

    gradient_result = constraint_result.get("gradient_constraint_result", {})
    lines.append(
        f"Gradient Constraint Status: "
        f"{gradient_result.get('thermal_gradient_constraint_status')}"
    )
    lines.append(
        f"Gradient Constraint Pass: "
        f"{gradient_result.get('thermal_gradient_constraint_pass')}"
    )

    lines.append("")
    lines.append("Thermal Profile Points")
    lines.append("-" * 54)

    for index, point in enumerate(profile.get("points", []), start=1):
        lines.append(
            f"{index}. x={_fmt(point.get('axial_position'), ' m')} | "
            f"q={_fmt(point.get('heat_flux'), ' W/m^2')} | "
            f"T_wall={_fmt(point.get('hot_wall_temperature'), ' K')} | "
            f"T_coolant={_fmt(point.get('coolant_temperature'), ' K')} | "
            f"dp={_fmt(point.get('pressure_drop'), ' Pa')} | "
            f"margin={_fmt(point.get('thermal_margin'), ' K')}"
        )

    overheated_points = []
    low_margin_points = []

    for index, point in enumerate(profile.get("points", []), start=1):
        wall_temp = point.get("hot_wall_temperature")
        margin = point.get("thermal_margin")

        try:
            if wall_temp is not None and float(wall_temp) > float(max_allowable_wall_temperature):
                overheated_points.append((index, point))
        except Exception:
            pass

        try:
            if margin is not None and float(margin) < 0.0:
                low_margin_points.append((index, point))
        except Exception:
            pass

    lines.append("")
    lines.append("Thermal Safety Summary")
    lines.append("-" * 54)

    if overheated_points:
        lines.append("Overheated Points:")
        for index, point in overheated_points:
            lines.append(
                f"- Point {index} at x={_fmt(point.get('axial_position'), ' m')} "
                f"has T_wall={_fmt(point.get('hot_wall_temperature'), ' K')}."
            )
    else:
        lines.append("No hot-wall temperature values exceed the allowable wall temperature.")

    if low_margin_points:
        lines.append("Negative Thermal Margin Points:")
        for index, point in low_margin_points:
            lines.append(
                f"- Point {index} at x={_fmt(point.get('axial_position'), ' m')} "
                f"has margin={_fmt(point.get('thermal_margin'), ' K')}."
            )
    else:
        lines.append("No negative thermal margins were found.")

    if constraint_result.get("errors"):
        lines.append("")
        lines.append("Errors")
        lines.append("-" * 54)
        for error in constraint_result.get("errors", []):
            lines.append(f"- {error}")

    if constraint_result.get("warnings"):
        lines.append("")
        lines.append("Warnings")
        lines.append("-" * 54)
        for warning in constraint_result.get("warnings", []):
            lines.append(f"- {warning}")

    if not constraint_result.get("errors") and not constraint_result.get("warnings"):
        lines.append("")
        lines.append("Thermal Readiness Summary")
        lines.append("-" * 54)
        lines.append(
            "No thermal constraint errors or thermal gradient warnings were reported."
        )
        lines.append(
            "This does not mean the cooling geometry is optimised; it means the "
            "thermal profile is acceptable for the current Phase 4C backend checks."
        )

    report_pass = (
        profile.get("regen_thermal_geometry_profile_pass", False)
        and len(errors) == 0
    )

    return {
        "regen_thermal_geometry_report_owner_status": (
            PASS_STATUS if report_pass else FAIL_STATUS
        ),
        "regen_thermal_geometry_report_owner_pass": report_pass,
        "report_text": "\n".join(lines),
        "profile": profile,
        "constraint_result": constraint_result,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_thermal_geometry_report_owner_result(result, prefix="recommended"):
    return {
        f"{prefix}_regen_thermal_geometry_report_owner_status": result.get(
            "regen_thermal_geometry_report_owner_status"
        ),
        f"{prefix}_regen_thermal_geometry_report_owner_pass": (
            1.0 if result.get("regen_thermal_geometry_report_owner_pass") else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_report_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_report_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_thermal_geometry_report_text": result.get(
            "report_text", ""
        ),
    }