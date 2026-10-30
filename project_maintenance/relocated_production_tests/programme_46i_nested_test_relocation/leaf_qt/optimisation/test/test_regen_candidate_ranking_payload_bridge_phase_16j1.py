from regen_candidate_ranking_payload_bridge import attach_regen_candidate_ranking_payload_bridge


def main():
    results = {
        "regen_optimisation_scored_candidates": [
            {
                "id": "CANDIDATE_A",
                "candidate_score": 91.5,
                "geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                },
                "scores": {
                    "thermal_margin": 40.0,
                    "pressure_drop": 30.0,
                    "geometry_fit": 21.5,
                },
            },
            {
                "id": "CANDIDATE_B",
                "candidate_score": 84.0,
                "geometry": {
                    "number_of_coolant_channels": 90,
                    "coolant_channel_width": 0.0012,
                },
            },
        ]
    }

    results = attach_regen_candidate_ranking_payload_bridge(results)

    assert results["phase_16j1_complete"] is True
    assert results["phase_16j1_status"] == "PASS_REGEN_CANDIDATE_RANKING_PAYLOAD_BRIDGE_PHASE_16J1"
    assert results["regen_candidate_ranking_payload_bridge_candidate_count"] == 2

    ranked = results["regen_candidate_ranking_inspector_ranked_candidates"]
    assert len(ranked) == 2
    assert ranked[0]["candidate_id"] == "CANDIDATE_A"
    assert ranked[0]["rank"] == 1
    assert ranked[0]["score"] == 91.5
    assert ranked[0]["winner"] is True
    assert ranked[1]["winner"] is False

    print("PASS_REGEN_CANDIDATE_RANKING_PAYLOAD_BRIDGE_PHASE_16J1")


if __name__ == "__main__":
    main()
