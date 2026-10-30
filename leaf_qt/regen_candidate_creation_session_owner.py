from leaf_qt.status_presentation import status_severity
"""
PHASE 11G.2
Candidate Creation Session Owner

Owns candidate creation session state and metadata.

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

OWNER_NAME = "REGEN_CANDIDATE_CREATION_SESSION_OWNER"
PHASE = "11G.2"

PASS_STATUS = "PASS_REGEN_CANDIDATE_CREATION_SESSION_OWNER_PHASE_11G2"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_CREATION_SESSION_OWNER_PHASE_11G2"


def attach_regen_candidate_creation_session_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_creation_session_owner(results))
    return results


def build_regen_candidate_creation_session_owner(results):
    input_ready = (
        results.get("regen_candidate_creation_input_audit_ready") is True
        and results.get("phase_11g_2_candidate_creation_session_owner_allowed") is True
    )

    input_audit = results.get("regen_candidate_creation_input_audit", {})
    generation_session = results.get("regen_candidate_generation_session", {})

    creation_session = _build_creation_session(input_audit, generation_session)

    checks = [
        _check(
            "candidate_creation_input_audit_ready",
            input_ready,
            "11G.1 candidate creation input audit allows session ownership.",
            "11G.1 candidate creation input audit is not ready.",
        ),
        _check(
            "creation_session_created",
            bool(creation_session.get("candidate_creation_session_id")),
            "Candidate creation session ID created.",
            "Candidate creation session ID missing.",
        ),
        _check(
            "generation_session_linked",
            bool(creation_session.get("candidate_generation_session_id")),
            "Candidate generation session is linked.",
            "Candidate generation session link missing.",
        ),
        _check(
            "required_input_groups_carried",
            len(creation_session.get("required_input_groups", [])) >= 1,
            "Required input groups carried into creation session.",
            "Required input groups missing from creation session.",
        ),
        _check(
            "creation_counts_zero",
            creation_session.get("created_candidate_count") == 0
            and creation_session.get("accepted_candidate_count") == 0
            and creation_session.get("rejected_candidate_count") == 0,
            "Candidate creation counts start at zero.",
            "Candidate creation counts should start at zero.",
        ),
        _check(
            "creation_locked",
            creation_session.get("candidate_creation_enabled") is False,
            "Candidate creation remains locked.",
            "Candidate creation must remain locked in 11G.2.",
        ),
        _check(
            "mutation_locked",
            creation_session.get("mutation_execution_enabled") is False,
            "Mutation remains locked.",
            "Mutation must remain locked in 11G.2.",
        ),
        _check(
            "solver_execution_locked",
            creation_session.get("solver_execution_enabled") is False,
            "Solver execution remains locked.",
            "Solver execution must remain locked in 11G.2.",
        ),
        _check(
            "geometry_commit_locked",
            creation_session.get("live_geometry_commit_enabled") is False,
            "Live geometry commit remains locked.",
            "Live geometry commit must remain locked in 11G.2.",
        ),
    ]

    failed = [c for c in checks if not c["passed"]]
    ready = len(failed) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_candidate_creation_session_owner_complete": True,
        "phase_11g_2_regen_candidate_creation_session_owner_complete": True,
        "regen_candidate_creation_session_owner_ready": ready,
        "regen_candidate_creation_session_owner_status": status,
        "regen_candidate_creation_session": creation_session,
        "regen_candidate_creation_session_owner_checks": checks,
        "regen_candidate_creation_session_owner_failed_checks": failed,
        "regen_candidate_creation_session_owner_report": build_report(status, ready, creation_session, checks, failed),
        "phase_11g_3_candidate_creation_report_owner_allowed": ready,
        "regen_candidate_creation_report_owner_allowed": ready,
        "regen_candidate_creation_session_state_owned": ready,
        "regen_candidate_creation_execution_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_creation_session(input_audit, generation_session):
    generation_session_id = generation_session.get(
        "candidate_generation_session_id",
        input_audit.get("candidate_generation_session_id", "CANDIDATE_GENERATION_SESSION_UNAVAILABLE"),
    )

    return {
        "candidate_creation_session_id": f"{generation_session_id}_CREATION",
        "candidate_generation_session_id": generation_session_id,
        "candidate_generation_registry_id": input_audit.get("candidate_generation_registry_id"),
        "owner": OWNER_NAME,
        "phase": PHASE,
        "candidate_creation_state": "SESSION_OWNED_CREATION_LOCKED",
        "candidate_creation_lifecycle_state": "NOT_STARTED",
        "candidate_creation_pool_state": "EMPTY",
        "objective_mode": generation_session.get("objective_mode"),
        "population_size": generation_session.get("population_size"),
        "generation_limit": generation_session.get("generation_limit"),
        "required_input_groups": list(input_audit.get("required_input_groups", [])),
        "constraint_context": {
            "geometry_constraints_required": True,
            "thermal_constraints_required": True,
            "material_constraints_required": True,
            "source_quality_constraints_required": True,
        },
        "creation_package": {
            "created_candidate_ids": [],
            "created_candidate_count": 0,
            "candidate_blueprints": [],
            "candidate_blueprint_count": 0,
        },
        "created_candidate_ids": [],
        "created_candidate_count": 0,
        "accepted_candidate_ids": [],
        "accepted_candidate_count": 0,
        "rejected_candidate_ids": [],
        "rejected_candidate_count": 0,
        "current_creation_candidate_id": None,
        "current_creation_population_id": None,
        "current_creation_generation_id": None,
        "candidate_creation_enabled": False,
        "candidate_creation_execution_enabled": False,
        "candidate_blueprint_creation_enabled": False,
        "mutation_execution_enabled": False,
        "candidate_scoring_enabled": False,
        "candidate_ranking_enabled": False,
        "candidate_acceptance_enabled": False,
        "solver_execution_enabled": False,
        "live_geometry_commit_enabled": False,
    }


def build_report(status, ready, creation_session, checks, failed):
    lines = [
        "PHASE 11G.2 REGEN CANDIDATE CREATION SESSION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 11G.3 Candidate Creation Report Owner: {ready}",
        "",
        "CANDIDATE CREATION SESSION SNAPSHOT",
        f"Creation Session ID: {creation_session.get('candidate_creation_session_id')}",
        f"Generation Session ID: {creation_session.get('candidate_generation_session_id')}",
        f"Creation State: {creation_session.get('candidate_creation_state')}",
        f"Lifecycle State: {creation_session.get('candidate_creation_lifecycle_state')}",
        f"Created Candidates: {creation_session.get('created_candidate_count')}",
        f"Accepted Candidates: {creation_session.get('accepted_candidate_count')}",
        f"Rejected Candidates: {creation_session.get('rejected_candidate_count')}",
        "",
        "SAFETY LOCKS",
        f"Candidate Creation Enabled: {creation_session.get('candidate_creation_enabled')}",
        f"Blueprint Creation Enabled: {creation_session.get('candidate_blueprint_creation_enabled')}",
        f"Mutation Enabled: {creation_session.get('mutation_execution_enabled')}",
        f"Solver Execution Enabled: {creation_session.get('solver_execution_enabled')}",
        f"Live Geometry Commit Enabled: {creation_session.get('live_geometry_commit_enabled')}",
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
        lines.append("11G.2 candidate creation session owner is complete.")
        lines.append("11G.3 candidate creation report ownership may begin.")
        lines.append("Actual candidate creation, mutation, scoring, acceptance, solver execution, and geometry commit remain locked.")

    return "\n".join(lines)


def _check(name, passed, pass_message, fail_message):
    return {
        "name": name,
        "passed": bool(passed),
        "pass_message": pass_message,
        "fail_message": fail_message,
    }
