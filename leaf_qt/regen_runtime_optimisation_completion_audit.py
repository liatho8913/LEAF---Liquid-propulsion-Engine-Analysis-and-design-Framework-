OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_COMPLETION_AUDIT"
PHASE = "14F"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_AUDIT_PHASE_14F"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_COMPLETION_AUDIT_PHASE_14F"


def attach_regen_runtime_optimisation_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_runtime_optimisation_completion_registry_ready") is not True:
        blockers.append("Runtime optimisation completion registry is not ready.")

    stop_checked = results.get("runtime_stop_condition_checked") is True
    stop_recommended = results.get("runtime_stop_recommended") is True
    convergence_detected = results.get("runtime_convergence_detected") is True
    max_generation_reached = results.get("runtime_max_generation_reached") is True

    if not stop_checked:
        blockers.append("Runtime stop condition was not checked.")

    complete = bool(stop_checked and stop_recommended and (convergence_detected or max_generation_reached))

    completion_reason = _completion_reason(
        convergence_detected=convergence_detected,
        max_generation_reached=max_generation_reached,
        stop_recommended=stop_recommended,
    )

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_optimisation_completion_audit_complete": True,
        "phase_14f_runtime_optimisation_completion_audit_complete": True,
        "regen_runtime_optimisation_completion_audit_ready": ready,
        "regen_runtime_optimisation_completion_audit_status": status,
        "regen_runtime_optimisation_completion_audit_blockers": blockers,

        "regen_runtime_optimisation_complete": complete if ready else False,
        "runtime_optimisation_complete": complete if ready else False,
        "runtime_optimisation_completion_reason": completion_reason if ready else "BLOCKED",
        "runtime_optimisation_continue_required": bool(ready and not complete),
        "runtime_optimisation_final_best_score": results.get("runtime_current_best_score"),
        "runtime_optimisation_final_generation": results.get("runtime_generation_advance_to", results.get("runtime_generation_number")),

        "regen_runtime_optimisation_completion_record": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "runtime_optimisation_complete": complete,
            "continue_required": bool(not complete),
            "completion_reason": completion_reason,
            "stop_recommended": stop_recommended,
            "convergence_detected": convergence_detected,
            "max_generation_reached": max_generation_reached,
            "live_geometry_committed": False,
        } if ready else None,

        "regen_runtime_final_live_geometry_committed": False,
    })

    return results


def _completion_reason(convergence_detected, max_generation_reached, stop_recommended):
    if convergence_detected:
        return "OPTIMISATION_COMPLETE_CONVERGENCE_DETECTED"
    if max_generation_reached:
        return "OPTIMISATION_COMPLETE_MAX_GENERATION_REACHED"
    if not stop_recommended:
        return "OPTIMISATION_CONTINUE_STOP_NOT_RECOMMENDED"
    return "OPTIMISATION_CONTINUE_NO_TERMINATION_REASON"
