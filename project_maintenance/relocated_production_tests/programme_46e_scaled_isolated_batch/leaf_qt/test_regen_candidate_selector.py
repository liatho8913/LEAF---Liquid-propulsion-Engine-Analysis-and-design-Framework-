from regen_candidate_selector import attach_regen_candidate_selector


def test_regen_candidate_selector_selects_rank_one_candidate():
    results = {
        "regen_candidate_ranker_ranked_candidates": [
            {
                "candidate_id": "RCG-0002",
                "validation_status": "PASS_CANDIDATE_VALIDATION",
                "candidate_rank": 2,
                "candidate_rank_score": 5.0,
                "inputs": {"number_of_coolant_channels": 90},
            },
            {
                "candidate_id": "RCG-0001",
                "validation_status": "PASS_CANDIDATE_VALIDATION",
                "candidate_rank": 1,
                "candidate_rank_score": 2.0,
                "inputs": {"number_of_coolant_channels": 80},
            },
        ]
    }

    results = attach_regen_candidate_selector(results)

    assert results["phase_11b_1d_regen_candidate_selector_complete"] is True
    assert results["regen_candidate_selector_complete"] is True
    assert results["regen_candidate_selector_status"] == "PASS_RECOMMENDED_CANDIDATE_SELECTED"
    assert results["regen_candidate_selector_selected_candidate_id"] == "RCG-0001"
    assert results["recommended_regen_candidate_id"] == "RCG-0001"
    assert results["recommended_regen_candidate_inputs"]["number_of_coolant_channels"] == 80
    assert results["regen_candidate_geometry_application_allowed"] is False


def test_regen_candidate_selector_blocks_without_ranked_candidates():
    results = {
        "regen_candidate_ranker_ranked_candidates": []
    }

    results = attach_regen_candidate_selector(results)

    assert results["regen_candidate_selector_status"] == (
        "FAIL_RECOMMENDED_CANDIDATE_SELECTION_BLOCKED"
    )
    assert results["regen_candidate_selector_selected_candidate"] is None
    assert results["recommended_regen_candidate"] is None