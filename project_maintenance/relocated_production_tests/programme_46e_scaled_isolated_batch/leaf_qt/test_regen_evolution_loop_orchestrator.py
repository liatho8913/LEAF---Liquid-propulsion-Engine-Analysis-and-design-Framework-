from regen_generation_builder import attach_regen_generation_builder
from regen_generation_validation_owner import attach_regen_generation_validation_owner
from regen_generation_scoring_owner import attach_regen_generation_scoring_owner
from regen_generation_selection_owner import attach_regen_generation_selection_owner
from regen_generation_selection_history_owner import attach_regen_generation_selection_history_owner
from regen_generation_selection_report_owner import attach_regen_generation_selection_report_owner
from regen_generation_selection_master_gate import attach_regen_generation_selection_master_gate
from regen_generation_evolution_controller import attach_regen_generation_evolution_controller
from regen_generation_evolution_history_owner import attach_regen_generation_evolution_history_owner
from regen_generation_evolution_master_gate import attach_regen_generation_evolution_master_gate
from regen_evolution_loop_orchestrator import attach_regen_evolution_loop_orchestrator
from regen_evolution_loop_history_owner import attach_regen_evolution_loop_history_owner
from regen_evolution_loop_master_gate import attach_regen_evolution_loop_master_gate


def build_ready_evolution_results():
    results = attach_regen_generation_builder({
        "regen_optimisation_next_action": "GENERATE_NEXT_GENERATION",
        "regen_convergence_generation_count": 1,
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
    results = attach_regen_generation_evolution_controller(results)
    results = attach_regen_generation_evolution_history_owner(results)
    results = attach_regen_generation_evolution_master_gate(results)
    return results


def test_evolution_loop_continues_when_ready():
    results = build_ready_evolution_results()

    results = attach_regen_evolution_loop_orchestrator(results)
    results = attach_regen_evolution_loop_history_owner(results)
    results = attach_regen_evolution_loop_master_gate(results)

    assert results["phase_11b_1t_regen_evolution_loop_complete"] is True
    assert results["phase_11b_1t_regen_evolution_loop_history_complete"] is True
    assert results["phase_11b_1t_regen_evolution_loop_master_gate_complete"] is True
    assert results["regen_evolution_loop_next_action"] == "BUILD_NEXT_GENERATION"
    assert results["regen_evolution_loop_master_gate_status"] == (
        "PASS_REGEN_EVOLUTION_LOOP_GATE_READY"
    )


def test_evolution_loop_blocks_without_evolution_ready():
    results = attach_regen_evolution_loop_orchestrator({})

    results = attach_regen_evolution_loop_history_owner(results)
    results = attach_regen_evolution_loop_master_gate(results)

    assert results["regen_evolution_loop_next_action"] == "BLOCKED"
    assert results["regen_evolution_loop_master_gate_ready"] is False


if __name__ == "__main__":
    test_evolution_loop_continues_when_ready()
    test_evolution_loop_blocks_without_evolution_ready()
    print("PASS_REGEN_EVOLUTION_LOOP_PHASE_11B1T")