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
from regen_next_generation_builder import attach_regen_next_generation_builder
from regen_next_generation_history_owner import attach_regen_next_generation_history_owner
from regen_next_generation_report_owner import attach_regen_next_generation_report_owner
from regen_next_generation_master_gate import attach_regen_next_generation_master_gate


def build_ready_loop_results():
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
    results = attach_regen_evolution_loop_orchestrator(results)
    results = attach_regen_evolution_loop_history_owner(results)
    results = attach_regen_evolution_loop_master_gate(results)
    return results


def test_next_generation_builder_creates_generation_two_population():
    results = build_ready_loop_results()

    results = attach_regen_next_generation_builder(results)
    results = attach_regen_next_generation_history_owner(results)
    results = attach_regen_next_generation_report_owner(results)
    results = attach_regen_next_generation_master_gate(results)

    assert results["phase_11b_1u_regen_next_generation_builder_complete"] is True
    assert results["phase_11b_1u_regen_next_generation_history_complete"] is True
    assert results["phase_11b_1u_regen_next_generation_report_complete"] is True
    assert results["phase_11b_1u_regen_next_generation_master_gate_complete"] is True
    assert results["regen_next_generation_builder_status"] == (
        "PASS_REGEN_NEXT_GENERATION_BUILDER_CREATED"
    )
    assert results["regen_next_generation_master_gate_status"] == (
        "PASS_REGEN_NEXT_GENERATION_GATE_READY"
    )
    assert results["regen_next_generation_number"] == 2
    assert results["regen_next_generation_candidate_count"] == 12
    assert results["regen_next_generation_solver_executed"] is False
    assert results["regen_next_generation_live_geometry_modified"] is False
    assert results["regen_next_generation_candidate_committed"] is False


def test_next_generation_builder_blocks_without_loop_request():
    results = attach_regen_next_generation_builder({})
    results = attach_regen_next_generation_history_owner(results)
    results = attach_regen_next_generation_report_owner(results)
    results = attach_regen_next_generation_master_gate(results)

    assert results["regen_next_generation_builder_ready"] is False
    assert results["regen_next_generation_master_gate_ready"] is False
    assert results["regen_next_generation_candidate_count"] == 0


if __name__ == "__main__":
    test_next_generation_builder_creates_generation_two_population()
    test_next_generation_builder_blocks_without_loop_request()
    print("PASS_REGEN_NEXT_GENERATION_BUILDER_PHASE_11B1U")
