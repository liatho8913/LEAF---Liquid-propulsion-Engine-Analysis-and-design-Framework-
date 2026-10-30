from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit
from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner
from regen_design_iteration_history_link import attach_regen_design_iteration_history_link
from regen_candidate_acceptance_completion_gate import attach_regen_candidate_acceptance_completion_gate
from regen_recommendation_explanation_engine import attach_regen_recommendation_explanation_engine
from regen_failure_root_cause_system import attach_regen_failure_root_cause_system
from regen_optimisation_proof_system import attach_regen_optimisation_proof_system
from regen_optimisation_completion_gate import attach_regen_optimisation_completion_gate
from regen_viewer_data_adapter import attach_regen_viewer_data_adapter
from regen_viewer_report_renderer import attach_regen_viewer_report_renderer
from regen_viewer_navigation_system import attach_regen_viewer_navigation_system


def fake_solver(payload):
    out = dict(payload)
    out["corrected_thrust"] = 3500.0
    out["isp_vac"] = 315.0
    out["coolant_pressure_drop"] = 900.0
    out["regen_validation_status"] = "PASS_REGENERATED_SOLVER_PAYLOAD"
    return out


def main():
    results = {
        "number_of_coolant_channels": 60,
        "coolant_channel_width": 0.0010,
        "coolant_channel_height": 0.0015,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0008,
        "corrected_thrust": 3300.0,
        "isp_vac": 300.0,
        "coolant_pressure_drop": 1200.0,
        "regen_solver_regeneration_callable": fake_solver,
        "regen_candidate_ranking_input_population": [
            {
                "candidate_id": "CANDIDATE_A",
                "candidate_geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                    "coolant_channel_height": 0.0020,
                    "rib_width": 0.0010,
                    "hot_gas_wall_thickness": 0.0010,
                },
            }
        ],
    }

    for fn in (
        attach_regen_ranking_owner_source_repair,
        attach_regen_recommendation_feed_repair,
        attach_regen_recommendation_viewer_repair,
        attach_regen_end_to_end_candidate_selection_validation,
        attach_regen_candidate_acceptance_integration,
        attach_regen_pending_geometry_commit_validation,
        attach_regen_live_geometry_commit_execution,
        attach_regen_solver_regeneration_after_commit,
        attach_regen_before_after_solver_comparison_report_owner,
        attach_regen_design_iteration_history_link,
        attach_regen_candidate_acceptance_completion_gate,
        attach_regen_recommendation_explanation_engine,
        attach_regen_failure_root_cause_system,
        attach_regen_optimisation_proof_system,
        attach_regen_optimisation_completion_gate,
        attach_regen_viewer_data_adapter,
        attach_regen_viewer_report_renderer,
        attach_regen_viewer_navigation_system,
    ):
        results = fn(results)

    assert results["phase_16k3_complete"] is True
    assert results["phase_16k3_status"] == "PASS_REGEN_VIEWER_NAVIGATION_SYSTEM_PHASE_16K3"

    payload = results["regen_viewer_navigation_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["section_count"] == 7
    assert payload["default_section_key"] == "summary"
    assert payload["read_only"] is True

    selected = results["regen_viewer_selected_section"]
    assert selected["key"] == "summary"
    assert "Optimisation Summary" in selected["content"]

    assert results["phase_16k4_viewer_ownership_architecture_allowed"] is True

    print("PASS_REGEN_VIEWER_NAVIGATION_SYSTEM_PHASE_16K3")


if __name__ == "__main__":
    main()
