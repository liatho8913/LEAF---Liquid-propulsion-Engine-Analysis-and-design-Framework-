
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u86_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u86_is_fail_like(text) or _leaf_16u86_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u86_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u86_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u86_is_fail_like(value):
    return _leaf_16u86_status_severity(value) == "FAIL"


def _leaf_16u86_is_warn_like(value):
    return _leaf_16u86_status_severity(value) == "WARN"


def _leaf_16u86_is_pass_like(value):
    return _leaf_16u86_status_severity(value) == "PASS"


def _fmt(value, unit="", precision=6):
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return LegacyCompatibilityProducer.marker_from_bool(value)
    if isinstance(value, (int, float)):
        return f"{value:.{precision}g} {unit}".strip()
    return str(value)


def _section(title):
    return [
        "",
        "=" * len(title),
        title,
        "=" * len(title),
    ]


def build_regen_geometry_report(solver_result):
    if solver_result is None:
        return {
            "regen_geometry_report_status": "FAIL_REGEN_GEOMETRY_REPORT_OWNER",
            "regen_geometry_report_text": "No regen geometry solver result was provided.",
        }

    solver_status = solver_result.get("solver_status", "UNKNOWN")
    solver_pass = bool(solver_result.get("solver_pass"))
    best_candidate = solver_result.get("best_candidate")
    candidate_report = solver_result.get("candidate_report", {})
    mapped = solver_result.get("mapped_results", {})
    history = candidate_report.get("iteration_history", {})

    lines = []

    lines += _section("REGEN GEOMETRY SOLVER REPORT")

    lines.append(f"Solver status: {solver_status}")
    lines.append(f"Solver pass: {LegacyCompatibilityProducer.marker_from_bool(solver_pass)}")

    lines += _section("CANDIDATE SEARCH SUMMARY")
    lines.append(f"Candidates checked: {_fmt(candidate_report.get('candidates_checked'), precision=0)}")
    lines.append(f"Valid fit candidates: {_fmt(candidate_report.get('valid_fit_candidates'), precision=0)}")
    lines.append(f"Rejected fit candidates: {_fmt(candidate_report.get('rejected_fit_candidates'), precision=0)}")
    lines.append(f"Rejected velocity candidates: {_fmt(candidate_report.get('rejected_velocity_candidates'), precision=0)}")
    lines.append(f"Rejected hydraulic-diameter candidates: {_fmt(candidate_report.get('rejected_hydraulic_diameter_candidates'), precision=0)}")
    lines.append(f"Rejected pressure-drop candidates: {_fmt(candidate_report.get('rejected_pressure_drop_candidates'), precision=0)}")
    lines.append(f"Rejected cooling-coverage candidates: {_fmt(candidate_report.get('rejected_cooling_coverage_candidates'), precision=0)}")

    lines += _section("SELECTED GEOMETRY")

    if best_candidate:
        lines.append(f"Channel count: {_fmt(best_candidate.get('channel_count'), precision=0)}")
        lines.append(f"Channel width: {_fmt(best_candidate.get('channel_width'), 'm')}")
        lines.append(f"Channel height: {_fmt(best_candidate.get('channel_height'), 'm')}")
        lines.append(f"Effective rib width: {_fmt(best_candidate.get('effective_rib_width'), 'm')}")
        lines.append(f"Pitch: {_fmt(best_candidate.get('pitch'), 'm')}")
        lines.append(f"Fit ratio: {_fmt(best_candidate.get('fit_ratio'))}")
        lines.append(f"Hydraulic diameter: {_fmt(best_candidate.get('hydraulic_diameter'), 'm')}")
        lines.append(f"Coolant velocity: {_fmt(best_candidate.get('coolant_velocity'), 'm/s')}")
        lines.append(f"Reynolds number: {_fmt(best_candidate.get('reynolds_number'))}")
        lines.append(f"Estimated pressure drop: {_fmt(best_candidate.get('estimated_pressure_drop'), 'Pa')}")
        lines.append(f"Circumferential cooling coverage: {_fmt(best_candidate.get('circumferential_coverage'))}")
        lines.append(f"Geometry score: {_fmt(best_candidate.get('score'))}")
        lines.append(f"Candidate status: {best_candidate.get('status', 'UNKNOWN')}")
    else:
        lines.append("No valid regen geometry candidate was selected.")

    lines += _section("CONSTRAINT OWNER SUMMARY")
    lines.append(f"Constraint status: {mapped.get('recommended_geometry_constraint_status', 'UNKNOWN')}")
    lines.append(f"Constraints pass: {_fmt(mapped.get('recommended_geometry_constraints_pass'))}")
    lines.append(f"Constraint failure count: {_fmt(mapped.get('recommended_geometry_constraint_failure_count'), precision=0)}")
    lines.append(f"Constraint warning count: {_fmt(mapped.get('recommended_geometry_constraint_warning_count'), precision=0)}")

    failures = mapped.get("recommended_geometry_constraint_failures", "")
    warnings = mapped.get("recommended_geometry_constraint_warnings", "")

    lines.append(f"Constraint failures: {failures if failures else 'None'}")
    lines.append(f"Constraint warnings: {warnings if warnings else 'None'}")

    lines += _section("ITERATION HISTORY SUMMARY")
    lines.append(f"Iteration history status: {history.get('iteration_history_status', 'UNKNOWN')}")
    lines.append(f"Total candidates seen by history: {_fmt(history.get('total_candidates_seen'), precision=0)}")
    lines.append(f"Total passed constraints: {_fmt(history.get('total_passed_constraints'), precision=0)}")
    lines.append(f"Total failed constraints: {_fmt(history.get('total_failed_constraints'), precision=0)}")
    lines.append(f"Stored iteration records: {_fmt(history.get('stored_iteration_records'), precision=0)}")
    lines.append(f"Selected candidate reason: {history.get('selected_candidate_reason', 'N/A')}")

    common_failures = history.get("most_common_failures", {})
    common_warnings = history.get("most_common_warnings", {})

    lines += _section("MOST COMMON FAILURES")
    if common_failures:
        for key, value in sorted(common_failures.items()):
            lines.append(f"{key}: {value}")
    else:
        lines.append("None")

    lines += _section("MOST COMMON WARNINGS")
    if common_warnings:
        for key, value in sorted(common_warnings.items()):
            lines.append(f"{key}: {value}")
    else:
        lines.append("None")

    lines += _section("FINAL DECISION")
    if solver_pass:
        lines.append("PASS: A regen geometry candidate was generated and selected.")
        lines.append("The selected candidate passed the regen geometry constraint owner.")
    else:
        lines.append("FAIL: No acceptable regen geometry candidate was selected.")
        lines.append("Review the constraint failures and iteration-history summary before changing thermal or material assumptions.")

    return {
        "regen_geometry_report_status": "PASS_REGEN_GEOMETRY_REPORT_OWNER",
        "regen_geometry_report_text": "\n".join(lines).strip(),
    }


def attach_regen_geometry_report_to_solver_result(solver_result):
    report = build_regen_geometry_report(solver_result)

    if solver_result is None:
        return {
            "solver_result": None,
            "report": report,
        }

    enriched = dict(solver_result)
    enriched["regen_geometry_report"] = report

    return enriched


def flatten_regen_geometry_report(report, prefix="recommended"):
    return {
        f"{prefix}_regen_geometry_report_status": report.get(
            "regen_geometry_report_status",
            "FAIL_REGEN_GEOMETRY_REPORT_OWNER",
        ),
        f"{prefix}_regen_geometry_report_text": report.get(
            "regen_geometry_report_text",
            "",
        ),
    }
