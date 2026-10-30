from leaf_qt.status_presentation import status_severity
"""
PHASE 12D.2
Candidate Blueprint Mutation Validation

Validates the mutation architecture created in 12D.1.

Does NOT:
- mutate geometry
- score candidates
- run solver
- accept candidates
- evolve populations
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

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_MUTATION_VALIDATION"
PHASE = "12D.2"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_MUTATION_VALIDATION_PHASE_12D2"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_MUTATION_VALIDATION_PHASE_12D2"


def attach_regen_candidate_blueprint_mutation_validation(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_mutation_validation(results))
    return results


def build_regen_candidate_blueprint_mutation_validation(results):
    blockers = []

    allowed = (
        results.get("phase_12d_2_candidate_blueprint_mutation_validation_allowed") is True
        and results.get("regen_candidate_blueprint_mutation_validation_allowed") is True
    )

    if not allowed:
        blockers.append("12D.1 mutation architecture has not allowed mutation validation.")

    architecture = results.get("regen_candidate_blueprint_mutation_architecture", {})
    session = results.get("regen_candidate_blueprint_mutation_session", {})
    registry = results.get("regen_candidate_blueprint_mutation_registry", {})

    if not isinstance(architecture, dict) or not architecture:
        blockers.append("Mutation architecture is missing.")

    if not isinstance(session, dict) or not session:
        blockers.append("Mutation session is missing.")

    if not isinstance(registry, dict) or not registry:
        blockers.append("Mutation registry is missing.")

    _require_locked(results, blockers)

    checks = []
    if isinstance(architecture, dict) and isinstance(session, dict) and isinstance(registry, dict):
        checks = _build_validation_checks(architecture, session, registry, results)

    failed_checks = [check for check in checks if not check["passed"]]
    ready = len(blockers) == 0 and len(checks) > 0 and len(failed_checks) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    validation = _build_validation_record(status, ready, checks, failed_checks, architecture, session, registry)
    report = build_report(status, ready, validation, checks, failed_checks, blockers)

    return {
        "regen_candidate_blueprint_mutation_validation_complete": True,
        "phase_12d_2_regen_candidate_blueprint_mutation_validation_complete": True,
        "regen_candidate_blueprint_mutation_validation_ready": ready,
        "regen_candidate_blueprint_mutation_validation_status": status,
        "regen_candidate_blueprint_mutation_validation_blockers": blockers,

        "regen_candidate_blueprint_mutation_validation": validation,
        "regen_candidate_blueprint_mutation_validation_checks": checks,
        "regen_candidate_blueprint_mutation_validation_failed_checks": failed_checks,
        "regen_candidate_blueprint_mutation_validation_report": report,

        "phase_12d_3_candidate_blueprint_diversity_controller_allowed": ready,
        "regen_candidate_blueprint_diversity_controller_allowed": ready,

        "regen_candidate_blueprint_mutation_execution_allowed": False,
        "regen_candidate_blueprint_generation_execution_allowed": False,
        "regen_candidate_blueprint_create_blueprints_allowed": False,
        "regen_candidate_creation_create_candidates_allowed": False,
        "regen_candidate_generation_create_candidates_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def _build_validation_checks(architecture, session, registry, results):
    scopes = registry.get("registered_mutation_scopes", [])
    modes = registry.get("registered_mutation_modes", [])
    permissions = registry.get("permissions", {})
    future = registry.get("future_linkage", {})
    lifecycle = architecture.get("mutation_lifecycle", {})

    required_scopes = [
        "number_of_coolant_channels",
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
        "hot_gas_wall_thickness",
        "coolant_flow_fraction",
    ]

    required_modes = [
        "scale_up",
        "scale_down",
        "bounded_integer_step",
        "bounded_float_step",
        "no_op_baseline_preservation",
    ]

    checks = [
        _check(
            "mutation_architecture_complete",
            results.get("phase_12d_1_regen_candidate_blueprint_mutation_architecture_complete") is True
            and results.get("regen_candidate_blueprint_mutation_architecture_ready") is True,
            "12D.1 mutation architecture is complete and ready.",
        ),
        _check(
            "architecture_state_valid",
            architecture.get("architecture_state") == "MUTATION_ARCHITECTURE_CREATED_EXECUTION_LOCKED",
            "Mutation architecture state is valid and execution locked.",
        ),
        _check(
            "session_ready",
            session.get("ready") is True
            and session.get("lifecycle_state") == "MUTATION_SESSION_CREATED_EXECUTION_LOCKED",
            "Mutation session is ready with correct lifecycle state.",
        ),
        _check(
            "registry_ready",
            registry.get("ready") is True,
            "Mutation registry is ready.",
        ),
        _check(
            "session_registry_linkage",
            session.get("mutation_session_id")
            and registry.get("mutation_session_id") == session.get("mutation_session_id"),
            "Mutation registry links to mutation session.",
        ),
        _check(
            "population_linkage_valid",
            session.get("source_population_id")
            and session.get("source_population_id") == registry.get("source_population_id"),
            "Mutation session and registry link to the same population.",
        ),
        _check(
            "all_required_mutation_scopes_registered",
            set(required_scopes).issubset(set(scopes)),
            "All required mutation scopes are registered.",
        ),
        _check(
            "mutation_scopes_unique",
            len(scopes) == len(set(scopes)),
            "Mutation scopes are unique.",
        ),
        _check(
            "all_required_mutation_modes_registered",
            set(required_modes).issubset(set(modes)),
            "All required mutation modes are registered.",
        ),
        _check(
            "mutation_modes_unique",
            len(modes) == len(set(modes)),
            "Mutation modes are unique.",
        ),
        _check(
            "permissions_valid",
            _permissions_valid(permissions),
            "Mutation permissions allow validation only and keep execution locked.",
        ),
        _check(
            "future_linkage_valid",
            _future_linkage_valid(future),
            "Future linkage exists for diversity, convergence, termination, and completion audit.",
        ),
        _check(
            "lifecycle_locked",
            _lifecycle_locked(lifecycle),
            "Mutation lifecycle confirms no execution has occurred.",
        ),
        _check(
            "global_execution_locks_closed",
            _global_execution_locks_closed(results),
            "Global execution locks remain closed.",
        ),
    ]

    return checks


def _build_validation_record(status, ready, checks, failed_checks, architecture, session, registry):
    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "ready": ready,
        "complete": ready,
        "mutation_session_id": session.get("mutation_session_id") if isinstance(session, dict) else None,
        "mutation_registry_id": registry.get("mutation_registry_id") if isinstance(registry, dict) else None,
        "source_population_id": session.get("source_population_id") if isinstance(session, dict) else None,
        "check_count": len(checks),
        "failed_check_count": len(failed_checks),
        "failed_checks": [check["name"] for check in failed_checks],
        "mutation_validation_state": (
            "MUTATION_ARCHITECTURE_VALIDATED_EXECUTION_LOCKED"
            if ready
            else "MUTATION_ARCHITECTURE_VALIDATION_BLOCKED"
        ),
        "next_phase": "12D.3_CANDIDATE_BLUEPRINT_DIVERSITY_CONTROLLER" if ready else None,
    }


def build_report(status, ready, validation, checks, failed_checks, blockers):
    lines = [
        "PHASE 12D.2 REGEN CANDIDATE BLUEPRINT MUTATION VALIDATION",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12D.3 Candidate Blueprint Diversity Controller: {ready}",
        f"Mutation Session ID: {validation.get('mutation_session_id')}",
        f"Mutation Registry ID: {validation.get('mutation_registry_id')}",
        f"Source Population ID: {validation.get('source_population_id')}",
        "",
    ]

    if blockers:
        lines.append("SYSTEM BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")
        lines.append("")

    lines.append("VALIDATION CHECKS")
    for check in checks:
        marker = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        lines.append(f"[{marker}] {check['name']} - {check['message']}")

    if failed_checks:
        lines.extend(["", "FAILED CHECKS"])
        for check in failed_checks:
            lines.append(f"- {check['name']}: {check['message']}")

    if ready:
        lines.extend([
            "",
            "SAFETY STATE",
            "- Diversity controller: allowed next",
            "- Mutation execution: locked",
            "- Scoring: locked",
            "- Solver execution: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12D.2 candidate blueprint mutation validation is complete.",
            "Mutation architecture has been validated.",
            "12D.3 candidate blueprint diversity controller may begin.",
        ])
    else:
        lines.extend([
            "",
            "RESULT",
            "12D.2 candidate blueprint mutation validation is blocked.",
        ])

    return "\n".join(lines)


def _permissions_valid(permissions):
    if not isinstance(permissions, dict):
        return False

    return (
        permissions.get("mutation_validation_allowed") is True
        and permissions.get("mutation_execution_allowed") is False
        and permissions.get("scoring_execution_allowed") is False
        and permissions.get("solver_execution_allowed") is False
        and permissions.get("candidate_acceptance_allowed") is False
        and permissions.get("live_geometry_commit_allowed") is False
    )


def _future_linkage_valid(future):
    if not isinstance(future, dict):
        return False

    required = [
        "mutation_validation_key",
        "diversity_controller_key",
        "convergence_monitor_key",
        "termination_owner_key",
        "optimisation_completion_audit_key",
    ]

    return all(bool(future.get(key)) for key in required)


def _lifecycle_locked(lifecycle):
    if not isinstance(lifecycle, dict):
        return False

    return (
        lifecycle.get("architecture_created") is True
        and lifecycle.get("validation_complete") is False
        and lifecycle.get("execution_enabled") is False
        and lifecycle.get("mutation_executed") is False
        and lifecycle.get("scoring_executed") is False
        and lifecycle.get("solver_executed") is False
        and lifecycle.get("candidate_accepted") is False
        and lifecycle.get("live_geometry_committed") is False
    )


def _global_execution_locks_closed(results):
    required_false = [
        "regen_candidate_blueprint_mutation_execution_allowed",
        "regen_candidate_blueprint_generation_execution_allowed",
        "regen_candidate_blueprint_create_blueprints_allowed",
        "regen_candidate_creation_create_candidates_allowed",
        "regen_candidate_generation_create_candidates_allowed",
        "regen_optimisation_runtime_execution_allowed",
        "regen_optimisation_generation_advance_allowed",
        "regen_optimisation_mutation_execution_allowed",
        "regen_optimisation_candidate_acceptance_allowed",
        "regen_optimisation_live_geometry_commit_allowed",
    ]
    return all(results.get(key) is False for key in required_false)


def _require_locked(results, blockers):
    required_false = {
        "regen_candidate_blueprint_mutation_execution_allowed":
            "Candidate blueprint mutation execution is not safely locked.",
        "regen_candidate_blueprint_generation_execution_allowed":
            "Blueprint generation execution is not safely locked.",
        "regen_candidate_blueprint_create_blueprints_allowed":
            "Blueprint creation is not safely locked.",
        "regen_candidate_creation_create_candidates_allowed":
            "Candidate creation is not safely locked.",
        "regen_candidate_generation_create_candidates_allowed":
            "Candidate generation is not safely locked.",
        "regen_optimisation_runtime_execution_allowed":
            "Runtime optimisation execution is not safely locked.",
        "regen_optimisation_generation_advance_allowed":
            "Population generation advance is not safely locked.",
        "regen_optimisation_mutation_execution_allowed":
            "Mutation execution is not safely locked.",
        "regen_optimisation_candidate_acceptance_allowed":
            "Candidate acceptance is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed":
            "Live geometry commit is not safely locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)


def _check(name, passed, message):
    return {
        "name": name,
        "passed": bool(passed),
        "message": message,
    }
