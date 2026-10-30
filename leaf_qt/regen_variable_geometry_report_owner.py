try:
    from regen_variable_geometry_profile import build_variable_geometry_profile
    from regen_variable_geometry_constraint_owner import validate_variable_geometry_profile_constraints
except Exception:
    from leaf_qt.regen_variable_geometry_profile import build_variable_geometry_profile
    from leaf_qt.regen_variable_geometry_constraint_owner import validate_variable_geometry_profile_constraints


PASS_STATUS = "PASS_REGEN_VARIABLE_GEOMETRY_REPORT_OWNER"
FAIL_STATUS = "FAIL_REGEN_VARIABLE_GEOMETRY_REPORT_OWNER"


def _fmt(value, unit="", digits=6):
    try:
        if value is None:
            return "N/A"
        return f"{float(value):.{digits}g}{unit}"
    except Exception:
        return str(value)


def generate_variable_geometry_profile_report(profile_points, constraint_result=None):
    errors = []
    warnings = []

    profile = build_variable_geometry_profile(profile_points)

    if constraint_result is None:
        constraint_result = validate_variable_geometry_profile_constraints(profile_points)

    lines = []

    lines.append("LEAF VARIABLE REGEN GEOMETRY PROFILE REPORT")
    lines.append("=" * 52)
    lines.append("")
    lines.append("Profile Summary")
    lines.append("-" * 52)
    lines.append(f"Profile Status: {profile.get('regen_variable_geometry_profile_status')}")
    lines.append(f"Profile Pass: {profile.get('regen_variable_geometry_profile_pass')}")
    lines.append(f"Point Count: {profile.get('point_count')}")
    lines.append(f"Minimum Axial Position: {_fmt(profile.get('minimum_axial_position'), ' m')}")
    lines.append(f"Maximum Axial Position: {_fmt(profile.get('maximum_axial_position'), ' m')}")
    lines.append("")
    lines.append("Constraint Summary")
    lines.append("-" * 52)
    lines.append(
        f"Constraint Owner Status: "
        f"{constraint_result.get('regen_variable_geometry_constraint_owner_status')}"
    )
    lines.append(
        f"Constraint Owner Pass: "
        f"{constraint_result.get('regen_variable_geometry_constraint_owner_pass')}"
    )
    lines.append(
        f"Point Constraint Fail Count: "
        f"{constraint_result.get('point_constraint_fail_count')}"
    )

    gradient_result = constraint_result.get("gradient_constraint_result", {})
    lines.append(
        f"Gradient Constraint Status: "
        f"{gradient_result.get('variable_geometry_gradient_constraint_status')}"
    )
    lines.append(
        f"Gradient Constraint Pass: "
        f"{gradient_result.get('variable_geometry_gradient_constraint_pass')}"
    )

    lines.append("")
    lines.append("Profile Points")
    lines.append("-" * 52)

    for index, point in enumerate(profile.get("points", []), start=1):
        lines.append(
            f"{index}. x={_fmt(point.get('axial_position'), ' m')} | "
            f"channel_width={_fmt(point.get('channel_width'), ' m')} | "
            f"channel_height={_fmt(point.get('channel_height'), ' m')} | "
            f"rib_width={_fmt(point.get('rib_width'), ' m')} | "
            f"hydraulic_diameter={_fmt(point.get('hydraulic_diameter'), ' m')}"
        )

    if constraint_result.get("errors"):
        lines.append("")
        lines.append("Errors")
        lines.append("-" * 52)
        for error in constraint_result.get("errors", []):
            lines.append(f"- {error}")

    if constraint_result.get("warnings"):
        lines.append("")
        lines.append("Warnings")
        lines.append("-" * 52)
        for warning in constraint_result.get("warnings", []):
            lines.append(f"- {warning}")

    if not constraint_result.get("errors") and not constraint_result.get("warnings"):
        lines.append("")
        lines.append("Manufacturing Readiness Summary")
        lines.append("-" * 52)
        lines.append(
            "No variable-geometry constraint errors or gradient warnings were reported."
        )
        lines.append(
            "This does not mean the design is thermally optimal; it means the "
            "profile is structurally acceptable for the current Phase 3C backend checks."
        )

    report_pass = (
        profile.get("regen_variable_geometry_profile_pass", False)
        and len(errors) == 0
    )

    return {
        "regen_variable_geometry_report_owner_status": (
            PASS_STATUS if report_pass else FAIL_STATUS
        ),
        "regen_variable_geometry_report_owner_pass": report_pass,
        "report_text": "\n".join(lines),
        "profile": profile,
        "constraint_result": constraint_result,
        "errors": errors,
        "warnings": warnings,
    }


def flatten_variable_geometry_report_owner_result(result, prefix="recommended"):
    return {
        f"{prefix}_regen_variable_geometry_report_owner_status": result.get(
            "regen_variable_geometry_report_owner_status"
        ),
        f"{prefix}_regen_variable_geometry_report_owner_pass": (
            1.0 if result.get("regen_variable_geometry_report_owner_pass") else 0.0
        ),
        f"{prefix}_regen_variable_geometry_report_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_variable_geometry_report_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_variable_geometry_report_text": result.get(
            "report_text", ""
        ),
    }