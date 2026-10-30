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
from regen_viewer_ownership_architecture import attach_regen_viewer_ownership_architecture
from regen_cross_section_viewer_integration import attach_regen_cross_section_viewer_integration
from regen_station_viewer_integration import attach_regen_station_viewer_integration


def fake_solver(payload):
    out = dict(payload)
    out["corrected_thrust"] = 3500.0
    out["isp_vac"] = 315.0
    out["coolant_pressure_drop"] = 900.0
    out["regen_validation_status"] = "PASS_REGENERATED_SOLVER_PAYLOAD"
    out["regen_station_rows"] = [
        {
            "station_index": 0,
            "x": 0.0,
            "radius": 0.02,
            "mach": 1.0,
            "hot_gas_wall_temperature": 850.0,
            "coolant_wall_temperature": 420.0,
            "coolant_bulk_temperature": 300.0,
            "heat_flux": 5.0e6,
            "coolant_pressure": 5.0e6,
            "coolant_pressure_drop": 0.0,
            "coolant_reynolds": 2500.0,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
            "hot_gas_wall_thickness": 0.001,
        },
        {
            "station_index": 1,
            "x": 0.05,
            "radius": 0.03,
            "mach": 2.0,
            "hot_gas_wall_temperature": 780.0,
            "coolant_wall_temperature": 410.0,
            "coolant_bulk_temperature": 305.0,
            "heat_flux": 4.0e6,
            "coolant_pressure": 4.999e6,
            "coolant_pressure_drop": 1000.0,
            "coolant_reynolds": 2600.0,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
            "hot_gas_wall_thickness": 0.001,
        },
    ]
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
        attach_regen_viewer_ownership_architecture,
        attach_regen_cross_section_viewer_integration,
        attach_regen_station_viewer_integration,
    ):
        results = fn(results)

    assert results["phase_16k6_complete"] is True
    assert results["phase_16k6_status"] == "PASS_REGEN_STATION_VIEWER_INTEGRATION_PHASE_16K6"

    payload = results["regen_station_viewer_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["viewer_mode"] == "STATION_REGEN_INSPECTION"
    assert payload["visibility"] == "UI_REPORT_VIEW"
    assert payload["read_only"] is True
    assert payload["station_count"] >= 1
    assert "thermal" in payload["presets"]
    assert "coolant" in payload["presets"]
    assert "geometry" in payload["presets"]

    report = results["regen_station_viewer_integration_report"]
    assert "STATION VIEWER INTEGRATION" in report
    assert "Station count" in report

    assert results["phase_16k7_viewer_completion_gate_allowed"] is True

    print("PASS_REGEN_STATION_VIEWER_INTEGRATION_PHASE_16K6")


if __name__ == "__main__":
    main()
