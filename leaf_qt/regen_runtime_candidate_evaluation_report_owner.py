OWNER_NAME = "REGEN_RUNTIME_CANDIDATE_EVALUATION_REPORT_OWNER"
PHASE = "14B"

PASS_STATUS = "PASS_REGEN_RUNTIME_CANDIDATE_EVALUATION_REPORT_OWNER_PHASE_14B"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_CANDIDATE_EVALUATION_REPORT_OWNER_PHASE_14B"


def attach_regen_runtime_candidate_evaluation_report_owner(results):
    if not isinstance(results, dict):
        return results

    evaluations = results.get("regen_runtime_candidate_evaluation_records", [])
    history = results.get("regen_runtime_candidate_evaluation_history")
    blockers = []

    if not isinstance(evaluations, list) or not evaluations:
        blockers.append("Runtime candidate evaluations are missing.")

    if not isinstance(history, dict):
        blockers.append("Runtime candidate evaluation history is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, evaluations)

    results.update({
        "regen_runtime_candidate_evaluation_report_owner_complete": True,
        "phase_14b_runtime_candidate_evaluation_report_owner_complete": True,
        "regen_runtime_candidate_evaluation_report_owner_ready": ready,
        "regen_runtime_candidate_evaluation_report_owner_status": status,
        "regen_runtime_candidate_evaluation_report_owner_blockers": blockers,
        "regen_runtime_candidate_evaluation_report": report,
    })

    return results


def _ready_report(status, evaluations):
    lines = [
        "PHASE 14B RUNTIME CANDIDATE EVALUATION ENGINE",
        f"Status: {status}",
        "",
        "Evaluation Results:",
    ]

    for item in evaluations[:20]:
        lines.append(
            f"- {item.get('runtime_candidate_id')} | "
            f"score={item.get('candidate_score')} | "
            f"solver_executed={item.get('solver_executed')} | "
            f"accepted=False"
        )

    lines.extend([
        "",
        "Execution Locks:",
        "- Candidate acceptance: LOCKED",
        "- Generation advancement: LOCKED",
        "- Live geometry commit: LOCKED",
        "",
        "14C runtime selection may begin after the 14B master gate passes.",
    ])

    return "\n".join(lines)


def _blocked_report(blockers):
    lines = [
        "PHASE 14B RUNTIME CANDIDATE EVALUATION ENGINE",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
