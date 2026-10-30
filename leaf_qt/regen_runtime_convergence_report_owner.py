OWNER_NAME = "REGEN_RUNTIME_CONVERGENCE_REPORT_OWNER"
PHASE = "14E"

PASS_STATUS = "PASS_REGEN_RUNTIME_CONVERGENCE_REPORT_OWNER_PHASE_14E"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CONVERGENCE_REPORT_OWNER_PHASE_14E"


def attach_regen_runtime_convergence_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    history = results.get("regen_runtime_convergence_history")

    if not isinstance(history, dict):
        blockers.append("Runtime convergence history is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, results)

    results.update({
        "regen_runtime_convergence_report_owner_complete": True,
        "phase_14e_runtime_convergence_report_owner_complete": True,
        "regen_runtime_convergence_report_owner_ready": ready,
        "regen_runtime_convergence_report_owner_status": status,
        "regen_runtime_convergence_report_owner_blockers": blockers,
        "regen_runtime_convergence_report": report,
    })

    return results


def _ready_report(status, results):
    lines = [
        "PHASE 14E RUNTIME CONVERGENCE ENGINE",
        f"Status: {status}",
        "",
        "Improvement Tracking:",
        f"- Previous best score: {results.get('runtime_previous_best_score')}",
        f"- Current best score: {results.get('runtime_current_best_score')}",
        f"- Generation improvement: {results.get('runtime_generation_improvement')}",
        "",
        "Stagnation:",
        f"- Stagnation count: {results.get('runtime_stagnation_count')}",
        f"- Stagnation limit: {results.get('runtime_stagnation_limit')}",
        f"- Limit reached: {results.get('runtime_stagnation_limit_reached')}",
        "",
        "Convergence:",
        f"- Convergence detected: {results.get('runtime_convergence_detected')}",
        f"- Stop recommended: {results.get('runtime_stop_recommended')}",
        f"- Stop reason: {results.get('runtime_stop_reason')}",
        "",
        "Execution Locks:",
        "- Optimisation completion: LOCKED UNTIL 14F",
        "- Live geometry commit: LOCKED",
    ]

    return "\n".join(lines)


def _blocked_report(blockers):
    lines = [
        "PHASE 14E RUNTIME CONVERGENCE ENGINE",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
