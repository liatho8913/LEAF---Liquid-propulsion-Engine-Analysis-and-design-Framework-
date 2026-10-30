from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import (
    attach_regen_end_to_end_candidate_selection_validation,
)


def main():
    results = {
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
        ]
    }

    results = attach_regen_ranking_owner_source_repair(results)
    results = attach_regen_recommendation_feed_repair(results)
    results = attach_regen_recommendation_viewer_repair(results)
    results = attach_regen_end_to_end_candidate_selection_validation(results)

    assert results["phase_16j3h_complete"] is True
    assert (
        results["phase_16j3h_status"]
        == "PASS_REGEN_END_TO_END_CANDIDATE_SELECTION_VALIDATION_PHASE_16J3H"
    )

    trace = results["regen_end_to_end_candidate_selection_trace"]

    assert trace["population_count"] == 2
    assert trace["ranked_count"] >= 1
    assert trace["best_candidate_id"] == "CANDIDATE_A"
    assert trace["selected_candidate_id"] == "CANDIDATE_A"
    assert trace["recommendation_candidate_id"] == "CANDIDATE_A"
    assert trace["viewer_candidate_id"] == "CANDIDATE_A"
    assert trace["geometry_application_state"] == "LOCKED_NOT_APPLIED"

    assert results["phase_16j4_candidate_acceptance_integration_allowed"] is True
    assert results["regen_candidate_geometry_application_allowed"] is False
    assert results["regen_end_to_end_candidate_selection_live_geometry_commit_executed"] is False

    report = results["regen_end_to_end_candidate_selection_report"]
    assert "Validated Chain" in report
    assert "16J.4 Candidate Acceptance Integration" in report

    print("PASS_REGEN_END_TO_END_CANDIDATE_SELECTION_VALIDATION_PHASE_16J3H")


if __name__ == "__main__":
    main()
