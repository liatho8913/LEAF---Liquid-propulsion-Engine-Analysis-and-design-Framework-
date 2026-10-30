PASS_STATUS = "PASS_REGEN_AXIAL_GEOMETRY_REPORT_OWNER"
FAIL_STATUS = "FAIL_REGEN_AXIAL_GEOMETRY_REPORT_OWNER"


def _fmt(value, unit="", digits=6):
    try:
        if value is None:
            return "N/A"
        value = float(value)
        return f"{value:.{digits}g}{unit}"
    except Exception:
        return str(value)


def _candidate_line(candidate):
    if not candidate:
        return "No valid candidate was selected."

    return (
        f"Channels: {_fmt(candidate.get('channel_count'), digits=0)}, "
        f"Width: {_fmt(candidate.get('channel_width'), ' m')}, "
        f"Height: {_fmt(candidate.get('channel_height'), ' m')}, "
        f"Rib: {_fmt(candidate.get('rib_width'), ' m')}, "
        f"Dh: {_fmt(candidate.get('hydraulic_diameter'), ' m')}, "
        f"Velocity: {_fmt(candidate.get('coolant_velocity'), ' m/s')}, "
        f"Re: {_fmt(candidate.get('reynolds_number'), digits=0)}"
    )


def generate_regen_axial_station_report(station_result, station_constraint=None):
    station_id = station_result.get("station_id", "unknown_station")
    station_name = station_result.get("station_name", station_id)

    lines = []

    lines.append(f"Station: {station_name}")
    lines.append(f"Station ID: {station_id}")
    lines.append(f"Axial Position: {_fmt(station_result.get('axial_position'), ' m')}")
    lines.append(f"Local Radius: {_fmt(station_result.get('local_radius'), ' m')}")
    lines.append(f"Solver Status: {station_result.get('station_solver_status', 'N/A')}")
    lines.append(f"Solver Pass: {station_result.get('station_solver_pass', 'N/A')}")
    lines.append("")
    lines.append("Selected Geometry:")
    lines.append(_candidate_line(station_result.get("best_candidate") or {}))

    if station_constraint:
        lines.append("")
        lines.append("Constraint Result:")
        lines.append(f"Constraint Status: {station_constraint.get('station_constraint_status', 'N/A')}")
        lines.append(f"Constraint Pass: {station_constraint.get('station_constraint_pass', 'N/A')}")

        errors = station_constraint.get("errors", [])
        warnings = station_constraint.get("warnings", [])

        if errors:
            lines.append("Errors:")
            for error in errors:
                lines.append(f"- {error}")

        if warnings:
            lines.append("Warnings:")
            for warning in warnings:
                lines.append(f"- {warning}")

        if not errors and not warnings:
            lines.append("No station-level errors or warnings were reported.")

    return "\n".join(lines)


def generate_regen_axial_geometry_report(
    axial_geometry_result,
    axial_constraint_result=None,
):
    errors = []
    warnings = []
    lines = []

    station_results = axial_geometry_result.get("station_results", [])

    if not station_results:
        errors.append("No station results were available for axial report generation.")

    constraint_by_station = {}

    if axial_constraint_result:
        for station_constraint in axial_constraint_result.get("station_constraint_results", []):
            constraint_by_station[station_constraint.get("station_id")] = station_constraint

    lines.append("LEAF REGEN AXIAL GEOMETRY REPORT")
    lines.append("=" * 40)
    lines.append("")
    lines.append("Whole-Engine Summary")
    lines.append("-" * 40)
    lines.append(
        f"Axial Solver Status: "
        f"{axial_geometry_result.get('axial_geometry_solver_status', 'N/A')}"
    )
    lines.append(
        f"Axial Solver Pass: "
        f"{axial_geometry_result.get('axial_geometry_solver_pass', 'N/A')}"
    )
    lines.append(
        f"Station Count: "
        f"{axial_geometry_result.get('station_count', len(station_results))}"
    )
    lines.append(
        f"Station Pass Count: "
        f"{axial_geometry_result.get('station_pass_count', 'N/A')}"
    )
    lines.append(
        f"Station Fail Count: "
        f"{axial_geometry_result.get('station_fail_count', 'N/A')}"
    )

    if axial_constraint_result:
        lines.append("")
        lines.append("Constraint Owner Summary")
        lines.append("-" * 40)
        lines.append(
            f"Constraint Owner Status: "
            f"{axial_constraint_result.get('regen_axial_constraint_owner_status', 'N/A')}"
        )
        lines.append(
            f"Constraint Owner Pass: "
            f"{axial_constraint_result.get('regen_axial_constraint_owner_pass', 'N/A')}"
        )
        lines.append(
            f"Constraint Station Fail Count: "
            f"{axial_constraint_result.get('station_constraint_fail_count', 'N/A')}"
        )

        if axial_constraint_result.get("errors"):
            lines.append("")
            lines.append("Whole-Engine Errors:")
            for error in axial_constraint_result.get("errors", []):
                lines.append(f"- {error}")

        if axial_constraint_result.get("warnings"):
            lines.append("")
            lines.append("Whole-Engine Warnings:")
            for warning in axial_constraint_result.get("warnings", []):
                lines.append(f"- {warning}")

    lines.append("")
    lines.append("Station-by-Station Results")
    lines.append("=" * 40)

    for index, station_result in enumerate(station_results):
        if index > 0:
            lines.append("")
            lines.append("-" * 40)

        station_constraint = constraint_by_station.get(station_result.get("station_id"))
        lines.append(generate_regen_axial_station_report(station_result, station_constraint))

    report_pass = len(errors) == 0 and len(station_results) > 0

    return {
        "regen_axial_report_owner_status": PASS_STATUS if report_pass else FAIL_STATUS,
        "regen_axial_report_owner_pass": report_pass,
        "report_text": "\n".join(lines),
        "station_report_count": len(station_results),
        "errors": errors,
        "warnings": warnings,
    }


def flatten_regen_axial_report_owner_result(result, prefix="recommended"):
    return {
        f"{prefix}_regen_axial_report_owner_status": result.get(
            "regen_axial_report_owner_status"
        ),
        f"{prefix}_regen_axial_report_owner_pass": (
            1.0 if result.get("regen_axial_report_owner_pass") else 0.0
        ),
        f"{prefix}_regen_axial_report_station_count": float(
            result.get("station_report_count", 0)
        ),
        f"{prefix}_regen_axial_report_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_axial_report_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_axial_report_text": result.get("report_text", ""),
    }