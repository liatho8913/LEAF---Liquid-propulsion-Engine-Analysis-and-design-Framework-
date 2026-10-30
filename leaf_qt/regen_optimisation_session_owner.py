from leaf_qt.status_presentation import status_severity
"""
PHASE 11C.2
Regen Optimisation Session Owner

Creates architecture-only optimisation session state.

This owner DOES NOT:
- run optimisation
- advance generations
- execute mutation
- execute solver sweeps
- accept candidates
- commit geometry
"""

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

from datetime import datetime, timezone

OWNER_NAME = "REGEN_OPTIMISATION_SESSION_OWNER"
PHASE = "11C.2"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SESSION_OWNER_PHASE_11C2"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SESSION_OWNER_PHASE_11C2"


def attach_regen_optimisation_session_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_optimisation_session_owner(results))
    return results


def build_regen_optimisation_session_owner(results):
    input_audit_ready = (
        results.get("regen_autonomous_optimisation_input_audit_ready") is True
        and results.get("phase_11c_2_optimisation_session_owner_allowed") is True
    )

    session = _build_session(results)

    checks = [
        _check(
            "phase_11c_1_input_audit_ready",
            input_audit_ready,
            "11C.1 input audit allows session ownership.",
            "11C.1 input audit does not allow session ownership.",
        ),
        _check(
            "session_id_created",
            bool(session.get("session_id")),
            "Optimisation session ID created.",
            "Optimisation session ID missing.",
        ),
        _check(
            "session_status_architecture_only",
            session.get("session_status") == "ARCHITECTURE_READY_RUNTIME_LOCKED",
            "Session is architecture-ready and runtime-locked.",
            "Session status is not runtime-locked.",
        ),
        _check(
            "generation_count_initialised",
            session.get("generation_count") == 0,
            "Generation count initialised to zero.",
            "Generation count must start at zero.",
        ),
        _check(
            "best_candidate_empty",
            session.get("best_candidate_id") is None,
            "Best candidate intentionally empty before runtime execution.",
            "Best candidate should not exist before runtime execution.",
        ),
        _check(
            "runtime_locked",
            session.get("runtime_execution_enabled") is False,
            "Runtime execution remains locked.",
            "Runtime execution must remain locked in 11C.2.",
        ),
        _check(
            "live_commit_locked",
            session.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11C.2.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_session_owner_complete": True,
        "phase_11c_2_regen_optimisation_session_owner_complete": True,
        "regen_optimisation_session_owner_ready": ready,
        "regen_optimisation_session_owner_status": status,
        "regen_optimisation_session": session,
        "regen_optimisation_session_checks": checks,
        "regen_optimisation_session_failed_checks": failed,
        "regen_optimisation_session_report": build_report(status, ready, session, checks, failed),
        "phase_11c_3_optimisation_report_owner_allowed": ready,
        "regen_optimisation_report_owner_architecture_allowed": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_session(results):
    settings = results.get("regen_autonomous_optimisation_input_settings", {})
    now = datetime.now(timezone.utc).isoformat()

    return {
        "session_id": "OPT_SESSION_0001",
        "phase": PHASE,
        "owner": OWNER_NAME,
        "created_utc": now,
        "updated_utc": now,
        "session_status": "ARCHITECTURE_READY_RUNTIME_LOCKED",
        "objective_mode": settings.get("objective_mode", "balanced_regen_geometry"),
        "population_size": settings.get("population_size", 16),
        "generation_limit": settings.get("generation_limit", 8),
        "generation_count": 0,
        "current_population_id": None,
        "best_candidate_id": None,
        "best_score": None,
        "convergence_state": "NOT_STARTED",
        "runtime_execution_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_auto_accept_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, session, checks, failed):
    lines = [
        "PHASE 11C.2 REGEN OPTIMISATION SESSION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11C.3 Report Owner: {ready}",
        "",
        "SESSION SNAPSHOT",
        f"Session ID: {session.get('session_id')}",
        f"Session Status: {session.get('session_status')}",
        f"Objective Mode: {session.get('objective_mode')}",
        f"Population Size: {session.get('population_size')}",
        f"Generation Limit: {session.get('generation_limit')}",
        f"Generation Count: {session.get('generation_count')}",
        f"Best Candidate: {session.get('best_candidate_id')}",
        f"Best Score: {session.get('best_score')}",
        f"Convergence State: {session.get('convergence_state')}",
        "",
        "SAFETY LOCKS",
        f"Runtime Execution Enabled: {session.get('runtime_execution_enabled')}",
        f"Solver Execution Enabled: {session.get('solver_execution_enabled')}",
        f"Live Geometry Commit Enabled: {session.get('live_geometry_commit_enabled')}",
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
        lines.append("11C.2 optimisation session owner is complete.")
        lines.append("11C.3 optimisation report ownership may begin.")
        lines.append("Runtime optimisation remains locked until 11D.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
