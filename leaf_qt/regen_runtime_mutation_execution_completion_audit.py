OWNER_NAME = "REGEN_RUNTIME_MUTATION_EXECUTION_COMPLETION_AUDIT"
PHASE = "14A"

PASS_STATUS = "PASS_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_MUTATION_EXECUTION_PHASE_14A"


def attach_regen_runtime_mutation_execution_completion_audit(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_runtime_mutation_execution_completion_audit(results)
    results.update(payload)
    return results


def build_regen_runtime_mutation_execution_completion_audit(results):
    blockers = []

    requirements = {
        "regen_runtime_mutation_execution_registry_ready": "Runtime mutation execution registry is not ready.",
        "regen_runtime_mutation_execution_engine_ready": "Runtime mutation execution engine is not ready.",
        "regen_runtime_mutation_execution_validation_owner_ready": "Runtime mutation execution validation owner is not ready.",
        "regen_runtime_mutation_execution_history_owner_ready": "Runtime mutation execution history owner is not ready.",
        "regen_runtime_mutation_execution_report_owner_ready": "Runtime mutation execution report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("regen_runtime_candidate_record_count", 0) <= 0:
        blockers.append("No runtime candidate records were created.")

    required_false = {
        "regen_runtime_mutation_solver_executed": "Solver execution occurred in 14A.",
        "regen_runtime_mutation_candidate_evaluated": "Candidate evaluation occurred in 14A.",
        "regen_runtime_mutation_candidate_accepted": "Candidate acceptance occurred in 14A.",
        "regen_runtime_mutation_generation_advanced": "Generation advancement occurred in 14A.",
        "regen_runtime_mutation_live_geometry_committed": "Live geometry commit occurred in 14A.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_runtime_mutation_execution_completion_audit_complete": True,
        "phase_14a_runtime_mutation_execution_completion_audit_complete": True,
        "regen_runtime_mutation_execution_completion_audit_ready": ready,
        "regen_runtime_mutation_execution_completion_audit_status": status,
        "regen_runtime_mutation_execution_completion_audit_blockers": blockers,

        "phase_14a_complete": ready,
        "phase_14a_status": status,

        "phase_14b_runtime_candidate_evaluation_allowed": ready,
        "phase_14c_runtime_selection_allowed": False,
        "phase_14d_runtime_evolution_allowed": False,
        "phase_14e_runtime_convergence_allowed": False,
        "phase_14f_runtime_optimisation_audit_allowed": False,

        "phase_14_runtime_optimisation_allowed": False,

        "regen_runtime_candidate_evaluation_allowed": ready,
        "regen_runtime_mutation_solver_execution_allowed": False,
        "regen_runtime_mutation_candidate_acceptance_allowed": False,
        "regen_runtime_mutation_generation_advance_allowed": False,
        "regen_runtime_mutation_live_geometry_commit_allowed": False,
    }
