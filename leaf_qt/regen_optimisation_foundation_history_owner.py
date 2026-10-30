OWNER_NAME = "REGEN_OPTIMISATION_FOUNDATION_HISTORY_OWNER"
PHASE = "13L"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_FOUNDATION_HISTORY_OWNER_PHASE_13L"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_FOUNDATION_HISTORY_OWNER_PHASE_13L"


def attach_regen_optimisation_foundation_history_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_foundation_history_owner(results)
    results.update(payload)
    return results


def build_regen_optimisation_foundation_history_owner(results):
    blockers = []

    registry = results.get("regen_optimisation_foundation_registry")
    validation = results.get("regen_optimisation_foundation_validation")

    if not isinstance(registry, dict) or registry.get("ready") is not True:
        blockers.append("Optimisation foundation registry is not ready.")

    if not isinstance(validation, dict) or validation.get("ready") is not True:
        blockers.append("Optimisation foundation validation is not ready.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None

    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "OPTIMISATION_FOUNDATION_DECLARED_RUNTIME_LOCKED",
            "entries": [
                {
                    "entry_id": "OPTIMISATION_FOUNDATION_HISTORY_0001",
                    "event": "13K_SELECTION_FRAMEWORK_CONFIRMED",
                    "phase": "13K",
                    "status": results.get("phase_13k_status"),
                },
                {
                    "entry_id": "OPTIMISATION_FOUNDATION_HISTORY_0002",
                    "event": "13L_OPTIMISATION_FOUNDATION_REGISTERED",
                    "phase": "13L",
                    "status": status,
                },
                {
                    "entry_id": "OPTIMISATION_FOUNDATION_HISTORY_0003",
                    "event": "PHASE_14A_UNLOCKED_WITH_RUNTIME_LOCKS",
                    "phase": "14A",
                    "runtime_mutation_execution_allowed": True,
                    "solver_execution_allowed": False,
                    "live_geometry_commit_allowed": False,
                },
            ],
            "runtime_execution_count": 0,
            "solver_execution_count": 0,
            "generation_advance_count": 0,
            "candidate_acceptance_count": 0,
            "live_geometry_commit_count": 0,
        }

    return {
        "regen_optimisation_foundation_history_owner_complete": True,
        "phase_13l_optimisation_foundation_history_owner_complete": True,
        "regen_optimisation_foundation_history_owner_ready": ready,
        "regen_optimisation_foundation_history_owner_status": status,
        "regen_optimisation_foundation_history_owner_blockers": blockers,
        "regen_optimisation_foundation_history": history,
    }
