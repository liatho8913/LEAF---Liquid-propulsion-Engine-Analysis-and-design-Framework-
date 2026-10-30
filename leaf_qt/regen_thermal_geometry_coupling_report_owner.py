try:
    from regen_thermal_geometry_coupling import build_coupled_thermal_geometry_profile
    from regen_thermal_geometry_coupling_constraint_owner import (
        validate_coupled_thermal_geometry_constraints,
    )
except Exception:
    from leaf_qt.regen_thermal_geometry_coupling import build_coupled_thermal_geometry_profile
    from leaf_qt.regen_thermal_geometry_coupling_constraint_owner import (
        validate_coupled_thermal_geometry_constraints,
    )


PASS_STATUS = "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_REPORT_OWNER"
FAIL_STATUS = "FAIL_REGEN_THERMAL_GEOMETRY_COUPLING_REPORT_OWNER"


def _fmt(value, unit="", digits=6):
    try:
        if value is None:
            return "N/A"
        return f"{float(value):.{digits}g}{unit}"
    except Exception:
        return str(value)


def generate_coupled_thermal_geometry_report(
    variable_geometry_points,
    thermal_geometry_points,
    sample_positions=None,
    constraint_result=None,
    max_allowable_wall_temperature=900.0,
):
    errors = []
    warnings = []

    coupling_result = build_coupled_thermal_geometry_profile(
        variable_geometry_points=variable_geometry_points,
        thermal_geometry_points=thermal_geometry_points,
        sample_positions=sample_positions,
        max_allowable_wall_temperature=max_allowable_wall_temperature,
    )

    if constraint_result is None:
        constraint_result = validate_coupled_thermal_geometry_constraints(
            variable_geometry_points=variable_geometry_points,
            thermal_geometry_points=thermal_geometry_points,
            sample_positions=sample_positions,
            max_allowable_wall_temperature=max_allowable_wall_temperature,
        )

    lines = []

    lines.append("LEAF THERMAL-GEOMETRY COUPLING REPORT")
    lines.append("=" * 58)
    lines.append("")
    lines.append("Coupling Summary")
    lines.append("-" * 58)
    lines.append(
        f"Coupling Status: "
        f"{coupling_result.get('regen_thermal_geometry_coupling_status')}"
    )
    lines.append(
        f"Coupling Pass: "
        f"{coupling_result.get('regen_thermal_geometry_coupling_pass')}"
    )
    lines.append(
        f"Coupled Point Count: "
        f"{coupling_result.get('coupled_point_count')}"
    )

    lines.append("")
    lines.append("Constraint Summary")
    lines.append("-" * 58)
    lines.append(
        f"Constraint Owner Status: "
        f"{constraint_result.get('regen_thermal_geometry_coupling_constraint_owner_status')}"
    )
    lines.append(
        f"Constraint Owner Pass: "
        f"{constraint_result.get('regen_thermal_geometry_coupling_constraint_owner_pass')}"
    )
    lines.append(
        f"Coupled Point Fail Count: "
        f"{constraint_result.get('point_constraint_fail_count')}"
    )
    lines.append(
        f"Total Pressure Drop: "
        f"{_fmt(constraint_result.get('total_pressure_drop'), ' Pa')}"
    )

    gradient_result = constraint_result.get("gradient_constraint_result", {})
    lines.append(
        f"Coupled Gradient Status: "
        f"{gradient_result.get('coupled_gradient_constraint_status')}"
    )
    lines.append(
        f"Coupled Gradient Pass: "
        f"{gradient_result.get('coupled_gradient_constraint_pass')}"
    )

    lines.append("")
    lines.append("Coupled Station Results")
    lines.append("-" * 58)

    point_constraints = {
        result.get("point_index"): result
        for result in constraint_result.get("point_constraint_results", [])
    }

    for index, point in enumerate(coupling_result.get("coupled_points", [])):
        point_constraint = point_constraints.get(index, {})

        lines.append(
            f"{index + 1}. x={_fmt(point.get('axial_position'), ' m')} | "
            f"cw={_fmt(point.get('channel_width'), ' m')} | "
            f"ch={_fmt(point.get('channel_height'), ' m')} | "
            f"rib={_fmt(point.get('rib_width'), ' m')} | "
            f"Dh={_fmt(point.get('hydraulic_diameter'), ' m')} | "
            f"q={_fmt(point.get('heat_flux'), ' W/m^2')} | "
            f"Twall={_fmt(point.get('hot_wall_temperature'), ' K')} | "
            f"Tcool={_fmt(point.get('coolant_temperature'), ' K')} | "
            f"dp={_fmt(point.get('pressure_drop'), ' Pa')} | "
            f"margin={_fmt(point.get('thermal_margin'), ' K')} | "
            f"status={point_constraint.get('coupled_station_constraint_status', 'N/A')}"
        )

    unsafe_points = [
        result
        for result in constraint_result.get("point_constraint_results", [])
        if not result.get("coupled_station_constraint_pass", False)
    ]

    lines.append("")
    lines.append("Coupled Safety Summary")
    lines.append("-" * 58)

    if unsafe_points:
        lines.append("Unsafe Coupled Stations:")
        for result in unsafe_points:
            lines.append(
                f"- Point {result.get('point_index')} at "
                f"x={_fmt(result.get('axial_position'), ' m')}: "
                f"{result.get('coupled_station_constraint_status')}"
            )
            for error in result.get("errors", []):
                lines.append(f"  - {error}")
    else:
        lines.append("No unsafe coupled stations were reported.")

    if constraint_result.get("warnings"):
        lines.append("")
        lines.append("Warnings")
        lines.append("-" * 58)
        for warning in constraint_result.get("warnings", []):
            lines.append(f"- {warning}")

    if constraint_result.get("errors"):
        lines.append("")
        lines.append("Errors")
        lines.append("-" * 58)
        for error in constraint_result.get("errors", []):
            lines.append(f"- {error}")

    if not constraint_result.get("errors") and not constraint_result.get("warnings"):
        lines.append("")
        lines.append("Coupled Readiness Summary")
        lines.append("-" * 58)
        lines.append(
            "No coupled thermal-geometry errors or coupled gradient warnings were reported."
        )
        lines.append(
            "This does not mean the engine is optimised; it means the current "
            "geometry and thermal profiles are compatible under the Phase 5C "
            "backend checks."
        )

    report_pass = (
        coupling_result.get("regen_thermal_geometry_coupling_pass", False)
        and len(errors) == 0
    )

    return {
        "regen_thermal_geometry_coupling_report_owner_status": (
            PASS_STATUS if report_pass else FAIL_STATUS
        ),
        "regen_thermal_geometry_coupling_report_owner_pass": report_pass,
        "report_text": "\n".join(lines),
        "coupling_result": coupling_result,
        "constraint_result": constraint_result,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_coupled_thermal_geometry_report_owner_result(
    result,
    prefix="recommended",
):
    return {
        f"{prefix}_regen_thermal_geometry_coupling_report_owner_status": result.get(
            "regen_thermal_geometry_coupling_report_owner_status"
        ),
        f"{prefix}_regen_thermal_geometry_coupling_report_owner_pass": (
            1.0
            if result.get("regen_thermal_geometry_coupling_report_owner_pass")
            else 0.0
        ),
        f"{prefix}_regen_thermal_geometry_coupling_report_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_thermal_geometry_coupling_report_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_thermal_geometry_coupling_report_text": result.get(
            "report_text", ""
        ),
    }