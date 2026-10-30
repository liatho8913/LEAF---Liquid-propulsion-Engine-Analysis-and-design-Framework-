OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_COMPLETION_REPORT_OWNER"
PHASE = "14F"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_REPORT_OWNER_PHASE_14F"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_COMPLETION_REPORT_OWNER_PHASE_14F"


def attach_regen_runtime_optimisation_completion_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if not isinstance(results.get("regen_runtime_optimisation_completion_history"), dict):
        blockers.append("Runtime optimisation completion history is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, results)

    results.update({
        "regen_runtime_optimisation_completion_report_owner_complete": True,
        "phase_14f_runtime_optimisation_completion_report_owner_complete": True,
        "regen_runtime_optimisation_completion_report_owner_ready": ready,
        "regen_runtime_optimisation_completion_report_owner_status": status,
        "regen_runtime_optimisation_completion_report_owner_blockers": blockers,
        "regen_runtime_optimisation_completion_report": report,
    })

    return results


def _ready_report(status, results):
    return "\n".join([
        "PHASE 14F RUNTIME OPTIMISATION COMPLETION AUDIT",
        f"Status: {status}",
        "",
        "Runtime Completion State:",
        f"- Complete: {results.get('regen_runtime_optimisation_complete')}",
        f"- Continue required: {results.get('runtime_optimisation_continue_required')}",
        f"- Reason: {results.get('runtime_optimisation_completion_reason')}",
        f"- Final best score: {results.get('runtime_optimisation_final_best_score')}",
        f"- Final generation: {results.get('runtime_optimisation_final_generation')}",
        "",
        "Execution Locks:",
        "- Live geometry commit: LOCKED",
        "- Visualisation layer: UNLOCKED NEXT",
    ])


def _blocked_report(blockers):
    lines = [
        "PHASE 14F RUNTIME OPTIMISATION COMPLETION AUDIT",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
