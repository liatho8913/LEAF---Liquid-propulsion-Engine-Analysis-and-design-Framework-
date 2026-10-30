"""
PHASE 12D.4
Candidate Blueprint Convergence Monitor
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_CONVERGENCE_MONITOR"
PHASE = "12D.4"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_CONVERGENCE_MONITOR_PHASE_12D4"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_CONVERGENCE_MONITOR_PHASE_12D4"

CONVERGENCE_HEALTHY = "CONVERGENCE_HEALTHY"
CONVERGENCE_WARNING = "CONVERGENCE_WARNING"
CONVERGENCE_STALLED = "CONVERGENCE_STALLED"
CONVERGENCE_EXHAUSTED = "CONVERGENCE_EXHAUSTED"


def attach_regen_candidate_blueprint_convergence_monitor(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_candidate_blueprint_convergence_monitor(results))
    return results


def build_regen_candidate_blueprint_convergence_monitor(results):
    blockers = []

    allowed = (
        results.get("phase_12d_4_candidate_blueprint_convergence_monitor_allowed") is True
        and results.get("regen_candidate_blueprint_convergence_monitor_allowed") is True
    )

    if not allowed:
        blockers.append("12D.3 diversity controller has not allowed convergence monitor creation.")

    diversity_controller = results.get("regen_candidate_blueprint_diversity_controller", {})
    diversity_registry = results.get("regen_candidate_blueprint_diversity_registry", {})
    diversity_metrics = results.get("regen_candidate_blueprint_diversity_metrics", {})
    population = results.get("regen_candidate_blueprint_population", {})

    if not isinstance(diversity_controller, dict) or diversity_controller.get("ready") is not True:
        blockers.append("Diversity controller is missing or not ready.")

    if not isinstance(diversity_registry, dict) or diversity_registry.get("ready") is not True:
        blockers.append("Diversity registry is missing or not ready.")

    if not isinstance(diversity_metrics, dict) or not diversity_metrics:
        blockers.append("Diversity metrics are missing.")

    if not isinstance(population, dict) or population.get("ready") is not True:
        blockers.append("Candidate blueprint population is missing or not ready.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    monitor = None
    if ready:
        monitor = _build_monitor(population, diversity_controller, diversity_registry, diversity_metrics)

    return {
        "regen_candidate_blueprint_convergence_monitor_complete": True,
        "phase_12d_4_regen_candidate_blueprint_convergence_monitor_complete": True,
        "regen_candidate_blueprint_convergence_monitor_ready": ready,
        "regen_candidate_blueprint_convergence_monitor_status": status,
        "regen_candidate_blueprint_convergence_monitor_blockers": blockers,
        "regen_candidate_blueprint_convergence_monitor": monitor,
        "regen_candidate_blueprint_convergence_registry": monitor.get("convergence_registry") if monitor else None,
        "regen_candidate_blueprint_convergence_metrics": monitor.get("convergence_metrics") if monitor else None,
        "regen_candidate_blueprint_convergence_monitor_report": _report(status, ready, monitor, blockers),
        "phase_12d_5_candidate_blueprint_termination_owner_allowed": ready,
        "regen_candidate_blueprint_termination_owner_allowed": ready,
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


def _build_monitor(population, diversity_controller, diversity_registry, diversity_metrics):
    ratio = float(diversity_metrics.get("geometry_uniqueness_ratio", 0.0))
    state = _classify(ratio)

    metrics = {
        "status": "CONVERGENCE_METRICS_CREATED",
        "population_size": int(diversity_metrics.get("member_count", 0)),
        "unique_geometry_count": int(diversity_metrics.get("unique_geometry_signature_count", 0)),
        "duplicate_geometry_count": int(diversity_metrics.get("duplicate_geometry_signature_count", 0)),
        "geometry_uniqueness_ratio": ratio,
        "convergence_state": state,
        "convergence_blocking": False,
        "score_convergence_assessed": False,
        "objective_improvement_assessed": False,
        "generation_history_assessed": False,
    }

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "convergence_registry_id": f"CONVERGENCE_REGISTRY_FOR_{population.get('population_id')}",
        "source_population_id": population.get("population_id"),
        "source_diversity_registry_id": diversity_registry.get("diversity_registry_id"),
        "source_diversity_controller_state": diversity_controller.get("diversity_controller_state"),
        "registered_convergence_states": [
            CONVERGENCE_HEALTHY,
            CONVERGENCE_WARNING,
            CONVERGENCE_STALLED,
            CONVERGENCE_EXHAUSTED,
        ],
        "permissions": {
            "termination_owner_allowed": True,
            "mutation_execution_allowed": False,
            "scoring_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
        "future_linkage": {
            "termination_owner_key": "regen_candidate_blueprint_termination_owner",
            "optimisation_completion_audit_key": "regen_candidate_blueprint_optimisation_completion_audit",
        },
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "convergence_monitor_state": "CONVERGENCE_MONITOR_CREATED_EXECUTION_LOCKED",
        "source_population_id": population.get("population_id"),
        "convergence_registry": registry,
        "convergence_metrics": metrics,
        "convergence_lifecycle": {
            "monitor_created": True,
            "convergence_assessed": True,
            "mutation_executed": False,
            "scoring_executed": False,
            "solver_executed": False,
            "candidate_accepted": False,
            "live_geometry_committed": False,
        },
        "convergence_readiness": {
            "ready_for_termination_owner": True,
            "ready_for_mutation_execution": False,
            "ready_for_scoring": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "12D.5_CANDIDATE_BLUEPRINT_TERMINATION_OWNER",
        },
    }


def _classify(ratio):
    if ratio >= 0.90:
        return CONVERGENCE_HEALTHY
    if ratio >= 0.75:
        return CONVERGENCE_WARNING
    if ratio >= 0.50:
        return CONVERGENCE_STALLED
    return CONVERGENCE_EXHAUSTED


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


def _report(status, ready, monitor, blockers):
    if not ready:
        return "PHASE 12D.4 BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)

    metrics = monitor["convergence_metrics"]
    return (
        "PHASE 12D.4 REGEN CANDIDATE BLUEPRINT CONVERGENCE MONITOR\n"
        f"Status: {status}\n"
        f"Convergence State: {metrics.get('convergence_state')}\n"
        "Mutation execution remains locked.\n"
        "12D.5 candidate blueprint termination owner may begin."
    )
