from leaf_qt.status_presentation import status_severity
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity in {"PASS", "WARN", "FAIL"}:
                return severity
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

def evaluate_regen_geometry_constraints(
    candidate,
    minimum_rib_width=0.0005,
    minimum_channel_width=0.0005,
    minimum_channel_height=0.0005,
    minimum_hydraulic_diameter=None,
    maximum_coolant_velocity=None,
    pressure_drop_limit=None,
    minimum_cooling_coverage=None,
):
    failures = []
    warnings = []

    if candidate is None:
        return {
            "constraint_status": "FAIL",
            "geometry_constraints_pass": False,
            "failures": ["NO_CANDIDATE_PROVIDED"],
            "warnings": [],
        }

    channel_width = candidate.get("channel_width")
    channel_height = candidate.get("channel_height")
    effective_rib_width = candidate.get("effective_rib_width")
    pitch = candidate.get("pitch")
    fit_ratio = candidate.get("fit_ratio")
    hydraulic_diameter = candidate.get("hydraulic_diameter")
    coolant_velocity = candidate.get("coolant_velocity")
    pressure_drop = candidate.get("estimated_pressure_drop")
    coverage = candidate.get("circumferential_coverage")

    if channel_width is None or channel_width <= 0:
        failures.append("CHANNEL_WIDTH_MISSING_OR_NON_POSITIVE")
    elif channel_width < minimum_channel_width:
        failures.append("CHANNEL_WIDTH_BELOW_MINIMUM")

    if channel_height is None or channel_height <= 0:
        failures.append("CHANNEL_HEIGHT_MISSING_OR_NON_POSITIVE")
    elif channel_height < minimum_channel_height:
        failures.append("CHANNEL_HEIGHT_BELOW_MINIMUM")

    if effective_rib_width is None or effective_rib_width <= 0:
        failures.append("EFFECTIVE_RIB_WIDTH_MISSING_OR_NON_POSITIVE")
    elif effective_rib_width < minimum_rib_width:
        failures.append("EFFECTIVE_RIB_WIDTH_BELOW_MINIMUM")

    if pitch is None or pitch <= 0:
        failures.append("PITCH_MISSING_OR_NON_POSITIVE")

    if fit_ratio is None:
        failures.append("FIT_RATIO_MISSING")
    elif fit_ratio < 1.0:
        failures.append("REQUESTED_GEOMETRY_DOES_NOT_FIT_CIRCUMFERENCE")

    if hydraulic_diameter is None or hydraulic_diameter <= 0:
        failures.append("HYDRAULIC_DIAMETER_MISSING_OR_NON_POSITIVE")
    elif (
        minimum_hydraulic_diameter is not None
        and hydraulic_diameter < minimum_hydraulic_diameter
    ):
        failures.append("HYDRAULIC_DIAMETER_BELOW_MINIMUM")

    if coolant_velocity is None or coolant_velocity <= 0:
        failures.append("COOLANT_VELOCITY_MISSING_OR_NON_POSITIVE")
    elif (
        maximum_coolant_velocity is not None
        and coolant_velocity > maximum_coolant_velocity
    ):
        failures.append("COOLANT_VELOCITY_ABOVE_LIMIT")

    if (
        pressure_drop_limit is not None
        and pressure_drop is not None
        and pressure_drop > pressure_drop_limit
    ):
        failures.append("PRESSURE_DROP_ABOVE_LIMIT")

    if coverage is None or coverage <= 0:
        failures.append("COOLING_COVERAGE_MISSING_OR_NON_POSITIVE")
    elif (
        minimum_cooling_coverage is not None
        and coverage < minimum_cooling_coverage
    ):
        failures.append("COOLING_COVERAGE_BELOW_MINIMUM")

    if not failures and fit_ratio is not None and fit_ratio < 1.05:
        warnings.append("LOW_CIRCUMFERENCE_FIT_MARGIN")

    if not failures and effective_rib_width is not None:
        if effective_rib_width < minimum_rib_width * 1.25:
            warnings.append("LOW_RIB_WIDTH_MARGIN")

    passed = len(failures) == 0

    return {
        "constraint_status": LegacyCompatibilityProducer.marker_from_bool(passed),
        "geometry_constraints_pass": passed,
        "failures": failures,
        "warnings": warnings,
    }


def flatten_constraint_result(result, prefix="recommended"):
    failures = result.get("failures", [])
    warnings = result.get("warnings", [])

    return {
        f"{prefix}_geometry_constraint_status": result.get("constraint_status"),
        f"{prefix}_geometry_constraints_pass": 1.0 if result.get("geometry_constraints_pass") else 0.0,
        f"{prefix}_geometry_constraint_failure_count": float(len(failures)),
        f"{prefix}_geometry_constraint_warning_count": float(len(warnings)),
        f"{prefix}_geometry_constraint_failures": "; ".join(failures),
        f"{prefix}_geometry_constraint_warnings": "; ".join(warnings),
    }
