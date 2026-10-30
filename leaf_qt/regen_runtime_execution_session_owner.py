from leaf_qt.status_presentation import status_severity
"""
PHASE 11E.2
Runtime Execution Session Owner

Owns execution lifecycle state.

Does NOT:
- generate candidates
- mutate geometry
- score candidates
- rank candidates
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

OWNER_NAME = "REGEN_RUNTIME_EXECUTION_SESSION_OWNER"
PHASE = "11E.2"

PASS_STATUS = "PASS_REGEN_RUNTIME_EXECUTION_SESSION_OWNER_PHASE_11E2"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_EXECUTION_SESSION_OWNER_PHASE_11E2"


def attach_regen_runtime_execution_session_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_runtime_execution_session_owner(results))
    return results


def build_regen_runtime_execution_session_owner(results):
    gate_ready = (
        results.get("regen_runtime_execution_input_gate_ready") is True
        and results.get("phase_11e_2_runtime_execution_session_owner_allowed") is True
    )

    runtime_session = results.get("regen_runtime_optimisation_session", {})
    runtime_registry = results.get("regen_runtime_optimisation_registry", {})

    execution_session = _build_execution_session(runtime_session, runtime_registry)

    checks = [
        _check(
            "execution_input_gate_ready",
            gate_ready,
            "11E.1 execution input gate allows execution session ownership.",
            "11E.1 execution input gate is not ready.",
        ),
        _check(
            "runtime_session_exists",
            isinstance(runtime_session, dict) and bool(runtime_session.get("runtime_session_id")),
            "Runtime session exists.",
            "Runtime session missing.",
        ),
        _check(
            "runtime_registry_exists",
            isinstance(runtime_registry, dict) and bool(runtime_registry.get("runtime_registry_id")),
            "Runtime registry exists.",
            "Runtime registry missing.",
        ),
        _check(
            "execution_session_created",
            bool(execution_session.get("execution_session_id")),
            "Execution session ID created.",
            "Execution session ID missing.",
        ),
        _check(
            "execution_state_prepared",
            execution_session.get("execution_state") == "PREPARED_EXECUTION_LOCKED",
            "Execution state prepared and locked.",
            "Execution state invalid.",
        ),
        _check(
            "execution_lifecycle_not_started",
            execution_session.get("lifecycle_state") == "NOT_STARTED",
            "Execution lifecycle has not started.",
            "Execution lifecycle should not start in 11E.2.",
        ),
        _check(
            "progress_zero",
            execution_session.get("execution_progress_fraction") == 0.0,
            "Execution progress starts at zero.",
            "Execution progress should be zero.",
        ),
        _check(
            "candidate_generation_locked",
            execution_session.get("candidate_generation_enabled") is False,
            "Candidate generation remains locked.",
            "Candidate generation must remain locked in 11E.2.",
        ),
        _check(
            "mutation_locked",
            execution_session.get("mutation_execution_enabled") is False,
            "Mutation remains locked.",
            "Mutation must remain locked in 11E.2.",
        ),
        _check(
            "geometry_commit_locked",
            execution_session.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11E.2.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_execution_session_owner_complete": True,
        "phase_11e_2_regen_runtime_execution_session_owner_complete": True,
        "regen_runtime_execution_session_owner_ready": ready,
        "regen_runtime_execution_session_owner_status": status,
        "regen_runtime_execution_session": execution_session,
        "regen_runtime_execution_session_owner_checks": checks,
        "regen_runtime_execution_session_owner_failed_checks": failed,
        "regen_runtime_execution_session_owner_report": build_report(status, ready, execution_session, checks, failed),
        "phase_11e_3_runtime_execution_report_owner_allowed": ready,
        "regen_runtime_execution_report_owner_allowed": ready,
        "regen_runtime_execution_session_state_owned": ready,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_execution_session(runtime_session, runtime_registry):
    runtime_session_id = runtime_session.get("runtime_session_id", "OPT_RUNTIME_SESSION_UNAVAILABLE")
    runtime_registry_id = runtime_registry.get("runtime_registry_id", "RUNTIME_OPT_REGISTRY_UNAVAILABLE")

    return {
        "execution_session_id": f"{runtime_session_id}_EXECUTION",
        "runtime_session_id": runtime_session_id,
        "runtime_registry_id": runtime_registry_id,
        "owner": OWNER_NAME,
        "phase": PHASE,
        "execution_state": "PREPARED_EXECUTION_LOCKED",
        "lifecycle_state": "NOT_STARTED",
        "execution_stage": "PRE_EXECUTION_OWNERSHIP",
        "pause_state": "NOT_PAUSED",
        "stop_state": "NOT_STOPPED",
        "safety_state": "LOCKED_SAFE",
        "readiness_state": "READY_FOR_REPORT_OWNER",
        "objective_mode": runtime_session.get("objective_mode"),
        "population_size": runtime_session.get("population_size"),
        "generation_limit": runtime_session.get("generation_limit"),
        "current_generation_index": runtime_session.get("current_generation_index", 0),
        "current_population_id": runtime_session.get("current_population_id"),
        "current_candidate_id": runtime_session.get("current_candidate_id"),
        "execution_progress_fraction": 0.0,
        "execution_started": False,
        "execution_finished": False,
        "runtime_execution_enabled": False,
        "candidate_generation_enabled": False,
        "solver_execution_enabled": False,
        "generation_advance_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_acceptance_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, execution_session, checks, failed):
    lines = [
        "PHASE 11E.2 RUNTIME EXECUTION SESSION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11E.3 Execution Report Owner: {ready}",
        "",
        "EXECUTION SESSION SNAPSHOT",
        f"Execution Session ID: {execution_session.get('execution_session_id')}",
        f"Runtime Session ID: {execution_session.get('runtime_session_id')}",
        f"Runtime Registry ID: {execution_session.get('runtime_registry_id')}",
        f"Execution State: {execution_session.get('execution_state')}",
        f"Lifecycle State: {execution_session.get('lifecycle_state')}",
        f"Execution Stage: {execution_session.get('execution_stage')}",
        f"Progress: {execution_session.get('execution_progress_fraction')}",
        "",
        "SAFETY LOCKS",
        f"Runtime Execution Enabled: {execution_session.get('runtime_execution_enabled')}",
        f"Candidate Generation Enabled: {execution_session.get('candidate_generation_enabled')}",
        f"Mutation Enabled: {execution_session.get('mutation_execution_enabled')}",
        f"Live Geometry Commit Enabled: {execution_session.get('live_geometry_commit_enabled')}",
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
        lines.append("11E.2 runtime execution session owner is complete.")
        lines.append("11E.3 runtime execution report ownership may begin.")
        lines.append("Candidate generation, mutation, scoring, acceptance, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
