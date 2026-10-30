OWNER_NAME = "REGEN_OPTIMISATION_FOUNDATION_VALIDATION_OWNER"
PHASE = "13L"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_FOUNDATION_VALIDATION_OWNER_PHASE_13L"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_FOUNDATION_VALIDATION_OWNER_PHASE_13L"


def attach_regen_optimisation_foundation_validation_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_foundation_validation_owner(results)
    results.update(payload)
    return results


def build_regen_optimisation_foundation_validation_owner(results):
    blockers = []

    registry = results.get("regen_optimisation_foundation_registry")

    if not isinstance(registry, dict) or registry.get("ready") is not True:
        blockers.append("Optimisation foundation registry is missing or not ready.")

    required_prior_layers = {
        "phase_13k_complete": "Phase 13K selection framework is not complete.",
        "regen_optimisation_selection_master_gate_passed": "Phase 13K master gate has not passed.",
    }

    for key, message in required_prior_layers.items():
        if key in results and results.get(key) is not True:
            blockers.append(message)

    required_locks = {
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_generation_advance_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }

    for key, required in required_locks.items():
        if key in results and results.get(key) is not required:
            blockers.append(f"Execution lock failed: {key} must be {required}.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    return {
        "regen_optimisation_foundation_validation_owner_complete": True,
        "phase_13l_optimisation_foundation_validation_owner_complete": True,
        "regen_optimisation_foundation_validation_owner_ready": ready,
        "regen_optimisation_foundation_validation_owner_status": status,
        "regen_optimisation_foundation_validation_owner_blockers": blockers,
        "regen_optimisation_foundation_validation": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "runtime_execution_locked": True,
            "solver_execution_locked": True,
            "candidate_acceptance_locked": True,
            "generation_advance_locked": True,
            "live_geometry_commit_locked": True,
        },

        "regen_optimisation_foundation_runtime_execution_allowed": False,
        "regen_optimisation_foundation_solver_execution_allowed": False,
        "regen_optimisation_foundation_candidate_acceptance_allowed": False,
        "regen_optimisation_foundation_generation_advance_allowed": False,
        "regen_optimisation_foundation_live_geometry_commit_allowed": False,
    }
