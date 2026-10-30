
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u81_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u81_is_fail_like(text) or _leaf_16u81_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u81_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u81_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u81_is_fail_like(value):
    return _leaf_16u81_status_severity(value) == "FAIL"


def _leaf_16u81_is_warn_like(value):
    return _leaf_16u81_status_severity(value) == "WARN"


def _leaf_16u81_is_pass_like(value):
    return _leaf_16u81_status_severity(value) == "PASS"


"""
PHASE 11D.3
Runtime Regen Optimisation Report Owner

Owns runtime optimisation reporting.

Does NOT:
- advance generations
- create mutations
- execute solver sweeps
- score candidates
- accept candidates
- commit geometry
"""

OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_REPORT_OWNER"
PHASE = "11D.3"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_REPORT_OWNER_PHASE_11D3"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_REPORT_OWNER_PHASE_11D3"


def attach_regen_runtime_optimisation_report_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_optimisation_report_owner(results))
    return results


def build_regen_runtime_optimisation_report_owner(results):
    session_ready = (
        results.get("regen_runtime_optimisation_session_owner_ready") is True
        and results.get("phase_11d_3_runtime_report_owner_allowed") is True
    )

    runtime_session = results.get("regen_runtime_optimisation_session", {})
    report_bundle = _build_runtime_report_bundle(runtime_session)

    checks = [
        _check(
            "runtime_session_owner_ready",
            session_ready,
            "11D.2 runtime session owner allows report ownership.",
            "11D.2 runtime session owner is not ready.",
        ),
        _check(
            "runtime_session_report_created",
            bool(report_bundle.get("runtime_session_report")),
            "Runtime session report created.",
            "Runtime session report missing.",
        ),
        _check(
            "runtime_generation_report_created",
            bool(report_bundle.get("runtime_generation_report")),
            "Runtime generation report created.",
            "Runtime generation report missing.",
        ),
        _check(
            "runtime_candidate_report_created",
            bool(report_bundle.get("runtime_candidate_report")),
            "Runtime candidate report created.",
            "Runtime candidate report missing.",
        ),
        _check(
            "runtime_convergence_report_created",
            bool(report_bundle.get("runtime_convergence_report")),
            "Runtime convergence report created.",
            "Runtime convergence report missing.",
        ),
        _check(
            "runtime_audit_trail_created",
            bool(report_bundle.get("runtime_audit_trail")),
            "Runtime audit trail created.",
            "Runtime audit trail missing.",
        ),
        _check(
            "runtime_execution_locked",
            report_bundle.get("runtime_execution_enabled") is False,
            "Runtime execution remains locked.",
            "Runtime execution must remain locked in 11D.3.",
        ),
        _check(
            "geometry_commit_locked",
            report_bundle.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11D.3.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_optimisation_report_owner_complete": True,
        "phase_11d_3_regen_runtime_optimisation_report_owner_complete": True,
        "regen_runtime_optimisation_report_owner_ready": ready,
        "regen_runtime_optimisation_report_owner_status": status,
        "regen_runtime_optimisation_report_bundle": report_bundle,
        "regen_runtime_optimisation_report_owner_checks": checks,
        "regen_runtime_optimisation_report_owner_failed_checks": failed,
        "regen_runtime_optimisation_report_owner_report": build_report(status, ready, report_bundle, checks, failed),
        "phase_11d_4_runtime_registration_owner_allowed": ready,
        "regen_runtime_optimisation_registration_owner_allowed": ready,
        "regen_runtime_optimisation_reporting_state_owned": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_runtime_report_bundle(runtime_session):
    runtime_session_id = runtime_session.get("runtime_session_id", "OPT_RUNTIME_SESSION_UNAVAILABLE")

    runtime_session_report = {
        "report_id": f"{runtime_session_id}_RUNTIME_SESSION_REPORT",
        "report_type": "RUNTIME_SESSION_REPORT",
        "runtime_session_id": runtime_session_id,
        "base_session_id": runtime_session.get("base_session_id"),
        "runtime_state": runtime_session.get("runtime_state"),
        "execution_state": runtime_session.get("execution_state"),
        "objective_mode": runtime_session.get("objective_mode"),
        "runtime_execution_state": "LOCKED_UNTIL_RUNTIME_EXECUTION_OWNER",
    }

    runtime_generation_report = {
        "report_id": f"{runtime_session_id}_RUNTIME_GENERATION_REPORT",
        "report_type": "RUNTIME_GENERATION_REPORT",
        "runtime_session_id": runtime_session_id,
        "current_generation_index": runtime_session.get("current_generation_index"),
        "generation_limit": runtime_session.get("generation_limit"),
        "generation_advance_state": "LOCKED",
        "current_population_id": runtime_session.get("current_population_id"),
    }

    runtime_candidate_report = {
        "report_id": f"{runtime_session_id}_RUNTIME_CANDIDATE_REPORT",
        "report_type": "RUNTIME_CANDIDATE_REPORT",
        "runtime_session_id": runtime_session_id,
        "current_candidate_id": runtime_session.get("current_candidate_id"),
        "best_candidate_id": runtime_session.get("best_candidate_id"),
        "best_score": runtime_session.get("best_score"),
        "candidate_scoring_state": "LOCKED",
        "candidate_acceptance_state": "LOCKED",
    }

    runtime_convergence_report = {
        "report_id": f"{runtime_session_id}_RUNTIME_CONVERGENCE_REPORT",
        "report_type": "RUNTIME_CONVERGENCE_REPORT",
        "runtime_session_id": runtime_session_id,
        "convergence_state": runtime_session.get("convergence_state"),
        "termination_state": runtime_session.get("termination_state"),
        "convergence_summary": "Runtime convergence reporting is prepared but execution remains locked.",
    }

    runtime_audit_trail = {
        "report_id": f"{runtime_session_id}_RUNTIME_AUDIT_TRAIL",
        "report_type": "RUNTIME_AUDIT_TRAIL",
        "runtime_session_id": runtime_session_id,
        "events": [
            {
                "event": "RUNTIME_REPORT_OWNER_CREATED",
                "phase": PHASE,
                "runtime_execution_enabled": False,
                "solver_execution_enabled": False,
                "live_geometry_commit_enabled": False,
            }
        ],
        "event_count": 1,
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "runtime_session_id": runtime_session_id,
        "runtime_session_report": runtime_session_report,
        "runtime_generation_report": runtime_generation_report,
        "runtime_candidate_report": runtime_candidate_report,
        "runtime_convergence_report": runtime_convergence_report,
        "runtime_audit_trail": runtime_audit_trail,
        "runtime_execution_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_auto_accept_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, report_bundle, checks, failed):
    lines = [
        "PHASE 11D.3 RUNTIME REGEN OPTIMISATION REPORT OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11D.4 Runtime Registration Owner: {ready}",
        "",
        "RUNTIME REPORT BUNDLE SNAPSHOT",
        f"Runtime Session ID: {report_bundle.get('runtime_session_id')}",
        f"Runtime Session Report: {bool(report_bundle.get('runtime_session_report'))}",
        f"Runtime Generation Report: {bool(report_bundle.get('runtime_generation_report'))}",
        f"Runtime Candidate Report: {bool(report_bundle.get('runtime_candidate_report'))}",
        f"Runtime Convergence Report: {bool(report_bundle.get('runtime_convergence_report'))}",
        f"Runtime Audit Trail: {bool(report_bundle.get('runtime_audit_trail'))}",
        "",
        "SAFETY LOCKS",
        f"Runtime Execution Enabled: {report_bundle.get('runtime_execution_enabled')}",
        f"Solver Execution Enabled: {report_bundle.get('solver_execution_enabled')}",
        f"Live Geometry Commit Enabled: {report_bundle.get('live_geometry_commit_enabled')}",
        "",
        "CHECKS",
    ]

    for check in checks:
        marker = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        message = check["pass_message"] if check["passed"] else check["fail_message"]
        lines.append(f"[{marker}] {check['name']} - {message}")

    if failed:
        lines.append("")
        lines.append("BLOCKERS")
        for check in failed:
            lines.append(f"- {check['name']}: {check['fail_message']}")
    else:
        lines.append("")
        lines.append("RESULT")
        lines.append("11D.3 runtime optimisation report owner is complete.")
        lines.append("11D.4 runtime registration ownership may begin.")
        lines.append("Runtime optimisation remains locked until later execution systems.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
