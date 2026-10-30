"""
PHASE 13A
Autonomous Blueprint Mutation Execution Foundation

Creates the execution governance layer for future real blueprint mutation.

Does NOT:
- mutate real geometry yet
- run solver
- score candidates
- accept candidates
- commit live geometry
"""

OWNER_NAME = "REGEN_AUTONOMOUS_BLUEPRINT_MUTATION_EXECUTION_FOUNDATION"
PHASE = "13A"

PASS_STATUS = "PASS_REGEN_AUTONOMOUS_BLUEPRINT_MUTATION_EXECUTION_FOUNDATION_PHASE_13A"
FAIL_STATUS = "FAIL_REGEN_AUTONOMOUS_BLUEPRINT_MUTATION_EXECUTION_FOUNDATION_PHASE_13A"


def attach_regen_autonomous_blueprint_mutation_execution_foundation(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_autonomous_blueprint_mutation_execution_foundation(results))
    return results


def build_regen_autonomous_blueprint_mutation_execution_foundation(results):
    blockers = []

    allowed = (
        results.get("phase_13a_autonomous_blueprint_mutation_execution_foundation_allowed") is True
        and results.get("regen_autonomous_blueprint_mutation_execution_foundation_allowed") is True
        and results.get("regen_candidate_blueprint_optimisation_foundation_complete") is True
    )

    if not allowed:
        blockers.append("Phase 12 optimisation foundation has not allowed Phase 13A.")

    optimisation_audit = results.get("regen_candidate_blueprint_optimisation_completion_audit", {})
    population = results.get("regen_candidate_blueprint_population", {})

    if not isinstance(optimisation_audit, dict) or optimisation_audit.get("ready") is not True:
        blockers.append("Optimisation completion audit is missing or not ready.")

    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    foundation = None
    if ready:
        foundation = _build_execution_foundation(population, optimisation_audit)

    return {
        "regen_autonomous_blueprint_mutation_execution_foundation_complete": True,
        "phase_13a_regen_autonomous_blueprint_mutation_execution_foundation_complete": True,
        "regen_autonomous_blueprint_mutation_execution_foundation_ready": ready,
        "regen_autonomous_blueprint_mutation_execution_foundation_status": status,
        "regen_autonomous_blueprint_mutation_execution_foundation_blockers": blockers,

        "regen_autonomous_blueprint_mutation_execution_foundation": foundation,
        "regen_autonomous_blueprint_mutation_execution_registry": (
            foundation.get("mutation_execution_registry") if isinstance(foundation, dict) else None
        ),
        "regen_autonomous_blueprint_mutation_execution_history": (
            foundation.get("mutation_execution_history") if isinstance(foundation, dict) else None
        ),
        "regen_autonomous_blueprint_mutation_execution_report": _report(
            status, ready, foundation, blockers
        ),

        "phase_13b_channel_count_mutation_allowed": ready,
        "regen_channel_count_mutation_allowed": ready,

        "regen_candidate_blueprint_mutation_execution_allowed": False,
        "regen_real_geometry_mutation_allowed": False,
        "regen_solver_execution_from_mutation_allowed": False,
        "regen_candidate_acceptance_from_mutation_allowed": False,
        "regen_live_geometry_commit_from_mutation_allowed": False,

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


def _build_execution_foundation(population, optimisation_audit):
    population_id = population.get("population_id")

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "mutation_execution_registry_id": f"MUTATION_EXECUTION_REGISTRY_FOR_{population_id}",
        "source_population_id": population_id,
        "source_optimisation_foundation_state": optimisation_audit.get(
            "optimisation_foundation_state"
        ),
        "registered_future_mutation_axes": [
            "number_of_coolant_channels",
            "coolant_channel_width",
            "coolant_channel_height",
            "rib_width",
            "hot_gas_wall_thickness",
            "coolant_flow_fraction",
        ],
        "registered_execution_modes": [
            "dry_run_mutation_plan",
            "bounded_geometry_mutation",
            "single_axis_mutation",
            "multi_axis_mutation",
            "baseline_preservation",
        ],
        "permissions": {
            "channel_count_mutation_allowed": True,
            "real_geometry_mutation_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
        "future_linkage": {
            "channel_count_mutation_key": "regen_channel_count_mutation",
            "channel_width_mutation_key": "regen_channel_width_mutation",
            "channel_height_mutation_key": "regen_channel_height_mutation",
            "rib_width_mutation_key": "regen_rib_width_mutation",
            "wall_thickness_mutation_key": "regen_wall_thickness_mutation",
            "coolant_split_mutation_key": "regen_coolant_split_mutation",
        },
    }

    history = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "history_state": "MUTATION_EXECUTION_HISTORY_CREATED_NO_MUTATIONS_RUN",
        "mutation_attempt_count": 0,
        "successful_mutation_count": 0,
        "failed_mutation_count": 0,
        "real_geometry_mutation_count": 0,
        "solver_execution_count": 0,
        "live_commit_count": 0,
        "entries": [],
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "execution_foundation_state": "MUTATION_EXECUTION_FOUNDATION_CREATED_REAL_MUTATION_LOCKED",
        "mutation_execution_registry": registry,
        "mutation_execution_history": history,
        "mutation_execution_lifecycle": {
            "foundation_created": True,
            "real_mutation_enabled": False,
            "mutation_executed": False,
            "solver_executed": False,
            "candidate_accepted": False,
            "live_geometry_committed": False,
        },
        "mutation_execution_readiness": {
            "ready_for_channel_count_mutation_foundation": True,
            "ready_for_real_geometry_mutation": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "13B_CHANNEL_COUNT_MUTATION_FOUNDATION",
        },
    }


def _require_locked(results, blockers):
    required_false = {
        "regen_candidate_blueprint_mutation_execution_allowed": "Candidate blueprint mutation execution is not safely locked.",
        "regen_candidate_blueprint_generation_execution_allowed": "Blueprint generation execution is not safely locked.",
        "regen_candidate_blueprint_create_blueprints_allowed": "Blueprint creation is not safely locked.",
        "regen_candidate_creation_create_candidates_allowed": "Candidate creation is not safely locked.",
        "regen_candidate_generation_create_candidates_allowed": "Candidate generation is not safely locked.",
        "regen_optimisation_runtime_execution_allowed": "Runtime optimisation execution is not safely locked.",
        "regen_optimisation_generation_advance_allowed": "Population generation advance is not safely locked.",
        "regen_optimisation_mutation_execution_allowed": "Mutation execution is not safely locked.",
        "regen_optimisation_candidate_acceptance_allowed": "Candidate acceptance is not safely locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Live geometry commit is not safely locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)


def _report(status, ready, foundation, blockers):
    if not ready:
        return "PHASE 13A BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)

    registry = foundation["mutation_execution_registry"]
    return (
        "PHASE 13A REGEN AUTONOMOUS BLUEPRINT MUTATION EXECUTION FOUNDATION\n"
        f"Status: {status}\n"
        f"Registry: {registry.get('mutation_execution_registry_id')}\n"
        "Real mutation execution remains locked.\n"
        "13B channel count mutation foundation may begin."
    )
