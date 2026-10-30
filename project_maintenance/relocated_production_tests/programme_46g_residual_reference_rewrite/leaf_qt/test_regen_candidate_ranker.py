from regen_candidate_generator import attach_regen_candidate_generator
from regen_candidate_validator import attach_regen_candidate_validator
from regen_candidate_ranker import attach_regen_candidate_ranker


def test_regen_candidate_ranker_runs_after_validator():
    results = {
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0010,
        "channel_mid_radius": 0.02258,
        "coolant_density": 810.0,
        "coolant_dynamic_viscosity": 0.0012,
        "coolant_mass_flow_rate": 0.4,
        "regen_target_reynolds_number": 1000.0,
        "regen_derived_minimum_coolant_velocity": 0.01,
        "regen_derived_maximum_coolant_velocity": 200.0,
        "minimum_hot_gas_wall_thickness": 0.0005,
        "maximum_hot_gas_wall_thickness": 0.006,
        "material_validation_mode": "SOURCED_VALIDATION_MODE",
        "coating_validation_mode": "SOURCED_VALIDATION_MODE",
    }

    results = attach_regen_candidate_generator(results)
    results = attach_regen_candidate_validator(results)
    results = attach_regen_candidate_ranker(results)

    assert results["phase_11b_1c_regen_candidate_ranker_complete"] is True
    assert results["regen_candidate_ranker_complete"] is True

    if results["regen_candidate_validator_pass_count"] > 0:
        assert results["regen_candidate_ranker_ranked_count"] > 0
        assert results["regen_candidate_ranker_best_candidate"] is not None
        assert results["regen_candidate_ranker_best_candidate_id"] is not None

        best = results["regen_candidate_ranker_best_candidate"]

        assert best["candidate_rank"] == 1
        assert best["candidate_ranking_status"] == "RANKED_PASSING_CANDIDATE"
        assert "candidate_rank_score" in best
        assert "candidate_rank_score_parts" in best


def test_regen_candidate_ranker_ignores_failed_candidates():
    results = {
        "regen_candidate_validator_validated_candidates": [
            {
                "candidate_id": "RCG-FAIL-0001",
                "validation_status": "FAIL_CANDIDATE_VALIDATION",
                "inputs": {},
                "preview_metrics": {},
                "validation_metrics": {},
            }
        ]
    }

    results = attach_regen_candidate_ranker(results)

    assert results["regen_candidate_ranker_status"] == "FAIL_NO_PASSING_CANDIDATES_TO_RANK"
    assert results["regen_candidate_ranker_ranked_count"] == 0
    assert results["regen_candidate_ranker_best_candidate"] is None