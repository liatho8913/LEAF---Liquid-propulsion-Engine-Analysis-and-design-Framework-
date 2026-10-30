from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair


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

    assert results["phase_16j3g_complete"] is True
    assert results["phase_16j3g_status"] == "PASS_REGEN_RECOMMENDATION_VIEWER_REPAIR_PHASE_16J3G"

    payload = results["regen_recommendation_viewer_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["rank"] == 1
    assert payload["geometry_application_state"] == "LOCKED_NOT_APPLIED"

    report = results["regen_recommendation_viewer_report"]
    assert "Recommendation Display" in report
    assert "Candidate ID: CANDIDATE_A" in report
    assert "Geometry application: LOCKED" in report

    assert results["regen_recommendation_display_candidate_id"] == "CANDIDATE_A"
    assert results["regen_candidate_geometry_application_allowed"] is False
    assert results["regen_recommendation_viewer_live_geometry_commit_executed"] is False
    assert results["phase_16j3h_end_to_end_selection_validation_allowed"] is True

    print("PASS_REGEN_RECOMMENDATION_VIEWER_REPAIR_PHASE_16J3G")


if __name__ == "__main__":
    main()
