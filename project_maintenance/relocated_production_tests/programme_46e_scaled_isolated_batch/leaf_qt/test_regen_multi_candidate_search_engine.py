from regen_multi_candidate_generator import attach_regen_multi_candidate_generator
from regen_multi_candidate_history_owner import attach_regen_multi_candidate_history_owner
from regen_multi_candidate_master_gate import attach_regen_multi_candidate_master_gate


def test_multi_candidate_generator_creates_population():
    solved = attach_regen_multi_candidate_generator({
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
    })

    assert solved["phase_11b_1l_regen_multi_candidate_generation_complete"] is True
    assert solved["regen_multi_candidate_generation_status"] == (
        "PASS_REGEN_MULTI_CANDIDATE_GENERATION_COMPLETE"
    )
    assert solved["regen_multi_candidate_count"] == 10
    assert len(solved["regen_multi_candidate_population"]) == 10


def test_multi_candidate_history_and_gate_pass():
    results = attach_regen_multi_candidate_generator({
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
    })

    results = attach_regen_multi_candidate_history_owner(results)
    results = attach_regen_multi_candidate_master_gate(results)

    assert results["phase_11b_1l_regen_multi_candidate_history_complete"] is True
    assert results["phase_11b_1l_regen_multi_candidate_master_gate_complete"] is True
    assert results["regen_multi_candidate_search_ready"] is True
    assert results["regen_multi_candidate_master_gate_status"] == (
        "PASS_REGEN_MULTI_CANDIDATE_SEARCH_READY"
    )