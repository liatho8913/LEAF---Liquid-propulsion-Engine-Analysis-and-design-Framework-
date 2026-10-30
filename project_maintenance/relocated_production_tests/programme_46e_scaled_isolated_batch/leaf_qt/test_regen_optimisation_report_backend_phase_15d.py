from regen_optimisation_report_backend_registry import attach_regen_optimisation_report_backend_registry
from regen_optimisation_report_backend_data_owner import attach_regen_optimisation_report_backend_data_owner
from regen_optimisation_report_section_owner import attach_regen_optimisation_report_section_owner
from regen_optimisation_report_metrics_owner import attach_regen_optimisation_report_metrics_owner
from regen_optimisation_report_history_owner import attach_regen_optimisation_report_history_owner
from regen_optimisation_report_backend_report_owner import attach_regen_optimisation_report_backend_report_owner
from regen_optimisation_report_backend_completion_audit import attach_regen_optimisation_report_backend_completion_audit
from regen_optimisation_report_backend_master_gate import attach_regen_optimisation_report_backend_master_gate


def main():
    results = {
        "phase_15c_complete": True,
        "phase_15c_status": "PASS_REGEN_EVOLUTION_TREE_BACKEND_PHASE_15C",
        "phase_15d_optimisation_report_backend_allowed": True,

        "phase_14_runtime_backend_complete": True,
        "regen_runtime_optimisation_complete": True,
        "runtime_optimisation_continue_required": False,
        "runtime_optimisation_completion_reason": "OPTIMISATION_COMPLETE_CONVERGENCE_DETECTED",
        "runtime_optimisation_final_generation": 4,
        "runtime_optimisation_final_best_score": 135.0,

        "optimisation_viewer_generation_count": 2,
        "optimisation_viewer_candidate_count": 3,
        "optimisation_viewer_improvement_count": 3,

        "candidate_comparison_summary": {
            "baseline_id": "BASELINE_A",
            "current_id": "CURRENT_B",
            "best_id": "BEST_C",
            "baseline_score": 100.0,
            "current_score": 120.0,
            "best_score": 135.0,
        },

        "evolution_tree_summary": {
            "generation_count": 2,
            "parent_link_count": 1,
            "mutation_link_count": 1,
            "path_count": 1,
            "best_candidate_id": "BEST_C",
        },

        "optimisation_viewer_backend_report": "viewer report",
        "candidate_comparison_backend_report": "comparison report",
        "evolution_tree_report": "tree report",

        "optimisation_report_qt_window_created": False,
        "optimisation_report_pdf_exported": False,
        "optimisation_report_html_exported": False,
    }

    for attach in (
        attach_regen_optimisation_report_backend_registry,
        attach_regen_optimisation_report_backend_data_owner,
        attach_regen_optimisation_report_section_owner,
        attach_regen_optimisation_report_metrics_owner,
        attach_regen_optimisation_report_history_owner,
        attach_regen_optimisation_report_backend_report_owner,
        attach_regen_optimisation_report_backend_completion_audit,
        attach_regen_optimisation_report_backend_master_gate,
    ):
        results = attach(results)

    assert results["regen_optimisation_report_backend_registry_status"] == (
        "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_REGISTRY_PHASE_15D"
    )
    assert results["regen_optimisation_report_backend_data_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_DATA_OWNER_PHASE_15D"
    )
    assert results["regen_optimisation_report_section_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_REPORT_SECTION_OWNER_PHASE_15D"
    )
    assert results["regen_optimisation_report_metrics_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_REPORT_METRICS_OWNER_PHASE_15D"
    )
    assert results["regen_optimisation_report_history_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_REPORT_HISTORY_OWNER_PHASE_15D"
    )
    assert results["regen_optimisation_report_backend_report_owner_status"] == (
        "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_REPORT_OWNER_PHASE_15D"
    )
    assert results["regen_optimisation_report_backend_completion_audit_status"] == (
        "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D"
    )
    assert results["regen_optimisation_report_backend_master_gate_status"] == (
        "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_MASTER_GATE_PHASE_15D"
    )

    assert results["phase_15d_status"] == "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D"
    assert results["phase_16_unified_regen_ecosystem_allowed"] is True
    assert results["optimisation_report_section_count"] == 5
    assert results["optimisation_report_backend_summary"]["ready_for_phase_16"] is True

    print("PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D")


if __name__ == "__main__":
    main()
