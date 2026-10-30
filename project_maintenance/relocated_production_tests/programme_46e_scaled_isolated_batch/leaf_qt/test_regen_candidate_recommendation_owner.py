from regen_candidate_recommendation_owner import (
    attach_regen_candidate_recommendation_owner,
)


def test_recommendation_owner_publishes_selected_candidate():
    selected = {
        "candidate_id": "RCG-0001",
        "validation_status": "PASS_CANDIDATE_VALIDATION",
        "candidate_rank": 1,
        "candidate_rank_score": 2.0,
        "candidate_rank_score_parts": {
            "geometry_fit_score": 0.5,
            "reynolds_score": 0.2,
        },
        "candidate_ranking_reason": "Best candidate by score.",
        "inputs": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
            "hot_gas_wall_thickness": 0.001,
        },
        "validation_metrics": {
            "fit_ratio": 1.1,
            "coolant_reynolds_preview": 12000.0,
            "coolant_velocity_preview": 18.0,
            "aspect_ratio": 1.333,
            "hot_gas_wall_thickness": 0.001,
        },
        "pass_reasons": ["Candidate passed validation."],
        "failure_reasons": [],
    }

    results = {
        "regen_candidate_selector_selected_candidate": selected,
        "regen_candidate_ranker_ranked_candidates": [selected],
        "regen_candidate_validator_validated_candidates": [selected],
    }

    results = attach_regen_candidate_recommendation_owner(results)

    assert results["phase_11b_1e_regen_candidate_recommendation_owner_complete"] is True
    assert results["regen_candidate_recommendation_owner_complete"] is True
    assert results["regen_candidate_recommendation_owner_status"] == (
        "PASS_REGEN_CANDIDATE_RECOMMENDATION_READY"
    )
    assert results["regen_candidate_recommendation_id"] == "RCG-0001"
    assert results["recommended_full_engine_regen_candidate_id"] == "RCG-0001"
    assert results["regen_candidate_recommendation_ready_for_application"] is True
    assert results["regen_candidate_geometry_application_allowed"] is False
    assert "Geometry has not been applied" in results["regen_candidate_recommendation_summary"]


def test_recommendation_owner_blocks_without_selected_candidate():
    results = {
        "regen_candidate_selector_selected_candidate": None,
        "regen_candidate_ranker_ranked_candidates": [],
        "regen_candidate_validator_validated_candidates": [],
    }

    results = attach_regen_candidate_recommendation_owner(results)

    assert results["regen_candidate_recommendation_owner_status"] == (
        "FAIL_REGEN_CANDIDATE_RECOMMENDATION_BLOCKED"
    )
    assert results["regen_candidate_recommendation"] is None
    assert results["recommended_full_engine_regen_candidate"] is None