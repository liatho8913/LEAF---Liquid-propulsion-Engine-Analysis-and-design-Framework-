from leaf_qt.status_presentation import status_severity
"""
PHASE 11D.2
Runtime Regen Optimisation Session Runtime Owner

Owns runtime optimisation state.

Does NOT:
- advance generations
- create mutations
- execute solver sweeps
- score candidates
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

OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_SESSION_OWNER"
PHASE = "11D.2"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_SESSION_OWNER_PHASE_11D2"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_SESSION_OWNER_PHASE_11D2"


def attach_regen_runtime_optimisation_session_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_optimisation_session_owner(results))
    return results


def build_regen_runtime_optimisation_session_owner(results):
    gate_ready = (
        results.get("regen_runtime_optimisation_input_gate_ready") is True
        and results.get("phase_11d_2_runtime_owner_allowed") is True
    )

    base_session = results.get("regen_optimisation_session", {})
    registry = results.get("regen_optimisation_registry", {})

    runtime_session = _build_runtime_session(base_session, registry)

    checks = [
        _check(
            "input_gate_ready",
            gate_ready,
            "11D.1 runtime input gate allows runtime session ownership.",
            "11D.1 runtime input gate does not allow runtime session ownership.",
        ),
        _check(
            "base_session_exists",
            isinstance(base_session, dict) and bool(base_session.get("session_id")),
            "Base optimisation session exists.",
            "Base optimisation session missing.",
        ),
        _check(
            "registry_exists",
            isinstance(registry, dict) and bool(registry.get("registry_id")),
            "Optimisation registry exists.",
            "Optimisation registry missing.",
        ),
        _check(
            "runtime_session_id_created",
            bool(runtime_session.get("runtime_session_id")),
            "Runtime session ID created.",
            "Runtime session ID missing.",
        ),
        _check(
            "current_generation_zero",
            runtime_session.get("current_generation_index") == 0,
            "Current generation starts at zero.",
            "Current generation should start at zero.",
        ),
        _check(
            "execution_state_locked",
            runtime_session.get("execution_state") == "READY_RUNTIME_EXECUTION_LOCKED",
            "Runtime execution state remains locked.",
            "Runtime execution state must remain locked in 11D.2.",
        ),
        _check(
            "solver_execution_locked",
            runtime_session.get("solver_execution_enabled") is False,
            "Solver execution remains locked.",
            "Solver execution must remain locked in 11D.2.",
        ),
        _check(
            "geometry_commit_locked",
            runtime_session.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11D.2.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_optimisation_session_owner_complete": True,
        "phase_11d_2_regen_runtime_optimisation_session_owner_complete": True,
        "regen_runtime_optimisation_session_owner_ready": ready,
        "regen_runtime_optimisation_session_owner_status": status,
        "regen_runtime_optimisation_session": runtime_session,
        "regen_runtime_optimisation_session_owner_checks": checks,
        "regen_runtime_optimisation_session_owner_failed_checks": failed,
        "regen_runtime_optimisation_session_owner_report": build_report(status, ready, runtime_session, checks, failed),
        "phase_11d_3_runtime_report_owner_allowed": ready,
        "regen_runtime_optimisation_report_owner_allowed": ready,
        "regen_runtime_optimisation_session_state_owned": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_runtime_session(base_session, registry):
    session_id = base_session.get("session_id", "OPT_SESSION_UNAVAILABLE")
    registry_id = registry.get("registry_id", "OPT_REGISTRY_UNAVAILABLE")

    return {
        "runtime_session_id": f"{session_id}_RUNTIME",
        "base_session_id": session_id,
        "registry_id": registry_id,
        "owner": OWNER_NAME,
        "phase": PHASE,
        "runtime_state": "ARCHITECTURE_READY",
        "execution_state": "READY_RUNTIME_EXECUTION_LOCKED",
        "objective_mode": base_session.get("objective_mode"),
        "population_size": base_session.get("population_size"),
        "generation_limit": base_session.get("generation_limit"),
        "current_generation_index": 0,
        "current_population_id": None,
        "current_candidate_id": None,
        "best_candidate_id": None,
        "best_score": None,
        "termination_state": "NOT_STARTED",
        "convergence_state": "NOT_STARTED",
        "runtime_execution_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_auto_accept_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, runtime_session, checks, failed):
    lines = [
        "PHASE 11D.2 RUNTIME REGEN OPTIMISATION SESSION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11D.3 Runtime Report Owner: {ready}",
        "",
        "RUNTIME SESSION SNAPSHOT",
        f"Runtime Session ID: {runtime_session.get('runtime_session_id')}",
        f"Base Session ID: {runtime_session.get('base_session_id')}",
        f"Registry ID: {runtime_session.get('registry_id')}",
        f"Objective Mode: {runtime_session.get('objective_mode')}",
        f"Current Generation: {runtime_session.get('current_generation_index')}",
        f"Execution State: {runtime_session.get('execution_state')}",
        f"Termination State: {runtime_session.get('termination_state')}",
        "",
        "SAFETY LOCKS",
        f"Runtime Execution Enabled: {runtime_session.get('runtime_execution_enabled')}",
        f"Solver Execution Enabled: {runtime_session.get('solver_execution_enabled')}",
        f"Live Geometry Commit Enabled: {runtime_session.get('live_geometry_commit_enabled')}",
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
        lines.append("11D.2 runtime optimisation session owner is complete.")
        lines.append("11D.3 runtime report ownership may begin.")
        lines.append("Runtime optimisation remains locked until later 11D execution systems.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
