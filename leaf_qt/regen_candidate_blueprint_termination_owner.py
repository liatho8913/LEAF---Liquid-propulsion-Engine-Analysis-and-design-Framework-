"""
PHASE 12D.5
Candidate Blueprint Optimisation Termination Owner
"""

OWNER_NAME = "REGEN_CANDIDATE_BLUEPRINT_TERMINATION_OWNER"
PHASE = "12D.5"

PASS_STATUS = "PASS_REGEN_CANDIDATE_BLUEPRINT_TERMINATION_OWNER_PHASE_12D5"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_BLUEPRINT_TERMINATION_OWNER_PHASE_12D5"

TERMINATION_NOT_REQUIRED = "TERMINATION_NOT_REQUIRED"
TERMINATION_CONVERGED = "TERMINATION_CONVERGED"
TERMINATION_DIVERSITY_EXHAUSTED = "TERMINATION_DIVERSITY_EXHAUSTED"
TERMINATION_MAX_GENERATIONS = "TERMINATION_MAX_GENERATIONS"
TERMINATION_MANUAL_STOP = "TERMINATION_MANUAL_STOP"
TERMINATION_UNKNOWN = "TERMINATION_UNKNOWN"


def attach_regen_candidate_blueprint_termination_owner(results):
    if not isinstance(results, dict):
        return results
    results.update(build_regen_candidate_blueprint_termination_owner(results))
    return results


