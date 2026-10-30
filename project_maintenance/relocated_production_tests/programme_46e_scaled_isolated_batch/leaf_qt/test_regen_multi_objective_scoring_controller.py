from regen_multi_objective_scoring_controller import (
    attach_regen_multi_objective_scoring_controller,
)
from regen_multi_objective_scoring_history_owner import (
    attach_regen_multi_objective_scoring_history_owner,
)
from regen_multi_objective_scoring_report_owner import (
    attach_regen_multi_objective_scoring_report_owner,
)
from regen_multi_objective_scoring_master_gate import (
    attach_regen_multi_objective_scoring_master_gate,
)


def apply_chain(results):
    results = attach_regen_multi_objective_scoring_controller(results)
    results = attach_regen_multi_objective_scoring_history_owner(results)
    results = attach_regen_multi_objective_scoring_report_owner(results)
    results = attach_regen_multi_objective_scoring_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_exploration_master_gate_ready": True,
        "hot_gas_wall_temperature": 800.0,
        "material_max_wall_temperature": 1000.0,
        "regen_pressure_drop": 100000.0,
        "chamber_pressure": 7000000.0,
        "coolant_velocity": 20.0,
        "channel_geometry_valid": True,
        "regen_channel_fit_ratio": 0.95,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.002,
        "rib_width": 0.001,
        "hot_gas_wall_thickness": 0.0012,
        "material_validation_status": "PASS_MATERIAL_VALIDATION",
        "regen_validation_status": "PASS_REGEN_VALIDATION",
    }


def test_multi_objective_scoring_passes_good_design():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2d_regen_multi_objective_scoring_complete"] is True
    assert results["phase_11b_2d_regen_multi_objective_scoring_history_complete"] is True
    assert results["phase_11b_2d_regen_multi_objective_scoring_report_complete"] is True
    assert results["phase_11b_2d_regen_multi_objective_scoring_master_gate_complete"] is True

    assert results["regen_multi_objective_scoring_status"] == (
        "PASS_REGEN_MULTI_OBJECTIVE_SCORING_READY"
    )
    assert results["regen_multi_objective_scoring_master_gate_status"] == (
        "PASS_REGEN_MULTI_OBJECTIVE_SCORING_GATE_READY"
    )

    assert results["regen_multi_objective_total_score"] > 80.0
    assert isinstance(results["regen_multi_objective_scores"], dict)

    assert results["regen_multi_objective_scoring_solver_executed"] is False
    assert results["regen_multi_objective_scoring_live_geometry_modified"] is False
    assert results["regen_multi_objective_scoring_candidate_committed"] is False


def test_multi_objective_scoring_penalises_overheated_wall():
    results = base_ready_results()
    results["hot_gas_wall_temperature"] = 1200.0

    results = apply_chain(results)

    assert results["regen_multi_objective_scores"]["thermal_margin"] < 50.0
    assert results["regen_multi_objective_total_score"] < 90.0


def test_multi_objective_scoring_blocks_without_exploration_gate():
    results = {}

    results = apply_chain(results)

    assert results["regen_multi_objective_scoring_ready"] is False
    assert results["regen_multi_objective_scoring_master_gate_ready"] is False


if __name__ == "__main__":
    test_multi_objective_scoring_passes_good_design()
    test_multi_objective_scoring_penalises_overheated_wall()
    test_multi_objective_scoring_blocks_without_exploration_gate()
    print("PASS_REGEN_MULTI_OBJECTIVE_SCORING_CONTROLLER_PHASE_11B2D")