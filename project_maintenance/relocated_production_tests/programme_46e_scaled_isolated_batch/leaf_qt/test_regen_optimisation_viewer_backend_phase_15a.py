from regen_optimisation_viewer_registry import attach_regen_optimisation_viewer_registry
from regen_optimisation_viewer_data_owner import attach_regen_optimisation_viewer_data_owner
from regen_generation_viewer_data_owner import attach_regen_generation_viewer_data_owner
from regen_candidate_viewer_data_owner import attach_regen_candidate_viewer_data_owner
from regen_improvement_viewer_data_owner import attach_regen_improvement_viewer_data_owner
from regen_optimisation_viewer_history_owner import attach_regen_optimisation_viewer_history_owner
from regen_optimisation_viewer_report_owner import attach_regen_optimisation_viewer_report_owner
from regen_optimisation_viewer_completion_audit import attach_regen_optimisation_viewer_completion_audit
from regen_optimisation_viewer_master_gate import attach_regen_optimisation_viewer_master_gate


def main():
    results = {
        "phase_14_runtime_backend_complete": True,
        "phase_14f_status": "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_PHASE_14F",
        "phase_15a_optimisation_viewer_backend_allowed": True,

        "regen_runtime_optimisation_complete": True,
        "runtime_optimisation_continue_required": False,
        "runtime_optimisation_completion_reason": "OPTIMISATION_COMPLETE_CONVERGENCE_DETECTED",
        "runtime_optimisation_final_generation": 4,
        "runtime_optimisation_final_best_score": 130.0,

        "runtime_generation_history": [
            {"entry_id": "GEN_0_TO_1", "event": "GENERATION_ADVANCED"},
        ],
        "runtime_generation_population": [
            {"runtime_generation_candidate_id": "GEN_1_CANDIDATE_0000"},
        ],

        "regen_runtime_selection_ranked_candidates": [
            {
                "runtime_candidate_id": "RUNTIME_A",
                "runtime_selection_score": 130.0,
                "runtime_selection_rank": 1,
                "runtime_candidate_survives": True,
                "runtime_selected_for_parent_pool": True,
            }
        ],

        "runtime_previous_best_score": 120.0,
        "runtime_current_best_score": 130.0,
        "runtime_generation_improvement": 10.0,
        "runtime_improvement_detected": True,
        "runtime_previous_stagnation_count": 0,
        "runtime_stagnation_count": 0,
        "runtime_stagnation_limit": 3,
        "runtime_stagnation_limit_reached": False,
    }

    for attach in (
        attach_regen_optimisation_viewer_registry,
        attach_regen_optimisation_viewer_data_owner,
        attach_regen_generation_viewer_data_owner,
        attach_regen_candidate_viewer_data_owner,
        attach_regen_improvement_viewer_data_owner,
        attach_regen_optimisation_viewer_history_owner,
        attach_regen_optimisation_viewer_report_owner,
        attach_regen_optimisation_viewer_completion_audit,
        attach_regen_optimisation_viewer_master_gate,
    ):
        results = attach(results)

    assert results["regen_optimisation_viewer_registry_status"] == (
        "PASS_REGEN_OPTIMISATION_VIEWER_REGISTRY_PHASE_15A"
    )
    assert results["regen_optimisation_viewer_data_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_VIEWER_DATA_OWNER_PHASE_15A"
    )
    assert results["regen_generation_viewer_data_owner_status"] == (
        "PASS_REGEN_GENERATION_VIEWER_DATA_OWNER_PHASE_15A"
    )
    assert results["regen_candidate_viewer_data_owner_status"] == (
        "PASS_REGEN_CANDIDATE_VIEWER_DATA_OWNER_PHASE_15A"
    )
    assert results["regen_improvement_viewer_data_owner_status"] == (
        "PASS_REGEN_IMPROVEMENT_VIEWER_DATA_OWNER_PHASE_15A"
    )
    assert results["regen_optimisation_viewer_history_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_VIEWER_HISTORY_OWNER_PHASE_15A"
    )
    assert results["regen_optimisation_viewer_report_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_VIEWER_REPORT_OWNER_PHASE_15A"
    )
    assert results["regen_optimisation_viewer_completion_audit_status"] == (
        "PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A"
    )
    assert results["regen_optimisation_viewer_master_gate_status"] == (
        "PASS_REGEN_OPTIMISATION_VIEWER_MASTER_GATE_PHASE_15A"
    )

    assert results["phase_15a_status"] == "PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A"
    assert results["phase_15b_candidate_comparison_viewer_backend_allowed"] is True

    assert results["optimisation_viewer_generation_count"] == 1
    assert results["optimisation_viewer_candidate_count"] == 1
    assert results["optimisation_viewer_improvement_count"] == 3

    assert results["optimisation_viewer_qt_window_created"] is False
    assert results["optimisation_viewer_plot_rendered"] is False
    assert results["optimisation_viewer_ui_widget_created"] is False

    print("PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A")


if __name__ == "__main__":
    main()
