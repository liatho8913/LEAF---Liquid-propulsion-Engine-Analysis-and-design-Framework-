OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_COMPLETION_AUDIT"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_FRAMEWORK_PHASE_13K"


def attach_regen_optimisation_selection_completion_audit(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_completion_audit(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_completion_audit(results):
    blockers = []

    requirements = {
        "regen_optimisation_selection_ranking_engine_ready": "Selection ranking engine is not ready.",
        "regen_optimisation_selection_registry_ready": "Selection registry is not ready.",
        "regen_optimisation_selection_validation_owner_ready": "Selection validation owner is not ready.",
        "regen_optimisation_selection_parent_pool_builder_ready": "Parent pool builder is not ready.",
        "regen_optimisation_selection_state_owner_ready": "Selection state owner is not ready.",
        "regen_optimisation_selection_history_owner_ready": "Selection history owner is not ready.",
        "regen_optimisation_selection_report_owner_ready": "Selection report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    _require_locks(results, blockers)

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_selection_completion_audit_complete": True,
        "phase_13k_selection_completion_audit_complete": True,
        "phase_13k_regen_optimisation_selection_framework_complete": ready,
        "regen_optimisation_selection_framework_complete": ready,
        "regen_optimisation_selection_completion_audit_ready": ready,
        "regen_optimisation_selection_completion_audit_status": status,
        "regen_optimisation_selection_completion_audit_blockers": blockers,

        "phase_13l_optimisation_foundation_allowed": ready,
        "regen_optimisation_foundation_phase_13l_allowed": ready,

        "regen_optimisation_selection_runtime_execution_allowed": False,
        "regen_optimisation_selection_generation_advance_allowed": False,
        "regen_optimisation_selection_solver_execution_allowed": False,
        "regen_optimisation_selection_candidate_acceptance_allowed": False,
        "regen_optimisation_selection_live_geometry_commit_allowed": False,
    }


def _require_locks(results, blockers):
    required_false_or_missing_ok = {
        "regen_optimisation_selection_runtime_execution_allowed": "13K runtime execution is not locked.",
        "regen_optimisation_selection_generation_advance_allowed": "13K generation advance is not locked.",
        "regen_optimisation_selection_solver_execution_allowed": "13K solver execution is not locked.",
        "regen_optimisation_selection_candidate_acceptance_allowed": "13K candidate acceptance is not locked.",
        "regen_optimisation_selection_live_geometry_commit_allowed": "13K live geometry commit is not locked.",
    }

    for key, message in required_false_or_missing_ok.items():
        if key in results and results.get(key) is not False:
            blockers.append(message)
