"""
PHASE 12C.2
Candidate Blueprint Population Registration Owner

Registers the managed blueprint population object into a formal population
registry.

Does NOT:
- mutate candidates
- score candidates
- run solver
- accept candidates
- evolve populations
- commit geometry
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_POPULATION_REGISTRATION_OWNER"
PHASE = "12C.2"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_POPULATION_REGISTRATION_OWNER_PHASE_12C2"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_POPULATION_REGISTRATION_OWNER_PHASE_12C2"


def attach_regen_candidate_blueprint_population_registration_owner(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_population_registration_owner(results))
    return results


def build_regen_candidate_blueprint_population_registration_owner(results):
    blockers = []

    allowed = (
        results.get("phase_12c_2_candidate_blueprint_population_registration_allowed") is True
        and results.get("regen_candidate_blueprint_population_registration_allowed") is True
    )

    if not allowed:
        blockers.append("12C.1 population builder has not allowed population registration.")

    population = results.get("regen_candidate_blueprint_population", {})
    if not isinstance(population, dict) or not population:
        blockers.append("Candidate blueprint population is missing.")

    if isinstance(population, dict) and population.get("ready") is not True:
        blockers.append("Candidate blueprint population is not ready.")

    if isinstance(population, dict) and not population.get("population_id"):
        blockers.append("Candidate blueprint population ID is missing.")

    if isinstance(population, dict) and population.get("member_count", 0) <= 0:
        blockers.append("Candidate blueprint population has no members.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    registry = None
    if ready:
        registry = _build_registry(population, results)

    report = build_report(status, ready, registry, blockers)

    return {
        "regen_candidate_blueprint_population_registration_owner_complete": True,
        "phase_12c_2_regen_candidate_blueprint_population_registration_owner_complete": True,
        "regen_candidate_blueprint_population_registration_owner_ready": ready,
        "regen_candidate_blueprint_population_registration_owner_status": status,
        "regen_candidate_blueprint_population_registration_owner_blockers": blockers,

        "regen_candidate_blueprint_population_registry": registry,
        "regen_candidate_blueprint_population_registry_id": (
            registry.get("population_registry_id") if isinstance(registry, dict) else None
        ),
        "regen_candidate_blueprint_population_registration_owner_report": report,

        "phase_12c_3_candidate_blueprint_population_validation_owner_allowed": ready,
        "regen_candidate_blueprint_population_validation_owner_allowed": ready,

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


def _build_registry(population, results):
    population_id = population.get("population_id")
    registry_id = f"POPULATION_REGISTRY_FOR_{population_id}"

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "population_registry_id": registry_id,
        "registered_population_id": population_id,
        "registered_population_lifecycle_state": population.get("population_lifecycle_state"),
        "registered_member_count": population.get("member_count"),
        "registered_member_ids": list(population.get("member_ids", [])),
        "source_population_builder_status": results.get(
            "regen_candidate_blueprint_population_builder_status"
        ),
        "registry_lifecycle_state": "BLUEPRINT_POPULATION_REGISTERED_EXECUTION_LOCKED",
        "registry_scope": [
            "population_identity",
            "population_members",
            "population_statistics",
            "population_provenance",
            "population_readiness",
            "future_population_validation",
            "future_population_completion_audit",
            "future_mutation_architecture",
        ],
        "future_validation_key": "regen_candidate_blueprint_population_validation",
        "future_completion_audit_key": "regen_candidate_blueprint_population_completion_audit",
        "future_mutation_key": "regen_candidate_blueprint_mutation_architecture",
        "future_generation_tracking_key": "regen_candidate_blueprint_generation_tracking",
        "permissions": {
            "population_validation_allowed": True,
            "mutation_execution_allowed": False,
            "scoring_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
        "next_phase": "12C.3_CANDIDATE_BLUEPRINT_POPULATION_VALIDATION_OWNER",
    }


def build_report(status, ready, registry, blockers):
    lines = [
        "PHASE 12C.2 REGEN CANDIDATE BLUEPRINT POPULATION REGISTRATION OWNER",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12C.3 Candidate Blueprint Population Validation Owner: {ready}",
        "",
    ]

    if registry:
        lines.extend([
            "POPULATION REGISTRY",
            f"Registry ID: {registry.get('population_registry_id')}",
            f"Registered Population ID: {registry.get('registered_population_id')}",
            f"Registered Member Count: {registry.get('registered_member_count')}",
            f"Registry Lifecycle: {registry.get('registry_lifecycle_state')}",
            "",
            "REGISTRY SCOPE",
        ])

        for item in registry.get("registry_scope", []):
            lines.append(f"- {item}")

        lines.extend([
            "",
            "FUTURE LINKAGE",
            f"Validation Key: {registry.get('future_validation_key')}",
            f"Completion Audit Key: {registry.get('future_completion_audit_key')}",
            f"Mutation Key: {registry.get('future_mutation_key')}",
            f"Generation Tracking Key: {registry.get('future_generation_tracking_key')}",
            "",
            "PERMISSIONS",
        ])

        for key, value in registry.get("permissions", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "RESULT",
            "12C.2 candidate blueprint population registration owner is complete.",
            "The blueprint population is now formally registered.",
            "12C.3 candidate blueprint population validation owner may begin.",
        ])

    else:
        lines.append("BLOCKERS")
        for blocker in blockers:
            lines.append(f"- {blocker}")

    return "\n".join(lines)


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
