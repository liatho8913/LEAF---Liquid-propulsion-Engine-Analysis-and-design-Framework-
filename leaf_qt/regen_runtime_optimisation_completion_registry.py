OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_COMPLETION_REGISTRY"
PHASE = "14F"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_REGISTRY_PHASE_14F"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_COMPLETION_REGISTRY_PHASE_14F"


def attach_regen_runtime_optimisation_completion_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_14f_runtime_optimisation_audit_allowed") is True
    phase_14e_complete = (
        results.get("phase_14e_complete") is True
        or results.get("phase_14e_status") == "PASS_REGEN_RUNTIME_CONVERGENCE_PHASE_14E"
    )

    if not allowed:
        blockers.append("Phase 14F has not been unlocked by Phase 14E.")

    if not phase_14e_complete:
        blockers.append("Phase 14E runtime convergence is not complete.")

    if results.get("runtime_stop_condition_checked") is not True:
        blockers.append("Runtime stop condition was not checked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_optimisation_completion_registry_complete": True,
        "phase_14f_runtime_optimisation_completion_registry_complete": True,
        "regen_runtime_optimisation_completion_registry_ready": ready,
        "regen_runtime_optimisation_completion_registry_status": status,
        "regen_runtime_optimisation_completion_registry_blockers": blockers,
        "regen_runtime_optimisation_completion_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "completion_audit_allowed": ready,
            "final_runtime_status_allowed": ready,
            "live_geometry_commit_allowed": False,
            "visualisation_allowed_next": True if ready else False,
        } if ready else None,
    })

    return results
