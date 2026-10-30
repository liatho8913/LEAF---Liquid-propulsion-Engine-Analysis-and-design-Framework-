from regen_generation_persistence_owner import (
    attach_regen_generation_persistence_owner,
)
from regen_generation_persistence_master_gate import (
    attach_regen_generation_persistence_master_gate,
)


def test_generation_persistence_passes_with_valid_loop_state():
    results = {
        "regen_evolution_loop_complete": True,
        "regen_evolution_loop_ready": True,
        "regen_evolution_loop_next_action": "BUILD_NEXT_GENERATION",
        "regen_evolution_loop_generation": 2,
        "regen_generation_population": [
            {
                "candidate_id": "RGEN2-0001",
                "candidate_generation": 2,
                "candidate_geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                    "coolant_channel_height": 0.0020,
                    "rib_width": 0.0010,
                    "hot_gas_wall_thickness": 0.0012,
                    "coolant_flow_fraction": 1.0,
                },
            }
        ],
        "regen_generation_scored_candidates": [
            {
                "candidate_id": "RGEN2-0001",
                "candidate_score": 150.0,
            }
        ],
        "regen_generation_selected_candidate": {
            "candidate_id": "RGEN2-0001",
            "candidate_score": 150.0,
            "candidate_generation": 2,
            "candidate_geometry": {
                "number_of_coolant_channels": 80,
                "coolant_channel_width": 0.0015,
                "coolant_channel_height": 0.0020,
                "rib_width": 0.0010,
                "hot_gas_wall_thickness": 0.0012,
                "coolant_flow_fraction": 1.0,
            },
        },
        "regen_generation_evolution_seed_geometry": {
            "number_of_coolant_channels": 80,
            "coolant_channel_width": 0.0015,
        },
    }

    results = attach_regen_generation_persistence_owner(results)
    results = attach_regen_generation_persistence_master_gate(results)

    assert results["phase_11b_1u_regen_generation_persistence_complete"] is True
    assert results["phase_11b_1u_regen_generation_persistence_master_gate_complete"] is True
    assert results["regen_generation_persistence_status"] == (
        "PASS_REGEN_GENERATION_PERSISTENCE_STORED"
    )
    assert results["regen_generation_persistence_master_gate_status"] == (
        "PASS_REGEN_GENERATION_PERSISTENCE_GATE_READY"
    )
    assert results["regen_generation_archive_count"] == 1
    assert results["regen_generation_archive"][0]["winner_id"] == "RGEN2-0001"
    assert results["regen_generation_archive"][0]["winner_score"] == 150.0

    assert results["regen_generation_persistence_solver_executed"] is False
    assert results["regen_generation_persistence_live_geometry_modified"] is False
    assert results["regen_generation_persistence_candidate_committed"] is False


def test_generation_persistence_blocks_without_loop_state():
    results = {}

    results = attach_regen_generation_persistence_owner(results)
    results = attach_regen_generation_persistence_master_gate(results)

    assert results["regen_generation_persistence_ready"] is False
    assert results["regen_generation_archive_count"] == 0
    assert results["regen_generation_persistence_master_gate_ready"] is False


if __name__ == "__main__":
    test_generation_persistence_passes_with_valid_loop_state()
    test_generation_persistence_blocks_without_loop_state()
    print("PASS_REGEN_GENERATION_PERSISTENCE_PHASE_11B1U")