from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit


def fake_solver(payload):
    out = dict(payload)
    out["corrected_thrust"] = 3500.0
    out["isp_vac"] = 315.0
    out["regen_geometry_valid"] = True
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

    assert results["phase_16j4d_complete"] is True
    assert results["phase_16j4d_status"] == "PASS_REGEN_SOLVER_REGENERATION_AFTER_COMMIT_PHASE_16J4D"

    payload = results["regen_solver_regeneration_result_payload"]
    assert payload["corrected_thrust"] == 3500.0
    assert payload["isp_vac"] == 315.0
    assert payload["regen_validation_status"] == "PASS_REGENERATED_SOLVER_PAYLOAD"

    comparison = results["regen_solver_regeneration_before_after_comparison"]
    assert comparison["change_count"] >= 2

    assert results["regen_solver_regenerated_after_commit"] is True
    assert results["phase_16j4e_before_after_solver_comparison_allowed"] is True

    report = results["regen_solver_regeneration_report"]
    assert "SOLVER REGENERATION AFTER COMMIT" in report
    assert "Refuses to fake regenerated solver outputs" in report

    print("PASS_REGEN_SOLVER_REGENERATION_AFTER_COMMIT_PHASE_16J4D")


if __name__ == "__main__":
    main()
