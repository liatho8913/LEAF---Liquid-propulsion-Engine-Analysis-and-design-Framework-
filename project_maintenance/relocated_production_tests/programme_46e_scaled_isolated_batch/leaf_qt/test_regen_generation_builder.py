from regen_generation_builder import attach_regen_generation_builder


def test_generation_builder_creates_next_generation():
    results = attach_regen_generation_builder({
        "regen_optimisation_next_action": "GENERATE_NEXT_GENERATION",
        "regen_optimisation_best_candidate": {
            "candidate_id": "RMC-0001",
            "score": 0.25,
            "decision": "BEST_SO_FAR",
            "candidate_geometry": {
                "number_of_coolant_channels": 80,
                "coolant_channel_width": 0.0015,
                "coolant_channel_height": 0.0020,
                "rib_width": 0.0010,
                "hot_gas_wall_thickness": 0.0012,
                "coolant_flow_fraction": 1.0,
            },
        },
    })

    assert results["phase_11b_1o_regen_generation_builder_complete"] is True
    assert results["regen_generation_ready"] is True
    assert results["regen_generation_candidate_count"] == 10
    assert results["regen_generation_population"][0]["candidate_generation"] == 2
    assert results["regen_generation_solver_executed"] is False
    assert results["regen_generation_live_geometry_modified"] is False
    assert results["regen_generation_candidate_committed"] is False


def test_generation_builder_blocks_without_next_action():
    results = attach_regen_generation_builder({
        "regen_optimisation_next_action": "WAIT",
        "regen_optimisation_best_candidate": {
            "candidate_geometry": {
                "number_of_coolant_channels": 80,
            },
        },
    })

    assert results["regen_generation_ready"] is False
    assert results["regen_generation_builder_status"] == (
        "FAIL_REGEN_GENERATION_BUILDER_BLOCKED"
    )


def test_generation_builder_uses_result_geometry_fallback():
    results = attach_regen_generation_builder({
        "regen_optimisation_next_action": "GENERATE_NEXT_GENERATION",
        "regen_optimisation_best_candidate": {
            "candidate_id": "BEST",
            "score": 0.25,
        },
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
    })

    assert results["regen_generation_ready"] is True
    assert results["regen_generation_candidate_count"] == 10


if __name__ == "__main__":
    test_generation_builder_creates_next_generation()
    test_generation_builder_blocks_without_next_action()
    test_generation_builder_uses_result_geometry_fallback()
    print("PASS_REGEN_GENERATION_BUILDER_PHASE_11B1O")