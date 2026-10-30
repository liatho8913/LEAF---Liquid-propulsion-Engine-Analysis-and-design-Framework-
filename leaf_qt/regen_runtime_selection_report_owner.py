OWNER_NAME = "REGEN_RUNTIME_SELECTION_REPORT_OWNER"
PHASE = "14C"

PASS_STATUS = "PASS_REGEN_RUNTIME_SELECTION_REPORT_OWNER_PHASE_14C"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_SELECTION_REPORT_OWNER_PHASE_14C"


def attach_regen_runtime_selection_report_owner(results):
    if not isinstance(results, dict):
        return results

    ranked = results.get("regen_runtime_selection_ranked_candidates", [])
    parent_pool = results.get("regen_runtime_parent_pool", [])
    history = results.get("regen_runtime_selection_history")
    blockers = []

    if not isinstance(ranked, list) or not ranked:
        blockers.append("Ranked runtime candidates are missing.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Runtime parent pool is missing.")

    if not isinstance(history, dict):
        blockers.append("Runtime selection history is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(status, ranked, parent_pool)

    results.update({
        "regen_runtime_selection_report_owner_complete": True,
        "phase_14c_runtime_selection_report_owner_complete": True,
        "regen_runtime_selection_report_owner_ready": ready,
        "regen_runtime_selection_report_owner_status": status,
        "regen_runtime_selection_report_owner_blockers": blockers,
        "regen_runtime_selection_report": report,
    })

    return results


def _ready_report(status, ranked, parent_pool):
    lines = [
        "PHASE 14C RUNTIME SELECTION ENGINE",
        f"Status: {status}",
        "",
        "Ranked Runtime Candidates:",
    ]

    for item in ranked[:20]:
        lines.append(
            f"- Rank {item.get('runtime_selection_rank')}: "
            f"{item.get('runtime_candidate_id')} | "
            f"score={item.get('runtime_selection_score')} | "
            f"survives={item.get('runtime_candidate_survives')} | "
            f"parent_pool={item.get('runtime_selected_for_parent_pool')}"
        )

    lines.extend(["", "Runtime Parent Pool:"])

    for item in parent_pool:
        lines.append(
            f"- {item.get('runtime_candidate_id')} "
            f"(rank {item.get('runtime_selection_rank')}, score {item.get('runtime_selection_score')})"
        )

    lines.extend([
        "",
        "Execution Locks:",
        "- Generation advancement: LOCKED UNTIL 14D",
        "- Live geometry commit: LOCKED",
        "- Full runtime optimisation loop: LOCKED",
    ])

    return "\n".join(lines)


def _blocked_report(blockers):
    lines = [
        "PHASE 14C RUNTIME SELECTION ENGINE",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    return "\n".join(lines)
