from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution


def main():
    results = {
        "number_of_coolant_channels": 60,
        "coolant_channel_width": 0.0010,
        "coolant_channel_height": 0.0015,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0008,
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

    assert results["phase_16j4c_complete"] is True
    assert results["phase_16j4c_status"] == "PASS_REGEN_LIVE_GEOMETRY_COMMIT_EXECUTION_PHASE_16J4C"

    assert results["number_of_coolant_channels"] == 80
    assert results["coolant_channel_width"] == 0.0015
    assert results["coolant_channel_height"] == 0.0020
    assert results["hot_gas_wall_thickness"] == 0.0010

    audit = results["regen_live_geometry_commit_audit_record"]
    assert audit["event_type"] == "REGEN_LIVE_GEOMETRY_COMMIT_EXECUTED"
    assert audit["candidate_id"] == "CANDIDATE_A"
    assert "coolant_channel_width" in audit["committed_keys"]

    assert results["regen_candidate_live_geometry_commit_executed"] is True
    assert results["regen_candidate_manual_overwrite_allowed"] is False
    assert results["phase_16j4d_solver_regeneration_after_commit_allowed"] is True

    report = results["regen_live_geometry_commit_report"]
    assert "LIVE GEOMETRY COMMIT EXECUTION" in report
    assert "Live geometry commit: EXECUTED" in report

    print("PASS_REGEN_LIVE_GEOMETRY_COMMIT_EXECUTION_PHASE_16J4C")


if __name__ == "__main__":
    main()
