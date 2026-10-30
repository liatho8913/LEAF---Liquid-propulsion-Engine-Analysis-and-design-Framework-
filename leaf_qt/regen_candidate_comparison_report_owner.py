OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_REPORT_OWNER"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_REPORT_OWNER_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_REPORT_OWNER_PHASE_15B"


def attach_regen_candidate_comparison_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if not isinstance(results.get("candidate_comparison_history"), dict):
        blockers.append("Candidate comparison history is missing.")

    if not isinstance(results.get("candidate_comparison_summary"), dict):
        blockers.append("Candidate comparison summary is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, results)

    results.update({
        "regen_candidate_comparison_report_owner_complete": True,
        "phase_15b_candidate_comparison_report_owner_complete": True,
        "regen_candidate_comparison_report_owner_ready": ready,
        "regen_candidate_comparison_report_owner_status": status,
        "regen_candidate_comparison_report_owner_blockers": blockers,
        "candidate_comparison_backend_report": report,
    })

    return results


def _ready_report(status, results):
    summary = results.get("candidate_comparison_summary", {})
    deltas = results.get("candidate_comparison_deltas", {})

    return "\n".join([
        "PHASE 15B CANDIDATE COMPARISON VIEWER BACKEND",
        f"Status: {status}",
        "",
        "Comparison Targets:",
        f"- Baseline: {summary.get('baseline_id')} | score={summary.get('baseline_score')}",
        f"- Current: {summary.get('current_id')} | score={summary.get('current_score')}",
        f"- Best: {summary.get('best_id')} | score={summary.get('best_score')}",
        "",
        "Score Deltas:",
        f"- Current vs Baseline: {deltas.get('current_vs_baseline', {}).get('score_delta')}",
        f"- Best vs Baseline: {deltas.get('best_vs_baseline', {}).get('score_delta')}",
        f"- Best vs Current: {deltas.get('best_vs_current', {}).get('score_delta')}",
        "",
        "Execution Locks:",
        "- Qt window creation: LOCKED",
        "- Plot rendering: LOCKED",
        "- UI widget creation: LOCKED",
        "",
        "Next phase: 15C Evolution Tree Backend.",
    ])


def _blocked_report(blockers):
    lines = [
        "PHASE 15B CANDIDATE COMPARISON VIEWER BACKEND",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
