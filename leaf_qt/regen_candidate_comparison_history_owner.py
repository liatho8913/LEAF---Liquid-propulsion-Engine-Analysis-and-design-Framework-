OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_HISTORY_OWNER"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_HISTORY_OWNER_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_HISTORY_OWNER_PHASE_15B"


def attach_regen_candidate_comparison_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_candidate_comparison_metrics_owner_ready") is not True:
        blockers.append("Candidate comparison metrics owner is not ready.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None
    if ready:
        summary = results.get("candidate_comparison_summary", {})
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "CANDIDATE_COMPARISON_BACKEND_ASSEMBLED",
            "entries": [
                {
                    "entry_id": "CANDIDATE_COMPARISON_HISTORY_15B_BASELINE_CURRENT_BEST",
                    "event": "COMPARISON_TARGETS_SELECTED",
                    "baseline_id": summary.get("baseline_id"),
                    "current_id": summary.get("current_id"),
                    "best_id": summary.get("best_id"),
                },
                {
                    "entry_id": "CANDIDATE_COMPARISON_HISTORY_15B_METRICS",
                    "event": "COMPARISON_DELTAS_COMPUTED",
                    "deltas": results.get("candidate_comparison_deltas"),
                    "improvements": results.get("candidate_comparison_improvements"),
                },
            ],
            "qt_window_count": 0,
            "plot_render_count": 0,
            "ui_widget_count": 0,
        }

    results.update({
        "regen_candidate_comparison_history_owner_complete": True,
        "phase_15b_candidate_comparison_history_owner_complete": True,
        "regen_candidate_comparison_history_owner_ready": ready,
        "regen_candidate_comparison_history_owner_status": status,
        "regen_candidate_comparison_history_owner_blockers": blockers,
        "candidate_comparison_history": history if ready else {},
    })

    return results
