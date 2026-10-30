OWNER_NAME = "REGEN_OPTIMISATION_SELECTION_REPORT_OWNER"
PHASE = "13K"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_SELECTION_REPORT_OWNER_PHASE_13K"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_SELECTION_REPORT_OWNER_PHASE_13K"


def attach_regen_optimisation_selection_report_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_optimisation_selection_report_owner(results)
    results.update(payload)
    return results


def build_regen_optimisation_selection_report_owner(results):
    blockers = []

    ranked = results.get("regen_optimisation_selection_ranked_candidates", [])
    parent_pool = results.get("regen_optimisation_parent_pool", [])
    state = results.get("regen_optimisation_selection_state")

    if not isinstance(ranked, list) or not ranked:
        blockers.append("Ranked candidates are missing.")

    if not isinstance(parent_pool, list) or not parent_pool:
        blockers.append("Parent pool is missing.")

    if not isinstance(state, dict):
        blockers.append("Selection state is missing.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    report = _blocked_report(blockers) if not ready else _ready_report(
        status=status,
        ranked=ranked,
        parent_pool=parent_pool,
        state=state,
    )

    return {
        "regen_optimisation_selection_report_owner_complete": True,
        "phase_13k_selection_report_owner_complete": True,
        "regen_optimisation_selection_report_owner_ready": ready,
        "regen_optimisation_selection_report_owner_status": status,
        "regen_optimisation_selection_report_owner_blockers": blockers,
        "regen_optimisation_selection_report": report,
    }


def _ready_report(status, ranked, parent_pool, state):
    lines = [
        "PHASE 13K OPTIMISATION SELECTION FRAMEWORK",
        f"Status: {status}",
        "",
        "Selection State:",
        f"- {state.get('selection_state')}",
        f"- Best Candidate: {state.get('best_candidate_id')}",
        "",
        "Top Ranked Candidates:",
    ]

    for item in ranked[:10]:
        lines.append(
            f"- Rank {item.get('selection_rank')}: "
            f"{item.get('candidate_id')} | "
            f"Score={item.get('selection_score')} | "
            f"Survives={item.get('survives_generation')} | "
            f"ParentPool={item.get('selected_for_parent_pool')}"
        )

    lines.extend([
        "",
        "Parent Pool:",
    ])

    for item in parent_pool:
        lines.append(
            f"- {item.get('candidate_id')} "
            f"(rank {item.get('selection_rank')}, score {item.get('selection_score')})"
        )

    lines.extend([
        "",
        "Execution Locks:",
        "- Solver execution: LOCKED",
        "- Geometry mutation: LOCKED",
        "- Candidate acceptance: LOCKED",
        "- Live geometry commit: LOCKED",
        "- Generation advance: LOCKED",
        "",
        "13L optimisation foundation may begin only after the 13K master gate passes.",
    ])

    return "\n".join(lines)


def _blocked_report(blockers):
    lines = [
        "PHASE 13K OPTIMISATION SELECTION FRAMEWORK",
        "Status: BLOCKED",
        "",
        "Blockers:",
    ]

    for blocker in blockers:
        lines.append(f"- {blocker}")

    return "\n".join(lines)
