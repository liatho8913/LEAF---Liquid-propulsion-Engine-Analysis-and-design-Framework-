from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair


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

    assert results["phase_16j3e_complete"] is True
    assert results["phase_16j3e_status"] == "PASS_REGEN_RANKING_OWNER_SOURCE_REPAIR_PHASE_16J3E"
    assert results["regen_ranking_owner_source_repair_ranked_count"] == 2

    ranked = results["regen_candidate_ranking_inspector_ranked_candidates"]
    assert len(ranked) == 2
    assert ranked[0]["rank"] == 1
    assert ranked[0]["winner"] is True
    assert ranked[0]["candidate_id"] == "CANDIDATE_A"

    assert results["regen_candidate_ranking_best_candidate"]["candidate_id"] == "CANDIDATE_A"
    assert results["regen_candidate_ranking_owner_complete"] is True
    assert results["phase_16j3f_recommendation_feed_repair_allowed"] is True

    print("PASS_REGEN_RANKING_OWNER_SOURCE_REPAIR_PHASE_16J3E")


if __name__ == "__main__":
    main()
