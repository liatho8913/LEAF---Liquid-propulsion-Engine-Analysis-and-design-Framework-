OWNER_NAME = "REGEN_OPTIMISATION_VIEWER_COMPLETION_AUDIT"
PHASE = "15A"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A"


def attach_regen_optimisation_viewer_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_optimisation_viewer_registry_ready": "Viewer registry is not ready.",
        "regen_optimisation_viewer_data_owner_ready": "Viewer data owner is not ready.",
        "regen_generation_viewer_data_owner_ready": "Generation viewer data owner is not ready.",
        "regen_candidate_viewer_data_owner_ready": "Candidate viewer data owner is not ready.",
        "regen_improvement_viewer_data_owner_ready": "Improvement viewer data owner is not ready.",
        "regen_optimisation_viewer_history_owner_ready": "Viewer history owner is not ready.",
        "regen_optimisation_viewer_report_owner_ready": "Viewer report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("optimisation_viewer_qt_window_created") is not False:
        blockers.append("Qt window was illegally created in 15A.")

    if results.get("optimisation_viewer_plot_rendered") is not False:
        blockers.append("Plot was illegally rendered in 15A.")

    if results.get("optimisation_viewer_ui_widget_created") is not False:
        blockers.append("UI widget was illegally created in 15A.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_viewer_completion_audit_complete": True,
        "phase_15a_optimisation_viewer_completion_audit_complete": True,
        "regen_optimisation_viewer_completion_audit_ready": ready,
        "regen_optimisation_viewer_completion_audit_status": status,
        "regen_optimisation_viewer_completion_audit_blockers": blockers,

        "phase_15a_complete": ready,
        "phase_15a_status": status,

        "phase_15b_candidate_comparison_viewer_backend_allowed": ready,
    })

    return results
