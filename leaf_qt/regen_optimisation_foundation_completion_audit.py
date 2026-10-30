OWNER_NAME = "REGEN_OPTIMISATION_FOUNDATION_COMPLETION_AUDIT"
PHASE = "13L"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_FOUNDATION_PHASE_13L"


def attach_regen_optimisation_foundation_completion_audit(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_foundation_completion_audit(results)
    results.update(payload)
    return results


def build_regen_optimisation_foundation_completion_audit(results):
    blockers = []

    requirements = {
        "regen_optimisation_foundation_registry_ready": "Optimisation foundation registry is not ready.",
        "regen_optimisation_foundation_validation_owner_ready": "Optimisation foundation validation owner is not ready.",
        "regen_optimisation_foundation_history_owner_ready": "Optimisation foundation history owner is not ready.",
        "regen_optimisation_foundation_report_owner_ready": "Optimisation foundation report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    required_false = {
        "regen_optimisation_foundation_runtime_execution_allowed": "Foundation runtime execution is not locked.",
        "regen_optimisation_foundation_solver_execution_allowed": "Foundation solver execution is not locked.",
        "regen_optimisation_foundation_candidate_acceptance_allowed": "Foundation candidate acceptance is not locked.",
        "regen_optimisation_foundation_generation_advance_allowed": "Foundation generation advance is not locked.",
        "regen_optimisation_foundation_live_geometry_commit_allowed": "Foundation live geometry commit is not locked.",
    }

    for key, message in required_false.items():
        if results.get(key) is not False:
            blockers.append(message)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_foundation_completion_audit_complete": True,
        "phase_13l_optimisation_foundation_completion_audit_complete": True,
        "regen_optimisation_foundation_completion_audit_ready": ready,
        "regen_optimisation_foundation_completion_audit_status": status,
        "regen_optimisation_foundation_completion_audit_blockers": blockers,

        "phase_13l_complete": ready,
        "phase_13l_status": status,

        "optimisation_foundation_complete": ready,
        "regen_optimisation_foundation_complete": ready,

        "phase_14_runtime_optimisation_allowed": False,
        "phase_14a_runtime_mutation_execution_allowed": ready,
        "phase_14b_runtime_candidate_evaluation_allowed": False,
        "phase_14c_runtime_selection_allowed": False,
        "phase_14d_runtime_evolution_allowed": False,
        "phase_14e_runtime_convergence_allowed": False,
        "phase_14f_runtime_optimisation_audit_allowed": False,
    }
