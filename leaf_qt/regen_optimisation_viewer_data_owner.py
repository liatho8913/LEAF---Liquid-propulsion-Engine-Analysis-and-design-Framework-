OWNER_NAME = "REGEN_OPTIMISATION_VIEWER_DATA_OWNER"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_VIEWER_DATA_OWNER_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_VIEWER_DATA_OWNER_PHASE_15A"


def attach_regen_optimisation_viewer_data_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_optimisation_viewer_registry_ready") is not True:
        blockers.append("Optimisation viewer registry is not ready.")

    payload = {
        "runtime_backend_complete": results.get("phase_14_runtime_backend_complete"),
        "runtime_optimisation_complete": results.get("regen_runtime_optimisation_complete"),
        "continue_required": results.get("runtime_optimisation_continue_required"),
        "completion_reason": results.get("runtime_optimisation_completion_reason"),
        "final_generation": results.get("runtime_optimisation_final_generation"),
        "final_best_score": results.get("runtime_optimisation_final_best_score"),
        "viewer_mode": "BACKEND_ONLY_NO_QT_WIDGETS",
    }

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_viewer_data_owner_complete": True,
        "phase_15a_optimisation_viewer_data_owner_complete": True,
        "regen_optimisation_viewer_data_owner_ready": ready,
        "regen_optimisation_viewer_data_owner_status": status,
        "regen_optimisation_viewer_data_owner_blockers": blockers,

        "optimisation_viewer_backend_payload": payload if ready else {},
        "optimisation_viewer_best_score": payload["final_best_score"] if ready else None,
        "optimisation_viewer_current_generation": payload["final_generation"] if ready else None,
        "optimisation_viewer_runtime_complete": payload["runtime_optimisation_complete"] if ready else False,

        "optimisation_viewer_qt_window_created": False,
        "optimisation_viewer_plot_rendered": False,
        "optimisation_viewer_ui_widget_created": False,
    })

    return results
