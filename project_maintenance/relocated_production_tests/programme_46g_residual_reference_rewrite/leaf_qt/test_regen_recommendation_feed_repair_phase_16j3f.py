from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair


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
    assert results["phase_16j3f_recommendation_feed_repair_allowed"] is True

    results = attach_regen_recommendation_feed_repair(results)

    assert results["regen_recommendation_feed_repair_complete"] is True
    assert results["phase_16j3f_complete"] is True
    assert results["phase_16j3f_status"] == "PASS_REGEN_RECOMMENDATION_FEED_REPAIR_PHASE_16J3F"

    selected = results["regen_recommendation_feed_repair_selected_candidate"]
    assert selected["candidate_id"] == "CANDIDATE_A"
    assert selected["candidate_rank"] == 1
    assert selected["validation_status"] == "PASS_CANDIDATE_VALIDATION"

    recommendation = results["regen_candidate_recommendation"]
    assert recommendation is not None
    assert recommendation["candidate_id"] == "CANDIDATE_A"
    assert results["regen_candidate_recommendation_owner_status"] == "PASS_REGEN_CANDIDATE_RECOMMENDATION_READY"

    assert results["regen_recommendation_viewer_feed_payload"] is recommendation
    assert results["phase_16j3g_recommendation_viewer_repair_allowed"] is True

    assert results["regen_recommendation_feed_repair_live_geometry_commit_executed"] is False
    assert results["regen_recommendation_feed_repair_geometry_application_executed"] is False
    assert results["regen_candidate_geometry_application_allowed"] is False

    print("PASS_REGEN_RECOMMENDATION_FEED_REPAIR_PHASE_16J3F")


if __name__ == "__main__":
    main()
