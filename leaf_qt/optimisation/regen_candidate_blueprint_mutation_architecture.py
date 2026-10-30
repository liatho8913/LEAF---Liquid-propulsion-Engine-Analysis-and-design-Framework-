"""
PHASE 12D.1
Candidate Blueprint Mutation Architecture

Creates the mutation governance architecture for a completed blueprint population.

Does NOT:
- mutate geometry
- score candidates
- run solver
- accept candidates
- evolve populations
- commit geometry
"""

from datetime import datetime, timezone

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_MUTATION_ARCHITECTURE"
PHASE = "12D.1"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_MUTATION_ARCHITECTURE_PHASE_12D1"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_MUTATION_ARCHITECTURE_PHASE_12D1"


def attach_regen_candidate_blueprint_mutation_architecture(results):
    if not isinstance(results, dict):
        return results

    results.update(build_regen_candidate_blueprint_mutation_architecture(results))
    return results


def build_regen_candidate_blueprint_mutation_architecture(results):
    blockers = []

    allowed = (
        results.get("phase_12d_1_candidate_blueprint_mutation_architecture_allowed") is True
        and results.get("regen_candidate_blueprint_mutation_architecture_allowed") is True
        and results.get("regen_candidate_blueprint_population_architecture_complete") is True
    )

    if not allowed:
        blockers.append("12C population architecture has not allowed mutation architecture.")

    population = results.get("regen_candidate_blueprint_population", {})
    population_audit = results.get("regen_candidate_blueprint_population_completion_audit", {})

    if not isinstance(population, dict) or not population:
        blockers.append("Candidate blueprint population is missing.")

    if not isinstance(population_audit, dict) or population_audit.get("ready") is not True:
        blockers.append("Population completion audit is missing or not ready.")

    if isinstance(population, dict) and population.get("member_count", 0) <= 0:
        blockers.append("Population has no members for mutation architecture.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    architecture = None
    if ready:
        architecture = _build_mutation_architecture(population, population_audit)

    report = build_report(status, ready, architecture, blockers)

    return {
        "regen_candidate_blueprint_mutation_architecture_complete": True,
        "phase_12d_1_regen_candidate_blueprint_mutation_architecture_complete": True,
        "regen_candidate_blueprint_mutation_architecture_ready": ready,
        "regen_candidate_blueprint_mutation_architecture_status": status,
        "regen_candidate_blueprint_mutation_architecture_blockers": blockers,

        "regen_candidate_blueprint_mutation_architecture": architecture,
        "regen_candidate_blueprint_mutation_session": (
            architecture.get("mutation_session") if isinstance(architecture, dict) else None
        ),
        "regen_candidate_blueprint_mutation_registry": (
            architecture.get("mutation_registry") if isinstance(architecture, dict) else None
        ),
        "regen_candidate_blueprint_mutation_architecture_report": report,

        "phase_12d_2_candidate_blueprint_mutation_validation_allowed": ready,
        "regen_candidate_blueprint_mutation_validation_allowed": ready,

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


def _build_mutation_architecture(population, population_audit):
    population_id = population.get("population_id")
    timestamp = datetime.now(timezone.utc).isoformat()

    session_id = f"MUTATION_SESSION_FOR_{population_id}"
    registry_id = f"MUTATION_REGISTRY_FOR_{population_id}"

    session = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "mutation_session_id": session_id,
        "source_population_id": population_id,
        "source_population_member_count": population.get("member_count"),
        "created_utc": timestamp,
        "lifecycle_state": "MUTATION_SESSION_CREATED_EXECUTION_LOCKED",
        "mutation_execution_allowed": False,
        "next_phase": "12D.2_CANDIDATE_BLUEPRINT_MUTATION_VALIDATION",
    }

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "mutation_registry_id": registry_id,
        "mutation_session_id": session_id,
        "source_population_id": population_id,
        "source_population_architecture_state": population_audit.get("population_architecture_state"),
        "registered_mutation_scopes": [
            "number_of_coolant_channels",
            "coolant_channel_width",
            "coolant_channel_height",
            "rib_width",
            "hot_gas_wall_thickness",
            "coolant_flow_fraction",
        ],
        "registered_mutation_modes": [
            "scale_up",
            "scale_down",
            "bounded_integer_step",
            "bounded_float_step",
            "no_op_baseline_preservation",
        ],
        "permissions": {
            "mutation_validation_allowed": True,
            "mutation_execution_allowed": False,
            "scoring_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
        "future_linkage": {
            "mutation_validation_key": "regen_candidate_blueprint_mutation_validation",
            "diversity_controller_key": "regen_candidate_blueprint_diversity_controller",
            "convergence_monitor_key": "regen_candidate_blueprint_convergence_monitor",
            "termination_owner_key": "regen_candidate_blueprint_termination_owner",
            "optimisation_completion_audit_key": "regen_candidate_blueprint_optimisation_completion_audit",
        },
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "architecture_state": "MUTATION_ARCHITECTURE_CREATED_EXECUTION_LOCKED",
        "mutation_session": session,
        "mutation_registry": registry,
        "mutation_lifecycle": {
            "architecture_created": True,
            "validation_complete": False,
            "execution_enabled": False,
            "mutation_executed": False,
            "scoring_executed": False,
            "solver_executed": False,
            "candidate_accepted": False,
            "live_geometry_committed": False,
        },
    }


def build_report(status, ready, architecture, blockers):
    lines = [
        "PHASE 12D.1 REGEN CANDIDATE BLUEPRINT MUTATION ARCHITECTURE",
        "",
        f"Owner: {OWNER_NAME}",
        f"Status: {status}",
        f"Ready for 12D.2 Candidate Blueprint Mutation Validation: {ready}",
        "",
    ]

    if architecture:
        session = architecture.get("mutation_session", {})
        registry = architecture.get("mutation_registry", {})

        lines.extend([
            "MUTATION SESSION",
            f"Session ID: {session.get('mutation_session_id')}",
            f"Source Population ID: {session.get('source_population_id')}",
            f"Lifecycle State: {session.get('lifecycle_state')}",
            "",
            "MUTATION REGISTRY",
            f"Registry ID: {registry.get('mutation_registry_id')}",
            f"Registered Scopes: {registry.get('registered_mutation_scopes')}",
            f"Registered Modes: {registry.get('registered_mutation_modes')}",
            "",
            "PERMISSIONS",
        ])

        for key, value in registry.get("permissions", {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "SAFETY STATE",
            "- Mutation validation: allowed next",
            "- Mutation execution: locked",
            "- Scoring: locked",
            "- Solver execution: locked",
            "- Candidate acceptance: locked",
            "- Live geometry commit: locked",
            "",
            "RESULT",
            "12D.1 candidate blueprint mutation architecture is complete.",
            "Mutation governance exists, but mutation execution remains locked.",
            "12D.2 candidate blueprint mutation validation may begin.",
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
