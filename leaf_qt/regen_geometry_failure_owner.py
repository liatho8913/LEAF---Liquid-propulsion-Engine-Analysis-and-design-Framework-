def _sorted_failure_counts(failure_counts):
    if not failure_counts:
        return []

    return sorted(
        failure_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )


def _recommend_action(primary_failure):
    if primary_failure == "EFFECTIVE_RIB_WIDTH_BELOW_MINIMUM":
        return "Increase available circumference, reduce channel count, reduce channel width, or relax manufacturable rib-width assumptions only if justified."

    if primary_failure == "REQUESTED_GEOMETRY_DOES_NOT_FIT_CIRCUMFERENCE":
        return "Reduce requested pitch demand, reduce channel count, reduce channel width, or increase channel radius."

    if primary_failure == "CHANNEL_WIDTH_BELOW_MINIMUM":
        return "Increase available circumference or reduce channel count so each channel can meet minimum manufacturable width."

    if primary_failure == "CHANNEL_HEIGHT_BELOW_MINIMUM":
        return "Increase channel height bounds or review manufacturable minimum channel height."

    if primary_failure == "HYDRAULIC_DIAMETER_BELOW_MINIMUM":
        return "Increase channel width or height to improve hydraulic diameter."

    if primary_failure == "COOLANT_VELOCITY_ABOVE_LIMIT":
        return "Increase total coolant flow area, reduce mass flow per channel, increase channel count, or increase channel dimensions."

    if primary_failure == "PRESSURE_DROP_ABOVE_LIMIT":
        return "Increase hydraulic diameter, reduce coolant velocity, shorten cooling path, or raise allowable pressure-drop budget."

    if primary_failure == "COOLING_COVERAGE_BELOW_MINIMUM":
        return "Increase channel width, channel count, or cooling coverage requirement feasibility."

    if primary_failure in {"NO_CANDIDATE_PROVIDED", "NO_VALID_GEOMETRY_FOUND"}:
        return "Review input bounds, radius, coolant properties, channel-count limits, and manufacturability constraints."

    return "Review regen geometry inputs, constraint limits, and candidate search bounds."


def evaluate_regen_geometry_failure(solver_result):
    if solver_result is None:
        return {
            "regen_geometry_failure_owner_status": "FAIL_REGEN_GEOMETRY_FAILURE_OWNER",
            "regen_geometry_failure_detected": True,
            "regen_geometry_primary_failure_reason": "NO_SOLVER_RESULT",
            "regen_geometry_secondary_failure_reason": "",
            "regen_geometry_dominant_failure_percentage": 100.0,
            "regen_geometry_failure_severity": "CRITICAL",
            "regen_geometry_recommended_next_action": "Run the regen geometry solver before evaluating failure ownership.",
        }

    solver_pass = bool(solver_result.get("solver_pass"))
    candidate_report = solver_result.get("candidate_report", {})
    history = candidate_report.get("iteration_history", {})
    failure_counts = history.get("most_common_failures", {}) or {}

    if solver_pass:
        return {
            "regen_geometry_failure_owner_status": "PASS_REGEN_GEOMETRY_FAILURE_OWNER",
            "regen_geometry_failure_detected": False,
            "regen_geometry_primary_failure_reason": "NONE",
            "regen_geometry_secondary_failure_reason": "",
            "regen_geometry_dominant_failure_percentage": 0.0,
            "regen_geometry_failure_severity": "NONE",
            "regen_geometry_recommended_next_action": "No failure action required. The selected regen geometry candidate passed the solver.",
        }

    sorted_failures = _sorted_failure_counts(failure_counts)

    if sorted_failures:
        primary_failure, primary_count = sorted_failures[0]
        secondary_failure = sorted_failures[1][0] if len(sorted_failures) > 1 else ""
        total_failures = sum(failure_counts.values())
        dominant_percentage = (
            100.0 * primary_count / total_failures
            if total_failures > 0
            else 0.0
        )
    else:
        primary_failure = candidate_report.get("status", "NO_VALID_GEOMETRY_FOUND")
        secondary_failure = ""
        dominant_percentage = 100.0

    candidates_checked = float(candidate_report.get("candidates_checked", 0) or 0)
    valid_fit_candidates = float(candidate_report.get("valid_fit_candidates", 0) or 0)

    if candidates_checked <= 0:
        severity = "CRITICAL"
    elif valid_fit_candidates <= 0:
        severity = "HIGH"
    elif dominant_percentage >= 75.0:
        severity = "HIGH"
    elif dominant_percentage >= 40.0:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return {
        "regen_geometry_failure_owner_status": "PASS_REGEN_GEOMETRY_FAILURE_OWNER",
        "regen_geometry_failure_detected": True,
        "regen_geometry_primary_failure_reason": primary_failure,
        "regen_geometry_secondary_failure_reason": secondary_failure,
        "regen_geometry_dominant_failure_percentage": dominant_percentage,
        "regen_geometry_failure_severity": severity,
        "regen_geometry_recommended_next_action": _recommend_action(primary_failure),
    }


def flatten_regen_geometry_failure_result(result, prefix="recommended"):
    return {
        f"{prefix}_regen_geometry_failure_owner_status": result.get(
            "regen_geometry_failure_owner_status",
            "FAIL_REGEN_GEOMETRY_FAILURE_OWNER",
        ),
        f"{prefix}_regen_geometry_failure_detected": 1.0
        if result.get("regen_geometry_failure_detected")
        else 0.0,
        f"{prefix}_regen_geometry_primary_failure_reason": result.get(
            "regen_geometry_primary_failure_reason",
            "",
        ),
        f"{prefix}_regen_geometry_secondary_failure_reason": result.get(
            "regen_geometry_secondary_failure_reason",
            "",
        ),
        f"{prefix}_regen_geometry_dominant_failure_percentage": result.get(
            "regen_geometry_dominant_failure_percentage",
            0.0,
        ),
        f"{prefix}_regen_geometry_failure_severity": result.get(
            "regen_geometry_failure_severity",
            "",
        ),
        f"{prefix}_regen_geometry_recommended_next_action": result.get(
            "regen_geometry_recommended_next_action",
            "",
        ),
    }