def build_regen_candidate_blueprint_termination_owner(results):
    blockers = []

    allowed = (
        results.get("phase_12d_5_candidate_blueprint_termination_owner_allowed") is True
        and results.get("regen_candidate_blueprint_termination_owner_allowed") is True
    )

    if not allowed:
        blockers.append("12D.4 convergence monitor has not allowed termination owner creation.")

    convergence_monitor = results.get("regen_candidate_blueprint_convergence_monitor", {})
    convergence_registry = results.get("regen_candidate_blueprint_convergence_registry", {})
    convergence_metrics = results.get("regen_candidate_blueprint_convergence_metrics", {})

    if not isinstance(convergence_monitor, dict) or convergence_monitor.get("ready") is not True:
        blockers.append("Convergence monitor is missing or not ready.")

    if not isinstance(convergence_registry, dict) or convergence_registry.get("ready") is not True:
        blockers.append("Convergence registry is missing or not ready.")

    if not isinstance(convergence_metrics, dict) or not convergence_metrics:
        blockers.append("Convergence metrics are missing.")

    _require_locked(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    owner = None
    if ready:
        owner = _build_termination_owner(convergence_monitor, convergence_registry, convergence_metrics)

    return {
        "regen_candidate_blueprint_termination_owner_complete": True,
        "phase_12d_5_regen_candidate_blueprint_termination_owner_complete": True,
        "regen_candidate_blueprint_termination_owner_ready": ready,
        "regen_candidate_blueprint_termination_owner_status": status,
        "regen_candidate_blueprint_termination_owner_blockers": blockers,

        "regen_candidate_blueprint_termination_owner": owner,
        "regen_candidate_blueprint_termination_registry": (
            owner.get("termination_registry") if isinstance(owner, dict) else None
        ),
        "regen_candidate_blueprint_termination_rules": (
            owner.get("termination_rules") if isinstance(owner, dict) else None
        ),
        "regen_candidate_blueprint_termination_lifecycle": (
            owner.get("termination_lifecycle") if isinstance(owner, dict) else None
        ),
        "regen_candidate_blueprint_termination_report": _report(status, ready, owner, blockers),

        "phase_12d_6_candidate_blueprint_optimisation_completion_audit_allowed": ready,
        "regen_candidate_blueprint_optimisation_completion_audit_allowed": ready,

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


def _build_termination_owner(convergence_monitor, convergence_registry, convergence_metrics):
    convergence_state = convergence_metrics.get("convergence_state")
    termination_state = _decide_termination_state(convergence_state)
    termination_required = termination_state != TERMINATION_NOT_REQUIRED

    rules = {
        "max_generations": 100,
        "minimum_uniqueness_ratio": 0.25,
        "allow_manual_termination": True,
        "allow_convergence_termination": True,
        "allow_diversity_termination": True,
    }

    registry = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "termination_registry_id": (
            f"TERMINATION_REGISTRY_FOR_{convergence_monitor.get('source_population_id')}"
        ),
        "source_population_id": convergence_monitor.get("source_population_id"),
        "source_convergence_registry_id": convergence_registry.get("convergence_registry_id"),
        "source_convergence_state": convergence_state,
        "registered_termination_states": [
            TERMINATION_NOT_REQUIRED,
            TERMINATION_CONVERGED,
            TERMINATION_DIVERSITY_EXHAUSTED,
            TERMINATION_MAX_GENERATIONS,
            TERMINATION_MANUAL_STOP,
            TERMINATION_UNKNOWN,
        ],
        "permissions": {
            "optimisation_completion_audit_allowed": True,
            "mutation_execution_allowed": False,
            "scoring_execution_allowed": False,
            "solver_execution_allowed": False,
            "candidate_acceptance_allowed": False,
            "live_geometry_commit_allowed": False,
        },
        "future_linkage": {
            "optimisation_completion_audit_key": (
                "regen_candidate_blueprint_optimisation_completion_audit"
            )
        },
    }

    lifecycle = {
        "termination_assessed": True,
        "termination_required": termination_required,
        "termination_state": termination_state,
        "optimisation_complete": termination_required,
        "mutation_executed": False,
        "scoring_executed": False,
        "solver_executed": False,
        "candidate_accepted": False,
        "live_geometry_committed": False,
    }

    return {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "status": PASS_STATUS,
        "ready": True,
        "termination_owner_state": "TERMINATION_OWNER_CREATED_EXECUTION_LOCKED",
        "termination_registry": registry,
        "termination_rules": rules,
        "termination_decision": {
            "convergence_state": convergence_state,
            "termination_state": termination_state,
            "termination_required": termination_required,
            "reason": _termination_reason(convergence_state, termination_state),
        },
        "termination_lifecycle": lifecycle,
        "termination_readiness": {
            "ready_for_optimisation_completion_audit": True,
            "ready_for_mutation_execution": False,
            "ready_for_scoring": False,
            "ready_for_solver_execution": False,
            "ready_for_candidate_acceptance": False,
            "ready_for_live_commit": False,
            "next_phase": "12D.6_CANDIDATE_BLUEPRINT_OPTIMISATION_COMPLETION_AUDIT",
        },
    }


def _decide_termination_state(convergence_state):
    if convergence_state in ("CONVERGENCE_HEALTHY", "CONVERGENCE_WARNING"):
        return TERMINATION_NOT_REQUIRED
    if convergence_state == "CONVERGENCE_STALLED":
        return TERMINATION_CONVERGED
    if convergence_state == "CONVERGENCE_EXHAUSTED":
        return TERMINATION_DIVERSITY_EXHAUSTED
    return TERMINATION_UNKNOWN


def _termination_reason(convergence_state, termination_state):
    if termination_state == TERMINATION_NOT_REQUIRED:
        return f"{convergence_state} does not require termination."
    if termination_state == TERMINATION_CONVERGED:
        return "Convergence monitor reports stalled diversity; termination may be required."
    if termination_state == TERMINATION_DIVERSITY_EXHAUSTED:
        return "Convergence monitor reports exhausted diversity; termination is required."
    return "Termination state could not be determined."


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


def _report(status, ready, owner, blockers):
    if not ready:
        return "PHASE 12D.5 BLOCKED\n" + "\n".join(f"- {b}" for b in blockers)

    decision = owner["termination_decision"]
    return (
        "PHASE 12D.5 REGEN CANDIDATE BLUEPRINT TERMINATION OWNER\n"
        f"Status: {status}\n"
        f"Termination State: {decision.get('termination_state')}\n"
        f"Termination Required: {decision.get('termination_required')}\n"
        "Mutation execution remains locked.\n"
        "12D.6 candidate blueprint optimisation completion audit may begin."
    )
