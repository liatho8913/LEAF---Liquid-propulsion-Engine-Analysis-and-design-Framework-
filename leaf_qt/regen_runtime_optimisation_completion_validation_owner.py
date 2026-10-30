OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_COMPLETION_VALIDATION_OWNER"
PHASE = "14F"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_VALIDATION_OWNER_PHASE_14F"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_COMPLETION_VALIDATION_OWNER_PHASE_14F"


def attach_regen_runtime_optimisation_completion_validation_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_optimisation_completion_audit_ready") is not True:
        blockers.append("Runtime optimisation completion audit is not ready.")

    if not isinstance(results.get("regen_runtime_optimisation_completion_record"), dict):
        blockers.append("Runtime optimisation completion record is missing.")

    if results.get("regen_runtime_final_live_geometry_committed") is not False:
        blockers.append("Live geometry was illegally committed in Phase 14F.")

    complete = results.get("regen_runtime_optimisation_complete") is True
    continue_required = results.get("runtime_optimisation_continue_required") is True

    if complete and continue_required:
        blockers.append("Optimisation cannot be both complete and continue-required.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_optimisation_completion_validation_owner_complete": True,
        "phase_14f_runtime_optimisation_completion_validation_owner_complete": True,
        "regen_runtime_optimisation_completion_validation_owner_ready": ready,
        "regen_runtime_optimisation_completion_validation_owner_status": status,
        "regen_runtime_optimisation_completion_validation_owner_blockers": blockers,
        "regen_runtime_optimisation_completion_validation": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "runtime_optimisation_complete": complete,
            "continue_required": continue_required,
            "live_geometry_commit_locked": True,
        },
    })

    return results
