from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit
from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner


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

    results = attach_regen_ranking_owner_source_repair(results)
    results = attach_regen_recommendation_feed_repair(results)
    results = attach_regen_recommendation_viewer_repair(results)
    results = attach_regen_end_to_end_candidate_selection_validation(results)
    results = attach_regen_candidate_acceptance_integration(results)
    results = attach_regen_pending_geometry_commit_validation(results)
    results = attach_regen_live_geometry_commit_execution(results)
    results = attach_regen_solver_regeneration_after_commit(results)
    results = attach_regen_before_after_solver_comparison_report_owner(results)

    assert results["phase_16j4e_complete"] is True
    assert results["phase_16j4e_status"] == "PASS_REGEN_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_PHASE_16J4E"

    payload = results["regen_before_after_solver_comparison_report_payload"]
    assert payload["visibility"] == "REPORT_ONLY"
    assert payload["candidate_id"] == "CANDIDATE_A"

    summary = results["regen_before_after_solver_comparison_summary"]
    assert summary["changed"] >= 3
    assert summary["improved"] >= 3

    changes = results["regen_before_after_solver_comparison_classified_changes"]
    assert any(c["key"] == "corrected_thrust" and c["classification"] == "IMPROVED" for c in changes)
    assert any(c["key"] == "coolant_pressure_drop" and c["classification"] == "IMPROVED" for c in changes)

    report = results["regen_before_after_solver_comparison_report"]
    assert "BEFORE/AFTER SOLVER COMPARISON REPORT OWNERSHIP" in report
    assert "REPORT_ONLY" in report

    assert results["phase_16j4f_design_iteration_history_link_allowed"] is True

    print("PASS_REGEN_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_PHASE_16J4E")


if __name__ == "__main__":
    main()
