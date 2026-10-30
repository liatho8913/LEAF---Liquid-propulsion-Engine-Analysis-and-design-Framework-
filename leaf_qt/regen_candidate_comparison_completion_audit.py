OWNER_NAME = "REGEN_CANDIDATE_COMPARISON_COMPLETION_AUDIT"
PHASE = "15B"

PASS_STATUS = "PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B"


def attach_regen_candidate_comparison_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_candidate_comparison_registry_ready": "Comparison registry is not ready.",
        "regen_candidate_comparison_baseline_owner_ready": "Baseline owner is not ready.",
        "regen_candidate_comparison_current_owner_ready": "Current owner is not ready.",
        "regen_candidate_comparison_best_owner_ready": "Best owner is not ready.",
        "regen_candidate_comparison_metrics_owner_ready": "Metrics owner is not ready.",
        "regen_candidate_comparison_history_owner_ready": "History owner is not ready.",
        "regen_candidate_comparison_report_owner_ready": "Report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("candidate_comparison_qt_window_created") is not False:
        blockers.append("Qt window was illegally created in 15B.")

    if results.get("candidate_comparison_plot_rendered") is not False:
        blockers.append("Plot was illegally rendered in 15B.")

    if results.get("candidate_comparison_ui_widget_created") is not False:
        blockers.append("UI widget was illegally created in 15B.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_candidate_comparison_completion_audit_complete": True,
        "phase_15b_candidate_comparison_completion_audit_complete": True,
        "regen_candidate_comparison_completion_audit_ready": ready,
        "regen_candidate_comparison_completion_audit_status": status,
        "regen_candidate_comparison_completion_audit_blockers": blockers,

        "phase_15b_complete": ready,
        "phase_15b_status": status,
        "phase_15c_evolution_tree_backend_allowed": ready,
    })

    return results
