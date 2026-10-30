OWNER_NAME = "REGEN_RUNTIME_CANDIDATE_EVALUATION_COMPLETION_AUDIT"
PHASE = "14B"

PASS_STATUS = "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CANDIDATE_EVALUATION_PHASE_14B"


def attach_regen_runtime_candidate_evaluation_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_runtime_candidate_evaluation_registry_ready": "Evaluation registry is not ready.",
        "regen_runtime_candidate_evaluation_engine_ready": "Evaluation engine is not ready.",
        "regen_runtime_candidate_evaluation_validation_owner_ready": "Evaluation validation owner is not ready.",
        "regen_runtime_candidate_evaluation_history_owner_ready": "Evaluation history owner is not ready.",
        "regen_runtime_candidate_evaluation_report_owner_ready": "Evaluation report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("regen_runtime_candidate_evaluation_record_count", 0) <= 0:
        blockers.append("No runtime candidate evaluation records were produced.")

    required_false = {
        "regen_runtime_candidate_accepted": "Candidate acceptance occurred in 14B.",
        "regen_runtime_candidate_generation_advanced": "Generation advancement occurred in 14B.",
        "regen_runtime_candidate_live_geometry_committed": "Live geometry commit occurred in 14B.",
        "regen_optimisation_candidate_acceptance_allowed": "Global candidate acceptance is not locked.",
        "regen_generation_advance_execution_allowed": "Global generation advance is not locked.",
        "regen_optimisation_live_geometry_commit_allowed": "Global live geometry commit is not locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_candidate_evaluation_completion_audit_complete": True,
        "phase_14b_runtime_candidate_evaluation_completion_audit_complete": True,
        "regen_runtime_candidate_evaluation_completion_audit_ready": ready,
        "regen_runtime_candidate_evaluation_completion_audit_status": status,
        "regen_runtime_candidate_evaluation_completion_audit_blockers": blockers,

        "phase_14b_complete": ready,
        "phase_14b_status": status,

        "phase_14c_runtime_selection_allowed": ready,
        "phase_14d_runtime_evolution_allowed": False,
        "phase_14e_runtime_convergence_allowed": False,
        "phase_14f_runtime_optimisation_audit_allowed": False,
        "phase_14_runtime_optimisation_allowed": False,
    })

    return results
