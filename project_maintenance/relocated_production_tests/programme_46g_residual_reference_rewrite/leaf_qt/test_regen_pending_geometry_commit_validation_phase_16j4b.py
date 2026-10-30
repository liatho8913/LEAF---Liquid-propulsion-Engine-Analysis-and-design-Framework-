from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation


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

    assert results["phase_16j4b_complete"] is True
    assert results["phase_16j4b_status"] == "PASS_REGEN_PENDING_GEOMETRY_COMMIT_VALIDATION_PHASE_16J4B"

    approval = results["regen_pending_geometry_commit_approval_payload"]
    assert approval["candidate_id"] == "CANDIDATE_A"
    assert approval["commit_readiness"] == "READY_FOR_EXPLICIT_COMMIT"
    assert approval["live_commit_executed"] is False

    assert results["phase_16j4c_live_geometry_commit_allowed"] is True
    assert results["regen_candidate_manual_overwrite_allowed"] is False
    assert results["regen_candidate_live_geometry_commit_executed"] is False

    report = results["regen_pending_geometry_commit_validation_report"]
    assert "PENDING GEOMETRY COMMIT VALIDATION" in report
    assert "Live geometry commit: NOT EXECUTED" in report

    print("PASS_REGEN_PENDING_GEOMETRY_COMMIT_VALIDATION_PHASE_16J4B")


if __name__ == "__main__":
    main()
