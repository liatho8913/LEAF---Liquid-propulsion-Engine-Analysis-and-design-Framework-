OWNER_NAME = "REGEN_SYSTEM_SIGNOFF_REPORT_OWNER"
PHASE = "16E"

PASS_STATUS = "PASS_REGEN_SYSTEM_SIGNOFF_REPORT_OWNER_PHASE_16E"
FAIL_STATUS = "FAIL_REGEN_SYSTEM_SIGNOFF_REPORT_OWNER_PHASE_16E"


def attach_regen_system_signoff_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_system_signoff_validation_owner_ready") is not True:
        blockers.append("Regen system signoff validation owner is not ready.")

    checks = results.get("regen_system_signoff_validation_checks", [])
    if not isinstance(checks, list) or not checks:
        blockers.append("Regen system signoff validation checks are missing.")

    summary = {
        "phase": PHASE,
        "runtime_backend_complete": results.get("phase_14_runtime_backend_complete"),
        "viewer_backend_complete": results.get("phase_15a_complete"),
        "comparison_backend_complete": results.get("phase_15b_complete"),
        "evolution_tree_backend_complete": results.get("phase_15c_complete"),
        "report_backend_complete": results.get("phase_15d_complete"),
        "unified_ecosystem_complete": results.get("phase_16a_complete"),
        "viewer_integration_complete": results.get("phase_16b_complete"),
        "report_integration_complete": results.get("phase_16c_complete"),
        "validation_integration_complete": results.get("phase_16d_complete"),
        "validation_check_count": len(checks) if isinstance(checks, list) else 0,
        "blocking_issue_count": len(results.get("regen_system_signoff_validation_owner_blockers", [])),
    }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, summary)

    results.update({
        "regen_system_signoff_report_owner_complete": True,
        "phase_16e_regen_system_signoff_report_owner_complete": True,
        "regen_system_signoff_report_owner_ready": ready,
        "regen_system_signoff_report_owner_status": status,
        "regen_system_signoff_report_owner_blockers": blockers,

        "regen_system_signoff_summary": summary if ready else {},
        "regen_system_signoff_report": report,
    })

    return results


def _ready_report(status, summary):
    return "\n".join([
        "PHASE 16E REGEN SYSTEM SIGN-OFF AUDIT",
        f"Status: {status}",
        "",
        "Integrated Backend Layers:",
        f"- Runtime backend complete: {summary.get('runtime_backend_complete')}",
        f"- Viewer backend complete: {summary.get('viewer_backend_complete')}",
        f"- Candidate comparison backend complete: {summary.get('comparison_backend_complete')}",
        f"- Evolution tree backend complete: {summary.get('evolution_tree_backend_complete')}",
        f"- Optimisation report backend complete: {summary.get('report_backend_complete')}",
        f"- Unified ecosystem complete: {summary.get('unified_ecosystem_complete')}",
        f"- Viewer integration complete: {summary.get('viewer_integration_complete')}",
        f"- Report integration complete: {summary.get('report_integration_complete')}",
        f"- Validation integration complete: {summary.get('validation_integration_complete')}",
        "",
        "Signoff:",
        f"- Validation checks: {summary.get('validation_check_count')}",
        f"- Blocking issues: {summary.get('blocking_issue_count')}",
        "",
        "Next phase: 16F Regen Completion Master Gate.",
    ])


def _blocked_report(blockers):
    lines = [
        "PHASE 16E REGEN SYSTEM SIGN-OFF AUDIT",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
