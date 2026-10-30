
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u76_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u76_is_fail_like(text) or _leaf_16u76_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u76_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u76_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u76_is_fail_like(value):
    return _leaf_16u76_status_severity(value) == "FAIL"


def _leaf_16u76_is_warn_like(value):
    return _leaf_16u76_status_severity(value) == "WARN"


def _leaf_16u76_is_pass_like(value):
    return _leaf_16u76_status_severity(value) == "PASS"


"""
PHASE 11C.3
Regen Optimisation Report Owner

Creates architecture-only optimisation report ownership.

Does NOT:
- run optimisation
- advance generations
- execute mutation
- execute solver sweeps
- accept candidates
- commit geometry
"""

OWNER_NAME = "REGEN_OPTIMISATION_REPORT_OWNER"
PHASE = "11C.3"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_OWNER_PHASE_11C3"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_OWNER_PHASE_11C3"


def attach_regen_optimisation_report_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_optimisation_report_owner(results))
    return results


def build_regen_optimisation_report_owner(results):
    session_ready = (
        results.get("regen_optimisation_session_owner_ready") is True
        and results.get("phase_11c_3_optimisation_report_owner_allowed") is True
    )

    session = results.get("regen_optimisation_session", {})
    report_bundle = _build_report_bundle(session)

    checks = [
        _check(
            "session_owner_ready",
            session_ready,
            "11C.2 session owner allows report ownership.",
            "11C.2 session owner is not ready.",
        ),
        _check(
            "session_report_created",
            bool(report_bundle.get("session_report")),
            "Session report created.",
            "Session report missing.",
        ),
        _check(
            "generation_report_created",
            bool(report_bundle.get("generation_report")),
            "Generation report created.",
            "Generation report missing.",
        ),
        _check(
            "candidate_report_created",
            bool(report_bundle.get("candidate_report")),
            "Candidate report created.",
            "Candidate report missing.",
        ),
        _check(
            "convergence_report_created",
            bool(report_bundle.get("convergence_report")),
            "Convergence report created.",
            "Convergence report missing.",
        ),
        _check(
            "runtime_locked",
            report_bundle.get("runtime_execution_enabled") is False,
            "Runtime execution remains locked.",
            "Runtime execution must remain locked in 11C.3.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_report_owner_complete": True,
        "phase_11c_3_regen_optimisation_report_owner_complete": True,
        "regen_optimisation_report_owner_ready": ready,
        "regen_optimisation_report_owner_status": status,
        "regen_optimisation_report_bundle": report_bundle,
        "regen_optimisation_report_owner_checks": checks,
        "regen_optimisation_report_owner_failed_checks": failed,
        "regen_optimisation_report_owner_report": build_report(status, ready, report_bundle, checks, failed),
        "phase_11c_4_optimisation_registration_owner_allowed": ready,
        "regen_optimisation_registration_owner_architecture_allowed": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_report_bundle(session):
    session_id = session.get("session_id", "OPT_SESSION_UNAVAILABLE")

    session_report = {
        "report_id": f"{session_id}_SESSION_REPORT",
        "report_type": "SESSION_REPORT",
        "session_id": session_id,
        "session_status": session.get("session_status", "UNKNOWN"),
        "objective_mode": session.get("objective_mode"),
        "population_size": session.get("population_size"),
        "generation_limit": session.get("generation_limit"),
        "generation_count": session.get("generation_count"),
        "runtime_state": "LOCKED_UNTIL_11D",
    }

    generation_report = {
        "report_id": f"{session_id}_GENERATION_REPORT",
        "report_type": "GENERATION_REPORT",
        "session_id": session_id,
        "generation_count": session.get("generation_count", 0),
        "current_population_id": session.get("current_population_id"),
        "generation_advance_state": "NOT_STARTED",
    }

    candidate_report = {
        "report_id": f"{session_id}_CANDIDATE_REPORT",
        "report_type": "CANDIDATE_REPORT",
        "session_id": session_id,
        "best_candidate_id": session.get("best_candidate_id"),
        "best_score": session.get("best_score"),
        "candidate_selection_state": "NOT_STARTED",
    }

    convergence_report = {
        "report_id": f"{session_id}_CONVERGENCE_REPORT",
        "report_type": "CONVERGENCE_REPORT",
        "session_id": session_id,
        "convergence_state": session.get("convergence_state", "NOT_STARTED"),
        "convergence_confidence": None,
        "convergence_summary": "Runtime convergence tracking is locked until 11D/11E.",
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "session_id": session_id,
        "session_report": session_report,
        "generation_report": generation_report,
        "candidate_report": candidate_report,
        "convergence_report": convergence_report,
        "runtime_execution_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_auto_accept_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, report_bundle, checks, failed):
    lines = [
        "PHASE 11C.3 REGEN OPTIMISATION REPORT OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11C.4 Registration Owner: {ready}",
        "",
        "REPORT BUNDLE SNAPSHOT",
        f"Session ID: {report_bundle.get('session_id')}",
        f"Session Report: {bool(report_bundle.get('session_report'))}",
        f"Generation Report: {bool(report_bundle.get('generation_report'))}",
        f"Candidate Report: {bool(report_bundle.get('candidate_report'))}",
        f"Convergence Report: {bool(report_bundle.get('convergence_report'))}",
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
        lines.append("11C.3 optimisation report owner is complete.")
        lines.append("11C.4 optimisation registration ownership may begin.")
        lines.append("Runtime optimisation remains locked until 11D.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
