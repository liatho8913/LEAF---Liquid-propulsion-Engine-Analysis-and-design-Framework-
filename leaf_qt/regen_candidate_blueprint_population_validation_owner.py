
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u91_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u91_is_fail_like(text) or _leaf_16u91_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u91_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u91_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u91_is_fail_like(value):
    return _leaf_16u91_status_severity(value) == "FAIL"


def _leaf_16u91_is_warn_like(value):
    return _leaf_16u91_status_severity(value) == "WARN"


def _leaf_16u91_is_pass_like(value):
    return _leaf_16u91_status_severity(value) == "PASS"


"""
PHASE 12C.3
Candidate Blueprint Population Validation Owner

Validates the registered candidate blueprint population.

Does NOT:
- mutate candidates
- score candidates
- run solver
- accept candidates
- evolve populations
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_POPULATION_VALIDATION_OWNER"
PHASE = "12C.3"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_POPULATION_VALIDATION_OWNER_PHASE_12C3"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_POPULATION_VALIDATION_OWNER_PHASE_12C3"


def attach_regen_candidate_blueprint_population_validation_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_population_validation_owner(results))
    return results


def build_regen_candidate_blueprint_population_validation_owner(results):
    blockers = []

    allowed = (
        results.get("phase_12c_3_candidate_blueprint_population_validation_owner_allowed") is True
        and results.get("regen_candidate_blueprint_population_validation_owner_allowed") is True
    )

    if not allowed:
        blockers.append("12C.2 population registration owner has not allowed population validation.")

    population = results.get("regen_candidate_blueprint_population", {})
    registry = results.get("regen_candidate_blueprint_population_registry", {})
    blueprints = results.get("regen_candidate_blueprints", [])

    if not isinstance(population, dict) or not population:
        blockers.append("Candidate blueprint population is missing.")

    if not isinstance(registry, dict) or not registry:
        blockers.append("Candidate blueprint population registry is missing.")

    if not isinstance(blueprints, list) or not blueprints:
        blockers.append("Candidate blueprint source blueprints are missing.")

    _require_locked(results, blockers)

    checks = []
    if isinstance(population, dict) and isinstance(registry, dict) and isinstance(blueprints, list):
        checks = _build_validation_checks(population, registry, blueprints)

    failed_checks = [check for check in checks if not check["passed"]]
    ready = len(blockers) == 0 and len(checks) > 0 and len(failed_checks) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    validation = _build_validation_record(status, ready, checks, failed_checks, population, registry)
    report = build_report(status, ready, validation, checks, failed_checks, blockers)

    return {
        "regen_candidate_blueprint_population_validation_owner_complete": True,
        "phase_12c_3_regen_candidate_blueprint_population_validation_owner_complete": True,
        "regen_candidate_blueprint_population_validation_owner_ready": ready,
        "regen_candidate_blueprint_population_validation_owner_status": status,
        "regen_candidate_blueprint_population_validation_owner_blockers": blockers,

        "regen_candidate_blueprint_population_validation": validation,
        "regen_candidate_blueprint_population_validation_checks": checks,
        "regen_candidate_blueprint_population_validation_failed_checks": failed_checks,
        "regen_candidate_blueprint_population_validation_owner_report": report,

        "phase_12c_4_candidate_blueprint_population_completion_audit_allowed": ready,
        "regen_candidate_blueprint_population_completion_audit_allowed": ready,

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


def _build_validation_checks(population, registry, blueprints):
    population_member_ids = population.get("member_ids", [])
    registry_member_ids = registry.get("registered_member_ids", [])
    blueprint_ids = [blueprint.get("blueprint_id") for blueprint in blueprints]

    checks = [
        _check(
            "population_ready",
            population.get("ready") is True,
            "Population builder marked the population ready.",
        ),
        _check(
            "registry_ready",
            registry.get("ready") is True,
            "Population registration owner marked the registry ready.",
        ),
        _check(
            "population_id_exists",
            bool(population.get("population_id")),
            "Population ID exists.",
        ),
        _check(
            "registry_id_exists",
            bool(registry.get("population_registry_id")),
            "Population registry ID exists.",
        ),
        _check(
            "registry_links_population",
            registry.get("registered_population_id") == population.get("population_id"),
            "Registry links to the population ID.",
        ),
        _check(
            "member_count_positive",
            _int(population.get("member_count")) > 0,
            "Population contains one or more members.",
        ),
        _check(
            "member_count_matches_ids",
            _int(population.get("member_count")) == len(population_member_ids),
            "Population member count matches member IDs.",
        ),
        _check(
            "registry_member_count_matches_population",
            _int(registry.get("registered_member_count")) == _int(population.get("member_count")),
            "Registry member count matches population member count.",
        ),
        _check(
            "registry_member_ids_match_population",
            set(registry_member_ids) == set(population_member_ids),
            "Registry member IDs match population member IDs.",
        ),
        _check(
            "population_member_ids_unique",
            len(population_member_ids) == len(set(population_member_ids)),
            "Population member IDs are unique.",
        ),
        _check(
            "population_member_ids_exist_in_blueprints",
            set(population_member_ids).issubset(set(blueprint_ids)),
            "Population members exist in source blueprints.",
        ),
        _check(
            "all_population_members_engineering_complete",
            _all_members_engineering_complete(population_member_ids, blueprints),
            "All population members are engineering-complete blueprints.",
        ),
        _check(
            "population_provenance_locked",
            _population_provenance_locked(population),
            "Population provenance confirms no mutation, scoring, solver, acceptance, or commit occurred.",
        ),
        _check(
            "registry_permissions_locked",
            _registry_permissions_locked(registry),
            "Registry permissions keep mutation, scoring, solver, acceptance, and commit locked.",
        ),
        _check(
            "population_readiness_correct",
            _population_readiness_correct(population),
            "Population readiness only allows registration/validation and blocks execution paths.",
        ),
        _check(
            "future_linkage_exists",
            bool(registry.get("future_completion_audit_key"))
            and bool(registry.get("future_mutation_key"))
            and bool(registry.get("future_generation_tracking_key")),
            "Registry future linkage exists.",
        ),
    ]

    return checks


def _build_validation_record(status, ready, checks, failed_checks, population, registry):
    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": status,
        "ready": ready,
        "complete": ready,
        "population_id": population.get("population_id") if isinstance(population, dict) else None,
        "population_registry_id": registry.get("population_registry_id") if isinstance(registry, dict) else None,
        "checked_member_count": population.get("member_count") if isinstance(population, dict) else 0,
        "check_count": len(checks),
        "failed_check_count": len(failed_checks),
        "failed_checks": [check["name"] for check in failed_checks],
        "population_validation_state": (
            "BLUEPRINT_POPULATION_VALIDATED_EXECUTION_LOCKED"
            if ready
            else "BLUEPRINT_POPULATION_VALIDATION_BLOCKED"
        ),
        "next_phase": "12C.4_CANDIDATE_BLUEPRINT_POPULATION_COMPLETION_AUDIT" if ready else None,
    }


def build_report(status, ready, validation, checks, failed_checks, blockers):
    lines = [
        "PHASE 12C.3 REGEN CANDIDATE BLUEPRINT POPULATION VALIDATION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12C.4 Candidate Blueprint Population Completion Audit: {ready}",
        f"Population ID: {validation.get('population_id')}",
        f"Population Registry ID: {validation.get('population_registry_id')}",
        f"Checked Member Count: {validation.get('checked_member_count')}",
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
            "- Mutation: locked",
            "- Scoring: locked",
            "- Solver execution: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12C.3 candidate blueprint population validation owner is complete.",
            "The registered blueprint population is valid.",
            "12C.4 candidate blueprint population completion audit may begin.",
        ])
    else:
        lines.extend([
            "",
            "RESULT",
            "12C.3 candidate blueprint population validation owner is blocked.",
        ])

    return "\n".join(lines)


def _all_members_engineering_complete(member_ids, blueprints):
    by_id = {
        blueprint.get("blueprint_id"): blueprint
        for blueprint in blueprints
        if isinstance(blueprint, dict)
    }

    for member_id in member_ids:
        blueprint = by_id.get(member_id)
        if not isinstance(blueprint, dict):
            return False

        if blueprint.get("blueprint_completion_status") != "PASS_BLUEPRINT_ENGINEERING_COMPLETION_AUDIT":
            return False

        if blueprint.get("blueprint_engineering_status") != "ENGINEERING_BLUEPRINT_COMPLETE_READY_FOR_POPULATION":
            return False

        if blueprint.get("blueprint_lifecycle_state") != "BLUEPRINT_ENGINEERING_COMPLETE_POPULATION_LOCKED":
            return False

        if not isinstance(blueprint.get("geometry_package"), dict):
            return False

        if not isinstance(blueprint.get("thermal_package"), dict):
            return False

        if not isinstance(blueprint.get("validation_package"), dict):
            return False

        if not isinstance(blueprint.get("blueprint_completion_audit"), dict):
            return False

    return True


def _population_provenance_locked(population):
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


def _registry_permissions_locked(registry):
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


def _population_readiness_correct(population):
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
