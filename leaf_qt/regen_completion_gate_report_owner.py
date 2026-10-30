OWNER_NAME = "REGEN_COMPLETION_GATE_REPORT_OWNER"
PHASE = "16F"

PASS_STATUS = "PASS_REGEN_COMPLETION_GATE_REPORT_OWNER_PHASE_16F"
FAIL_STATUS = "FAIL_REGEN_COMPLETION_GATE_REPORT_OWNER_PHASE_16F"


def attach_regen_completion_gate_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_completion_gate_validation_owner_ready") is not True:
        blockers.append("Regen completion gate validation owner is not ready.")

    checks = results.get("regen_completion_gate_validation_checks", [])
    if not isinstance(checks, list) or not checks:
        blockers.append("Regen completion gate validation checks are missing.")

    summary = {
        "phase": PHASE,
        "completed_phase_count": 18,
        "final_gate_ready": results.get("regen_completion_gate_validation_passed"),
        "validation_check_count": len(checks) if isinstance(checks, list) else 0,
        "blocking_issue_count": len(results.get("regen_completion_gate_validation_owner_blockers", [])),
        "regen_system_complete": False,
        "final_status_target": "PASS_REGEN_SYSTEM_COMPLETE",
    }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    report = _blocked_report(blockers) if not ready else _ready_report(status, summary)

    results.update({
        "regen_completion_gate_report_owner_complete": True,
        "phase_16f_regen_completion_gate_report_owner_complete": True,
        "regen_completion_gate_report_owner_ready": ready,
        "regen_completion_gate_report_owner_status": status,
        "regen_completion_gate_report_owner_blockers": blockers,

        "regen_completion_gate_summary": summary if ready else {},
        "regen_completion_gate_report": report,
    })

    return results


def _ready_report(status, summary):
    return "\n".join([
        "PHASE 16F REGEN COMPLETION MASTER GATE",
        f"Status: {status}",
        "",
        "Completion Gate Summary:",
        f"- Completed phase count: {summary.get('completed_phase_count')}",
        f"- Validation checks: {summary.get('validation_check_count')}",
        f"- Blocking issues: {summary.get('blocking_issue_count')}",
        f"- Final target: {summary.get('final_status_target')}",
        "",
        "If the final master gate passes, LEAF will emit:",
        "PASS_REGEN_SYSTEM_COMPLETE",
    ])


def _blocked_report(blockers):
    lines = [
        "PHASE 16F REGEN COMPLETION MASTER GATE",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
