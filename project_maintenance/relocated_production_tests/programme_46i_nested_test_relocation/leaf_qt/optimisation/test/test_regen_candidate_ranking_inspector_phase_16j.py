from regen_candidate_ranking_inspector import (
    get_ranked_candidates,
    build_ranking_summary,
    format_ranking_details,
)


def main():
    results = {
        "regen_optimisation_recommendation_ranked_candidates": [
            {
                "candidate_id": "CANDIDATE_001",
                "rank": 1,
                "score": 82.4,
                "candidate_status": "RANKED",
                "winner": True,
                "candidate_geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                    "coolant_channel_height": 0.002,
                    "rib_width": 0.001,
                    "hot_gas_wall_thickness": 0.001,
                },
                "score_breakdown": {
                    "thermal_margin": 35.0,
                    "pressure_drop": 20.0,
                    "geometry_fit": 27.4,
                },
                "penalties": {
                    "laminar_penalty": -4.0,
                },
                "failure_reasons": [],
                "ranking_explanation": "Best balance of thermal margin and geometry fit.",
            },
            {
                "candidate_id": "CANDIDATE_002",
                "rank": 2,
                "score": 76.1,
                "candidate_status": "RANKED_WITH_WARNINGS",
                "winner": False,
                "candidate_geometry": {
                    "number_of_coolant_channels": 90,
                    "coolant_channel_width": 0.0012,
                    "coolant_channel_height": 0.0024,
                    "rib_width": 0.0008,
                    "hot_gas_wall_thickness": 0.0011,
                },
                "score_breakdown": {
                    "thermal_margin": 38.0,
                    "pressure_drop": 12.0,
                    "geometry_fit": 26.1,
                },
                "penalties": {
                    "pressure_drop_penalty": -8.0,
                },
                "failure_reasons": ["Pressure drop margin reduced."],
            },
        ]
    }

    ranked = get_ranked_candidates(results)
    assert len(ranked) == 2

    summary = build_ranking_summary(ranked[0], 0)
    assert summary["rank"] == 1
    assert summary["id"] == "CANDIDATE_001"
    assert summary["score"] == 82.4
    assert summary["winner"] is True

    details = format_ranking_details(ranked[0], 0)
    assert "CANDIDATE RANKING DETAILS" in details
    assert "thermal_margin" in details
    assert "laminar_penalty" in details
    assert "Best balance" in details
    assert "read-only" in details.lower()

    print("PASS_REGEN_CANDIDATE_RANKING_INSPECTOR_PHASE_16J")


if __name__ == "__main__":
    main()
