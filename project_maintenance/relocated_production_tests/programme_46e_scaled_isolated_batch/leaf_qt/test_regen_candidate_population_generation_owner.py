from regen_candidate_population_generation_owner import (
    build_regen_candidate_population_generation_owner,
)


def run_test():
    results = {
        "phase_11b_2t_regen_objective_decision_master_gate_complete": True,
        "regen_objective_decision_architecture_complete": True,
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
        "coolant_flow_fraction": 1.0,
        "regen_population_requested_size": 16,
    }

    payload = build_regen_candidate_population_generation_owner(results)

    assert payload["regen_candidate_population_generation_owner_complete"] is True
    assert payload["phase_11b_3a_regen_candidate_population_generation_owner_complete"] is True
    assert payload["regen_candidate_population_generation_ready"] is True
    assert payload["regen_candidate_population_count"] == 16
    assert len(payload["regen_candidate_population"]) == 16
    assert payload["regen_candidate_population_solver_executed"] is False
    assert payload["regen_candidate_population_live_geometry_modified"] is False
    assert payload["regen_candidate_population_candidate_committed"] is False
    assert payload["regen_candidate_population_ranking_executed"] is False
    assert payload["regen_candidate_population_mutation_executed"] is False

    for candidate in payload["regen_candidate_population"]:
        assert candidate["candidate_status"] == "GENERATED_NOT_SOLVED_NOT_RANKED"
        assert candidate["candidate_metadata"]["phase"] == "11B.3A"
        assert candidate["candidate_metadata"]["ranking_allowed"] is False
        assert candidate["candidate_metadata"]["mutation_allowed"] is False
        assert candidate["candidate_geometry"]["coolant_channel_width"] > 0
        assert candidate["candidate_geometry"]["coolant_channel_height"] > 0
        assert candidate["candidate_geometry"]["rib_width"] > 0

    assert "LEAF PHASE 11B.3A" in payload["regen_candidate_population_generation_report"]

    print("PASS_REGEN_CANDIDATE_POPULATION_GENERATION_OWNER_PHASE_11B3A")
    return True


if __name__ == "__main__":
    run_test()
