from regen_generation_builder import attach_regen_generation_builder
from regen_generation_validation_owner import (
    attach_regen_generation_validation_owner,
)
from regen_generation_scoring_owner import (
    attach_regen_generation_scoring_owner,
)
from regen_generation_selection_owner import (
    attach_regen_generation_selection_owner,
)
from regen_generation_selection_history_owner import (
    attach_regen_generation_selection_history_owner,
)
from regen_generation_selection_report_owner import (
    attach_regen_generation_selection_report_owner,
)
from regen_generation_selection_master_gate import (
    attach_regen_generation_selection_master_gate,
)


def test_generation_selection_pipeline_selects_winner():
    results = attach_regen_generation_builder({
        "regen_optimisation_next_action": "GENERATE_NEXT_GENERATION",
        "regen_optimisation_best_candidate": {
            "candidate_id": "RMC-0001",
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
    results = attach_regen_generation_scoring_owner(results)
    results = attach_regen_generation_selection_owner(results)
    results = attach_regen_generation_selection_history_owner(results)
    results = attach_regen_generation_selection_report_owner(results)
    results = attach_regen_generation_selection_master_gate(results)

    assert results["phase_11b_1r_regen_generation_selection_complete"] is True
    assert results["phase_11b_1r_regen_generation_selection_history_complete"] is True
    assert results["phase_11b_1r_regen_generation_selection_report_complete"] is True
    assert results["phase_11b_1r_regen_generation_selection_master_gate_complete"] is True

    assert results["regen_generation_selection_master_gate_ready"] is True
    assert results["regen_generation_selected_candidate"] is not None
    assert results["regen_generation_selection_master_gate_status"] == (
        "PASS_REGEN_GENERATION_SELECTION_GATE_READY"
    )


def test_generation_selection_blocks_without_scored_candidates():
    results = {
        "regen_generation_scored_candidates": []
    }

    results = attach_regen_generation_selection_owner(results)
    results = attach_regen_generation_selection_history_owner(results)
    results = attach_regen_generation_selection_report_owner(results)
    results = attach_regen_generation_selection_master_gate(results)

    assert results["regen_generation_selection_master_gate_ready"] is False
    assert results["regen_generation_selection_master_gate_status"] == (
        "FAIL_REGEN_GENERATION_SELECTION_GATE_NO_WINNER"
    )


if __name__ == "__main__":
    test_generation_selection_pipeline_selects_winner()
    test_generation_selection_blocks_without_scored_candidates()
    print("PASS_REGEN_GENERATION_SELECTION_PHASE_11B1R")