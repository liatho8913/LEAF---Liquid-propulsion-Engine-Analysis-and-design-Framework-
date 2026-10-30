from leaf_qt.status_presentation import status_severity
"""
PHASE 11F.2
Candidate Generation Session Owner

Owns candidate generation session state and metadata.

Does NOT:
- create candidates
- mutate geometry
- score candidates
- rank candidates
- accept candidates
- commit geometry
- execute solvers
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

OWNER_NAME = "REGEN_CANDIDATE_GENERATION_SESSION_OWNER"
PHASE = "11F.2"

PASS_STATUS = "PASS_REGEN_CANDIDATE_GENERATION_SESSION_OWNER_PHASE_11F2"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_GENERATION_SESSION_OWNER_PHASE_11F2"


def attach_regen_candidate_generation_session_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_generation_session_owner(results))
    return results


def build_regen_candidate_generation_session_owner(results):
    gate_ready = (
        results.get("regen_candidate_generation_input_gate_ready") is True
        and results.get("phase_11f_2_candidate_generation_session_owner_allowed") is True
    )

    gate = results.get("regen_candidate_generation_input_gate", {})
    execution_session = results.get("regen_runtime_execution_session", {})

    candidate_session = _build_candidate_generation_session(gate, execution_session)

    checks = [
        _check(
            "candidate_generation_input_gate_ready",
            gate_ready,
            "11F.1 candidate generation input gate allows session ownership.",
            "11F.1 candidate generation input gate is not ready.",
        ),
        _check(
            "candidate_session_created",
            bool(candidate_session.get("candidate_generation_session_id")),
            "Candidate generation session ID created.",
            "Candidate generation session ID missing.",
        ),
        _check(
            "execution_session_linked",
            bool(candidate_session.get("execution_session_id")),
            "Execution session is linked.",
            "Execution session link missing.",
        ),
        _check(
            "candidate_type_scope_present",
            len(candidate_session.get("candidate_type_scope", [])) >= 1,
            "Candidate type scope is present.",
            "Candidate type scope missing.",
        ),
        _check(
            "candidate_counts_zero",
            candidate_session.get("candidate_count") == 0
            and candidate_session.get("population_count") == 0
            and candidate_session.get("generation_count") == 0,
            "Candidate, population, and generation counts start at zero.",
            "Candidate, population, or generation count should start at zero.",
        ),
        _check(
            "creation_locked",
            candidate_session.get("candidate_creation_enabled") is False,
            "Candidate creation remains locked.",
            "Candidate creation must remain locked in 11F.2.",
        ),
        _check(
            "mutation_locked",
            candidate_session.get("mutation_execution_enabled") is False,
            "Mutation remains locked.",
            "Mutation must remain locked in 11F.2.",
        ),
        _check(
            "solver_execution_locked",
            candidate_session.get("solver_execution_enabled") is False,
            "Solver execution remains locked.",
            "Solver execution must remain locked in 11F.2.",
        ),
        _check(
            "geometry_commit_locked",
            candidate_session.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11F.2.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_candidate_generation_session_owner_complete": True,
        "phase_11f_2_regen_candidate_generation_session_owner_complete": True,
        "regen_candidate_generation_session_owner_ready": ready,
        "regen_candidate_generation_session_owner_status": status,
        "regen_candidate_generation_session": candidate_session,
        "regen_candidate_generation_session_owner_checks": checks,
        "regen_candidate_generation_session_owner_failed_checks": failed,
        "regen_candidate_generation_session_owner_report": build_report(status, ready, candidate_session, checks, failed),
        "phase_11f_3_candidate_generation_report_owner_allowed": ready,
        "regen_candidate_generation_report_owner_allowed": ready,
        "regen_candidate_generation_session_state_owned": ready,
        "regen_candidate_generation_execution_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_candidate_generation_session(gate, execution_session):
    execution_session_id = execution_session.get(
        "execution_session_id",
        gate.get("execution_session_id", "OPT_EXECUTION_SESSION_UNAVAILABLE"),
    )

    return {
        "candidate_generation_session_id": f"{execution_session_id}_CANDIDATE_GENERATION",
        "execution_session_id": execution_session_id,
        "execution_registry_id": gate.get("execution_registry_id"),
        "owner": OWNER_NAME,
        "phase": PHASE,
        "candidate_generation_state": "SESSION_OWNED_CREATION_LOCKED",
        "candidate_lifecycle_state": "NOT_STARTED",
        "candidate_pool_state": "EMPTY",
        "candidate_type_scope": list(gate.get("candidate_type_scope", [])),
        "objective_mode": execution_session.get("objective_mode", gate.get("objective_mode")),
        "population_size": execution_session.get("population_size"),
        "generation_limit": execution_session.get("generation_limit"),
        "candidate_count": 0,
        "population_count": 0,
        "generation_count": 0,
        "current_candidate_id": None,
        "current_population_id": None,
        "current_generation_id": None,
        "candidate_ids": [],
        "population_ids": [],
        "generation_ids": [],
        "candidate_metadata_registry": {},
        "population_metadata_registry": {},
        "generation_metadata_registry": {},
        "candidate_creation_enabled": False,
        "candidate_generation_execution_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_ranking_enabled": False,
        "candidate_acceptance_enabled": False,
        "solver_execution_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, candidate_session, checks, failed):
    lines = [
        "PHASE 11F.2 REGEN CANDIDATE GENERATION SESSION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11F.3 Candidate Generation Report Owner: {ready}",
        "",
        "CANDIDATE SESSION SNAPSHOT",
        f"Candidate Session ID: {candidate_session.get('candidate_generation_session_id')}",
        f"Execution Session ID: {candidate_session.get('execution_session_id')}",
        f"Candidate State: {candidate_session.get('candidate_generation_state')}",
        f"Candidate Pool State: {candidate_session.get('candidate_pool_state')}",
        f"Candidate Count: {candidate_session.get('candidate_count')}",
        f"Population Count: {candidate_session.get('population_count')}",
        f"Generation Count: {candidate_session.get('generation_count')}",
        "",
        "SAFETY LOCKS",
        f"Candidate Creation Enabled: {candidate_session.get('candidate_creation_enabled')}",
        f"Mutation Enabled: {candidate_session.get('mutation_execution_enabled')}",
        f"Solver Execution Enabled: {candidate_session.get('solver_execution_enabled')}",
        f"Live Geometry Commit Enabled: {candidate_session.get('live_geometry_commit_enabled')}",
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
        lines.append("11F.2 candidate generation session owner is complete.")
        lines.append("11F.3 candidate generation report ownership may begin.")
        lines.append("Actual candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
