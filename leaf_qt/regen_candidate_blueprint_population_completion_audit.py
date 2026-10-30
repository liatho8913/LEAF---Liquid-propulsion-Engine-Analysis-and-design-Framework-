from leaf_qt.status_presentation import status_severity
"""
PHASE 12C.4
Candidate Blueprint Population Completion Audit

Final completion audit for the candidate blueprint population subsystem.

Does NOT:
- mutate candidates
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

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_POPULATION_COMPLETION_AUDIT"
PHASE = "12C.4"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_POPULATION_COMPLETION_AUDIT_PHASE_12C4"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_POPULATION_COMPLETION_AUDIT_PHASE_12C4"


def attach_regen_candidate_blueprint_population_completion_audit(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_population_completion_audit(results))
    return results


def build_regen_candidate_blueprint_population_completion_audit(results):
    blockers = []

    allowed = (
        results.get("phase_12c_4_candidate_blueprint_population_completion_audit_allowed") is True
        and results.get("regen_candidate_blueprint_population_completion_audit_allowed") is True
    )

    if not allowed:
        blockers.append("12C.3 population validation owner has not allowed completion audit.")

    population = results.get("regen_candidate_blueprint_population", {})
    registry = results.get("regen_candidate_blueprint_population_registry", {})
    validation = results.get("regen_candidate_blueprint_population_validation", {})

    if not isinstance(population, dict) or not population:
        blockers.append("Candidate blueprint population is missing.")

    if not isinstance(registry, dict) or not registry:
        blockers.append("Candidate blueprint population registry is missing.")

    if not isinstance(validation, dict) or not validation:
        blockers.append("Candidate blueprint population validation is missing.")

    _require_locked(results, blockers)

    checks = []
    if isinstance(population, dict) and isinstance(registry, dict) and isinstance(validation, dict):
        checks = _build_completion_checks(population, registry, validation, results)

    failed_checks = [check for check in checks if not check["passed"]]

    ready = len(blockers) == 0 and len(checks) > 0 and len(failed_checks) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    audit = _build_audit_record(status, ready, checks, failed_checks, population, registry, validation)
    report = build_report(status, ready, audit, checks, failed_checks, blockers)

    return {
        "regen_candidate_blueprint_population_completion_audit_complete": True,
        "phase_12c_4_regen_candidate_blueprint_population_completion_audit_complete": True,
        "regen_candidate_blueprint_population_completion_audit_ready": ready,
        "regen_candidate_blueprint_population_completion_audit_status": status,
        "regen_candidate_blueprint_population_completion_audit_blockers": blockers,

        "regen_candidate_blueprint_population_completion_audit": audit,
        "regen_candidate_blueprint_population_completion_audit_checks": checks,
        "regen_candidate_blueprint_population_completion_audit_failed_checks": failed_checks,
        "regen_candidate_blueprint_population_completion_audit_report": report,

        "phase_12c_blueprint_population_architecture_complete": ready,
        "regen_candidate_blueprint_population_architecture_complete": ready,

        "phase_12d_1_candidate_blueprint_mutation_architecture_allowed": ready,
        "regen_candidate_blueprint_mutation_architecture_allowed": ready,

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


def _build_completion_checks(population, registry, validation, results):
    checks = [
        _check(
            "population_builder_complete",
            results.get("phase_12c_1_regen_candidate_blueprint_population_builder_complete") is True
            and results.get("regen_candidate_blueprint_population_builder_ready") is True,
            "12C.1 population builder is complete and ready.",
        ),
        _check(
            "population_registration_complete",
            results.get("phase_12c_2_regen_candidate_blueprint_population_registration_owner_complete") is True
            and results.get("regen_candidate_blueprint_population_registration_owner_ready") is True,
            "12C.2 population registration owner is complete and ready.",
        ),
        _check(
            "population_validation_complete",
            results.get("phase_12c_3_regen_candidate_blueprint_population_validation_owner_complete") is True
            and results.get("regen_candidate_blueprint_population_validation_owner_ready") is True,
            "12C.3 population validation owner is complete and ready.",
        ),
        _check(
            "population_object_ready",
            population.get("ready") is True
            and population.get("population_lifecycle_state") == "BLUEPRINT_POPULATION_CREATED_EXECUTION_LOCKED",
            "Population object is ready with correct lifecycle state.",
        ),
        _check(
            "population_registry_ready",
            registry.get("ready") is True
            and registry.get("registry_lifecycle_state") == "BLUEPRINT_POPULATION_REGISTERED_EXECUTION_LOCKED",
            "Population registry is ready with correct lifecycle state.",
        ),
        _check(
            "population_validation_ready",
            validation.get("ready") is True
            and validation.get("population_validation_state") == "BLUEPRINT_POPULATION_VALIDATED_EXECUTION_LOCKED",
            "Population validation is ready with correct validation state.",
        ),
        _check(
            "population_id_linkage",
            population.get("population_id")
            and registry.get("registered_population_id") == population.get("population_id")
            and validation.get("population_id") == population.get("population_id"),
            "Population ID is consistent across population, registry, and validation.",
        ),
        _check(
            "population_registry_linkage",
            registry.get("population_registry_id")
            and validation.get("population_registry_id") == registry.get("population_registry_id"),
            "Population registry ID is linked in validation.",
        ),
        _check(
            "member_count_consistent",
            _int(population.get("member_count")) > 0
            and _int(population.get("member_count")) == _int(registry.get("registered_member_count"))
            and _int(population.get("member_count")) == _int(validation.get("checked_member_count")),
            "Population member count is consistent across layers.",
        ),
        _check(
            "validation_has_no_failed_checks",
            _int(validation.get("failed_check_count")) == 0,
            "Population validation has no failed checks.",
        ),
        _check(
            "population_readiness_valid",
            _population_readiness_valid(population),
            "Population readiness is valid and execution paths remain locked.",
        ),
        _check(
            "registry_permissions_valid",
            _registry_permissions_valid(registry),
            "Population registry permissions are valid and execution paths remain locked.",
        ),
        _check(
            "population_provenance_valid",
            _population_provenance_valid(population),
            "Population provenance confirms no mutation, scoring, solver, acceptance, or commit occurred.",
        ),
        _check(
            "future_mutation_linkage_exists",
            bool(registry.get("future_mutation_key"))
            and bool(registry.get("future_generation_tracking_key")),
            "Future mutation and generation-tracking linkage exists.",
        ),
        _check(
            "global_execution_locks_closed",
            _global_execution_locks_closed(results),
            "Global execution locks remain closed.",
        ),
    ]

    return checks


def _build_audit_record(status, ready, checks, failed_checks, population, registry, validation):
    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "ready": ready,
        "complete": ready,
        "population_id": population.get("population_id") if isinstance(population, dict) else None,
        "population_registry_id": registry.get("population_registry_id") if isinstance(registry, dict) else None,
        "validated_member_count": validation.get("checked_member_count") if isinstance(validation, dict) else 0,
        "check_count": len(checks),
        "failed_check_count": len(failed_checks),
        "failed_checks": [check["name"] for check in failed_checks],
        "population_architecture_state": (
            "BLUEPRINT_POPULATION_ARCHITECTURE_COMPLETE_MUTATION_LOCKED"
            if ready
            else "BLUEPRINT_POPULATION_ARCHITECTURE_INCOMPLETE"
        ),
        "next_phase": "12D.1_CANDIDATE_BLUEPRINT_MUTATION_ARCHITECTURE" if ready else None,
    }


def build_report(status, ready, audit, checks, failed_checks, blockers):
    lines = [
        "PHASE 12C.4 REGEN CANDIDATE BLUEPRINT POPULATION COMPLETION AUDIT",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Population Architecture Complete: {ready}",
        f"Ready for 12D.1 Candidate Blueprint Mutation Architecture: {ready}",
        f"Population ID: {audit.get('population_id')}",
        f"Population Registry ID: {audit.get('population_registry_id')}",
        f"Validated Member Count: {audit.get('validated_member_count')}",
        f"Architecture State: {audit.get('population_architecture_state')}",
        "",
    ]

    if blockers:
        lines.append("SYSTEM BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")
        lines.append("")

    lines.append("COMPLETION CHECKS")
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
            "- Mutation architecture: allowed next, execution still locked",
            "- Mutation execution: locked",
            "- Scoring: locked",
            "- Solver execution: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12C.4 candidate blueprint population completion audit is complete.",
            "Blueprint population architecture is complete.",
            "12D.1 candidate blueprint mutation architecture may begin.",
        ])
    else:
        lines.extend([
            "",
            "RESULT",
            "12C.4 candidate blueprint population completion audit is blocked.",
        ])

    return "\n".join(lines)


def _population_readiness_valid(population):
    readiness = population.get("population_readiness", {})
    if not isinstance(readiness, dict):
        return False

    return (
        readiness.get("ready_for_population_registration") is True
        and readiness.get("ready_for_population_validation") is False
        and readiness.get("ready_for_mutation") is False
        and readiness.get("ready_for_scoring") is False
        and readiness.get("ready_for_solver_execution") is False
        and readiness.get("ready_for_candidate_acceptance") is False
        and readiness.get("ready_for_live_commit") is False
    )


def _registry_permissions_valid(registry):
    permissions = registry.get("permissions", {})
    if not isinstance(permissions, dict):
        return False

    return (
        permissions.get("population_validation_allowed") is True
        and permissions.get("mutation_execution_allowed") is False
        and permissions.get("scoring_execution_allowed") is False
        and permissions.get("solver_execution_allowed") is False
        and permissions.get("candidate_acceptance_allowed") is False
        and permissions.get("live_geometry_commit_allowed") is False
    )


def _population_provenance_valid(population):
    provenance = population.get("population_provenance", {})
    if not isinstance(provenance, dict):
        return False

    return (
        provenance.get("mutation_executed") is False
        and provenance.get("scoring_executed") is False
        and provenance.get("solver_executed") is False
        and provenance.get("candidate_acceptance_executed") is False
        and provenance.get("live_geometry_modified") is False
    )


def _global_execution_locks_closed(results):
    required_false = [
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


def _int(value):
    try:
        if value is None:
            return 0
        return int(round(float(value)))
    except Exception:
        return 0


def _check(name, passed, message):
    return {
        "name": name,
        "passed": bool(passed),
        "message": message,
    }
