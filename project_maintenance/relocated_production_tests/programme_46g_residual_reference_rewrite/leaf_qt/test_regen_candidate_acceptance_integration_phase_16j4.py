from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import (
    attach_regen_end_to_end_candidate_selection_validation,
)
from regen_candidate_acceptance_integration import (
    attach_regen_candidate_acceptance_integration,
)


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
            },
            {
                "candidate_id": "CANDIDATE_B",
                "candidate_geometry": {
                    "number_of_coolant_channels": 100,
                    "coolant_channel_width": 0.0012,
                    "coolant_channel_height": 0.0025,
                    "rib_width": 0.0008,
                    "hot_gas_wall_thickness": 0.0012,
                },
            },
        ],
    }

    results = attach_regen_ranking_owner_source_repair(results)
    results = attach_regen_recommendation_feed_repair(results)
    results = attach_regen_recommendation_viewer_repair(results)
    results = attach_regen_end_to_end_candidate_selection_validation(results)
    results = attach_regen_candidate_acceptance_integration(results)

    assert results["phase_16j4_complete"] is True
    assert (
        results["phase_16j4_status"]
        == "PASS_REGEN_CANDIDATE_ACCEPTANCE_INTEGRATION_PHASE_16J4"
    )

    payload = results["regen_candidate_acceptance_pending_application_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["commit_state"] == "NOT_COMMITTED"
    assert payload["application_mode"] == "PENDING_REVIEW"

    preview = results["regen_candidate_acceptance_before_after_preview"]
    assert preview["change_count"] >= 1

    history = results["regen_candidate_acceptance_history_event"]
    assert history["event_type"] == "REGEN_CANDIDATE_ACCEPTED_PENDING_APPLICATION"
    assert history["commit_state"] == "NOT_COMMITTED"

    assert results["regen_candidate_accepted_for_pending_application"] is True
    assert results["regen_candidate_geometry_application_allowed"] is True
    assert results["regen_candidate_manual_overwrite_allowed"] is False
    assert results["regen_candidate_live_geometry_commit_executed"] is False
    assert results["phase_16j4b_pending_geometry_commit_validation_allowed"] is True

    report = results["regen_candidate_acceptance_report"]
    assert "Pending Geometry Commit Validation" in report
    assert "Live geometry commit: NOT EXECUTED" in report

    print("PASS_REGEN_CANDIDATE_ACCEPTANCE_INTEGRATION_PHASE_16J4")


if __name__ == "__main__":
    main()
