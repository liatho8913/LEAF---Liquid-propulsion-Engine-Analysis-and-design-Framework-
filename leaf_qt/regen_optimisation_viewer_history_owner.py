OWNER_NAME = "REGEN_OPTIMISATION_VIEWER_HISTORY_OWNER"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_VIEWER_HISTORY_OWNER_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_VIEWER_HISTORY_OWNER_PHASE_15A"


def attach_regen_optimisation_viewer_history_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_improvement_viewer_data_owner_ready") is not True:
        blockers.append("Improvement viewer data owner is not ready.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    history = None

    if ready:
        history = {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "history_state": "OPTIMISATION_VIEWER_BACKEND_DATA_ASSEMBLED",
            "entries": [
                {
                    "entry_id": "OPTIMISATION_VIEWER_HISTORY_15A_GENERATIONS",
                    "event": "GENERATION_VIEWER_DATA_CREATED",
                    "count": results.get("optimisation_viewer_generation_count"),
                },
                {
                    "entry_id": "OPTIMISATION_VIEWER_HISTORY_15A_CANDIDATES",
                    "event": "CANDIDATE_VIEWER_DATA_CREATED",
                    "count": results.get("optimisation_viewer_candidate_count"),
                },
                {
                    "entry_id": "OPTIMISATION_VIEWER_HISTORY_15A_IMPROVEMENTS",
                    "event": "IMPROVEMENT_VIEWER_DATA_CREATED",
                    "count": results.get("optimisation_viewer_improvement_count"),
                },
            ],
            "qt_window_count": 0,
            "plot_render_count": 0,
        }

    results.update({
        "regen_optimisation_viewer_history_owner_complete": True,
        "phase_15a_optimisation_viewer_history_owner_complete": True,
        "regen_optimisation_viewer_history_owner_ready": ready,
        "regen_optimisation_viewer_history_owner_status": status,
        "regen_optimisation_viewer_history_owner_blockers": blockers,

        "optimisation_viewer_history": history if ready else {},
    })

    return results
