from regen_ranking_input_feed_bridge import attach_regen_ranking_input_feed_bridge


def main():
    results = {
        "regen_candidate_population_candidates": [
            {
                "candidate_id": "CANDIDATE_A",
                "geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                },
            },
            {
                "candidate_id": "CANDIDATE_B",
                "candidate_geometry": {
                    "number_of_coolant_channels": 90,
                    "coolant_channel_width": 0.0012,
                },
            },
        ]
    }

    results = attach_regen_ranking_input_feed_bridge(results)

    assert results["phase_16j3d_complete"] is True
    assert results["phase_16j3d_status"] == "PASS_REGEN_RANKING_INPUT_FEED_BRIDGE_PHASE_16J3D"
    assert results["regen_ranking_input_feed_bridge_candidate_count"] == 2
    assert results["regen_ranking_input_feed_bridge_population_available"] is True

    population = results["regen_candidate_ranking_input_population"]
    assert len(population) == 2
    assert population[0]["candidate_id"] == "CANDIDATE_A"
    assert population[0]["candidate_geometry"]["number_of_coolant_channels"] == 80
    assert results["phase_16j3e_ranking_owner_recheck_allowed"] is True

    print("PASS_REGEN_RANKING_INPUT_FEED_BRIDGE_PHASE_16J3D")


if __name__ == "__main__":
    main()
