from regen_candidate_comparison_registry import attach_regen_candidate_comparison_registry
from regen_candidate_comparison_baseline_owner import attach_regen_candidate_comparison_baseline_owner
from regen_candidate_comparison_current_owner import attach_regen_candidate_comparison_current_owner
from regen_candidate_comparison_best_owner import attach_regen_candidate_comparison_best_owner
from regen_candidate_comparison_metrics_owner import attach_regen_candidate_comparison_metrics_owner
from regen_candidate_comparison_history_owner import attach_regen_candidate_comparison_history_owner
from regen_candidate_comparison_report_owner import attach_regen_candidate_comparison_report_owner
from regen_candidate_comparison_completion_audit import attach_regen_candidate_comparison_completion_audit
from regen_candidate_comparison_master_gate import attach_regen_candidate_comparison_master_gate


def main():
    results = {
        "phase_15a_complete": True,
        "phase_15a_status": "PASS_REGEN_OPTIMISATION_VIEWER_BACKEND_PHASE_15A",
        "phase_15b_candidate_comparison_viewer_backend_allowed": True,

        "optimisation_viewer_candidates": [
            {
                "runtime_candidate_id": "BASELINE_A",
                "score": 100.0,
                "rank": 3,
                "source_key": "regen_runtime_candidate_records",
            },
            {
                "runtime_candidate_id": "CURRENT_B",
                "score": 120.0,
                "rank": 2,
                "source_key": "regen_runtime_candidate_evaluation_records",
            },
            {
                "runtime_candidate_id": "BEST_C",
                "score": 135.0,
                "rank": 1,
                "source_key": "regen_runtime_selection_ranked_candidates",
            },
        ],

        "candidate_comparison_qt_window_created": False,
        "candidate_comparison_plot_rendered": False,
        "candidate_comparison_ui_widget_created": False,
    }

    for attach in (
        attach_regen_candidate_comparison_registry,
        attach_regen_candidate_comparison_baseline_owner,
        attach_regen_candidate_comparison_current_owner,
        attach_regen_candidate_comparison_best_owner,
        attach_regen_candidate_comparison_metrics_owner,
        attach_regen_candidate_comparison_history_owner,
        attach_regen_candidate_comparison_report_owner,
        attach_regen_candidate_comparison_completion_audit,
        attach_regen_candidate_comparison_master_gate,
    ):
        results = attach(results)

    assert results["regen_candidate_comparison_registry_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_REGISTRY_PHASE_15B"
    )
    assert results["regen_candidate_comparison_baseline_owner_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_BASELINE_OWNER_PHASE_15B"
    )
    assert results["regen_candidate_comparison_current_owner_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_CURRENT_OWNER_PHASE_15B"
    )
    assert results["regen_candidate_comparison_best_owner_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_BEST_OWNER_PHASE_15B"
    )
    assert results["regen_candidate_comparison_metrics_owner_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_METRICS_OWNER_PHASE_15B"
    )
    assert results["regen_candidate_comparison_history_owner_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_HISTORY_OWNER_PHASE_15B"
    )
    assert results["regen_candidate_comparison_report_owner_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_REPORT_OWNER_PHASE_15B"
    )
    assert results["regen_candidate_comparison_completion_audit_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B"
    )
    assert results["regen_candidate_comparison_master_gate_status"] == (
        "PASS_REGEN_CANDIDATE_COMPARISON_MASTER_GATE_PHASE_15B"
    )

    assert results["phase_15b_status"] == "PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B"
    assert results["phase_15c_evolution_tree_backend_allowed"] is True

    assert results["candidate_comparison_baseline"]["runtime_candidate_id"] == "BASELINE_A"
    assert results["candidate_comparison_best"]["runtime_candidate_id"] == "BEST_C"
    assert results["candidate_comparison_deltas"]["best_vs_baseline"]["score_delta"] == 35.0

    print("PASS_REGEN_CANDIDATE_COMPARISON_VIEWER_BACKEND_PHASE_15B")


if __name__ == "__main__":
    main()
