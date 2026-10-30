from regen_generation_builder import attach_regen_generation_builder
from regen_generation_validation_owner import (
    attach_regen_generation_validation_owner,
)
from regen_generation_validation_history_owner import (
    attach_regen_generation_validation_history_owner,
)
from regen_generation_validation_report_owner import (
    attach_regen_generation_validation_report_owner,
)
from regen_generation_validation_master_gate import (
    attach_regen_generation_validation_master_gate,
)


def test_generation_validation_pipeline_passes_valid_generation():
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

    results = attach_regen_generation_validation_owner(results)
    results = attach_regen_generation_validation_history_owner(results)
    results = attach_regen_generation_validation_report_owner(results)
    results = attach_regen_generation_validation_master_gate(results)

    assert results["phase_11b_1p_regen_generation_validation_complete"] is True
    assert results["phase_11b_1p_regen_generation_validation_history_complete"] is True
    assert results["phase_11b_1p_regen_generation_validation_report_complete"] is True
    assert results["phase_11b_1p_regen_generation_validation_master_gate_complete"] is True

    assert results["regen_generation_valid_candidate_count"] > 0
    assert results["regen_generation_validation_ready"] is True
    assert results["regen_generation_validation_master_gate_status"] == (
        "PASS_REGEN_GENERATION_VALIDATION_GATE_READY"
    )


def test_generation_validation_blocks_invalid_generation():
    results = {
        "regen_generation_population": [
            {
                "candidate_id": "BAD",
                "candidate_generation": 2,
                "candidate_geometry": {
                    "number_of_coolant_channels": 0,
                    "coolant_channel_width": -1.0,
                    "coolant_channel_height": 0.0,
                    "rib_width": 0.0,
                    "hot_gas_wall_thickness": -0.001,
                },
            }
        ]
    }

    results = attach_regen_generation_validation_owner(results)
    results = attach_regen_generation_validation_history_owner(results)
    results = attach_regen_generation_validation_report_owner(results)
    results = attach_regen_generation_validation_master_gate(results)

    assert results["regen_generation_valid_candidate_count"] == 0
    assert results["regen_generation_validation_ready"] is False
    assert results["regen_generation_validation_master_gate_status"] == (
        "FAIL_REGEN_GENERATION_VALIDATION_GATE_NO_VALID_CANDIDATES"
    )


if __name__ == "__main__":
    test_generation_validation_pipeline_passes_valid_generation()
    test_generation_validation_blocks_invalid_generation()
    print("PASS_REGEN_GENERATION_VALIDATION_PHASE_11B1P")