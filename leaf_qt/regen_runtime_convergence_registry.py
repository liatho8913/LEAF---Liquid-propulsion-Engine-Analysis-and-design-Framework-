OWNER_NAME = "REGEN_RUNTIME_CONVERGENCE_REGISTRY"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_CONVERGENCE_REGISTRY_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CONVERGENCE_REGISTRY_PHASE_14E"


def attach_regen_runtime_convergence_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_14e_runtime_convergence_allowed") is True
    phase_14d_complete = (
        results.get("phase_14d_complete") is True
        or results.get("phase_14d_status") == "PASS_REGEN_RUNTIME_EVOLUTION_PHASE_14D"
    )

    if not allowed:
        blockers.append("Phase 14E has not been unlocked by Phase 14D.")

    if not phase_14d_complete:
        blockers.append("Phase 14D runtime evolution is not complete.")

    history = results.get("runtime_generation_history", [])
    parent_pool = results.get("regen_runtime_parent_pool", [])

    if not isinstance(history, list):
        blockers.append("Runtime generation history is not available.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Runtime parent pool is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_convergence_registry_complete": True,
        "phase_14e_runtime_convergence_registry_complete": True,
        "regen_runtime_convergence_registry_ready": ready,
        "regen_runtime_convergence_registry_status": status,
        "regen_runtime_convergence_registry_blockers": blockers,
        "regen_runtime_convergence_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "improvement_tracking_allowed": ready,
            "stagnation_detection_allowed": ready,
            "convergence_detection_allowed": ready,
            "stop_condition_detection_allowed": ready,
            "optimisation_completion_allowed": False,
            "live_geometry_commit_allowed": False,
        } if ready else None,
    })

    return results
