from regen_candidate_population_generation_owner import build_regen_candidate_population_generation_owner
from regen_candidate_population_report_owner import build_regen_candidate_population_report_owner
from regen_candidate_population_registration_owner import build_regen_candidate_population_registration_owner
from regen_candidate_population_completion_audit import build_regen_candidate_population_completion_audit
from regen_candidate_population_master_gate import build_regen_candidate_population_master_gate
from regen_candidate_ranking_input_audit import build_regen_candidate_ranking_input_audit
from regen_candidate_ranking_owner import build_regen_candidate_ranking_owner
from regen_candidate_ranking_report_owner import build_regen_candidate_ranking_report_owner
from regen_candidate_ranking_registration_owner import build_regen_candidate_ranking_registration_owner
from regen_candidate_ranking_completion_audit import build_regen_candidate_ranking_completion_audit
from regen_candidate_ranking_master_gate import build_regen_candidate_ranking_master_gate
from regen_candidate_mutation_input_audit import build_regen_candidate_mutation_input_audit
from regen_candidate_mutation_owner import build_regen_candidate_mutation_owner
from regen_candidate_mutation_report_owner import build_regen_candidate_mutation_report_owner
from regen_candidate_mutation_registration_owner import build_regen_candidate_mutation_registration_owner
from regen_candidate_mutation_completion_audit import build_regen_candidate_mutation_completion_audit
from regen_candidate_mutation_master_gate import build_regen_candidate_mutation_master_gate
from regen_evolution_loop_input_audit import build_regen_evolution_loop_input_audit
from regen_evolution_loop_owner import build_regen_evolution_loop_owner


def run_test():
    results = {
        "phase_11b_2t_regen_objective_decision_master_gate_complete": True,
        "regen_objective_decision_architecture_complete": True,
        "regen_candidate_ranking_objective_requested": "BALANCED",
        "number_of_coolant_channels": 80,
        "coolant_channel_width": 0.0015,
        "coolant_channel_height": 0.0020,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0012,
        "coolant_flow_fraction": 1.0,
        "regen_population_requested_size": 16,
        "regen_evolution_population_size": 16,
        "regen_evolution_generation_limit": 1,
        "regen_evolution_elite_count": 1,
        "regen_evolution_mutation_count": 1,
        "regen_evolution_mutation_rate": 0.06,
        "regen_evolution_convergence_tolerance": 0.001,
    }

    results.update(build_regen_candidate_population_generation_owner(results))
    results.update(build_regen_candidate_population_report_owner(results))
    results.update(build_regen_candidate_population_registration_owner(results))
    results.update(build_regen_candidate_population_completion_audit(results))
    results.update(build_regen_candidate_population_master_gate(results))
    results.update(build_regen_candidate_ranking_input_audit(results))
    results.update(build_regen_candidate_ranking_owner(results))
    results.update(build_regen_candidate_ranking_report_owner(results))
    results.update(build_regen_candidate_ranking_registration_owner(results))
    results.update(build_regen_candidate_ranking_completion_audit(results))
    results.update(build_regen_candidate_ranking_master_gate(results))
    results.update(build_regen_candidate_mutation_input_audit(results))
    results.update(build_regen_candidate_mutation_owner(results))
    results.update(build_regen_candidate_mutation_report_owner(results))
    results.update(build_regen_candidate_mutation_registration_owner(results))
    results.update(build_regen_candidate_mutation_completion_audit(results))
    results.update(build_regen_candidate_mutation_master_gate(results))
    results.update(build_regen_evolution_loop_input_audit(results))
    results.update(build_regen_evolution_loop_owner(results))

    assert results["regen_evolution_loop_owner_complete"] is True
    assert results["phase_11b_6b_regen_evolution_loop_owner_complete"] is True
    assert results["regen_evolution_loop_ready"] is True

    assert (
        results["regen_evolution_loop_status"]
        == "PASS_REGEN_EVOLUTION_LOOP_OWNER_PHASE_11B6B"
    )

    gen1 = results["regen_evolution_generation_1_record"]
    gen2 = results["regen_evolution_generation_2_record"]
    state = results["regen_evolution_loop_state"]
    history = results["regen_evolution_loop_history"]

    assert gen1["generation_number"] == 1
    assert gen1["generation_id"] == "GEN_001"
    assert gen1["population_count"] == 16
    assert gen1["runtime_generation_advanced"] is False

    assert gen2["generation_number"] == 2
    assert gen2["generation_id"] == "GEN_002"
    assert gen2["population_count"] == 1
    assert gen2["offspring_candidate_id"] == results["regen_candidate_offspring_candidate"]["candidate_id"]
    assert gen2["runtime_generation_advanced"] is False

    assert state["status"] == "LOOP_ARCHITECTURE_CREATED_NOT_EXECUTED"
    assert state["current_generation"] == 1
    assert state["next_generation"] == 2
    assert state["runtime_evolution_executed"] is False

    assert isinstance(history, list)
    assert len(history) == 2
    assert results["regen_evolution_loop_history_count"] == 2

    assert results["regen_evolution_loop_architecture_created"] is True
    assert results["regen_evolution_loop_generation_record_created"] is True
    assert results["regen_evolution_loop_generation_advanced"] is False
    assert results["regen_evolution_loop_runtime_executed"] is False
    assert results["regen_evolution_loop_offspring_ranked"] is False
    assert results["regen_evolution_loop_selection_executed"] is False
    assert results["regen_evolution_loop_convergence_checked"] is False
    assert results["regen_evolution_loop_solver_executed"] is False
    assert results["regen_evolution_loop_live_commit_executed"] is False
    assert results["regen_evolution_loop_candidate_acceptance_executed"] is False

    assert results["regen_evolution_loop_report_owner_allowed"] is True
    assert results["phase_11b_6c_evolution_loop_report_owner_allowed"] is True

    report = results["regen_evolution_loop_report"]

    assert "LEAF PHASE 11B.6B" in report
    assert "Generation advanced: False" in report
    assert "Runtime evolution executed: False" in report
    assert "Candidate acceptance executed: False" in report

    print("PASS_REGEN_EVOLUTION_LOOP_OWNER_PHASE_11B6B")
    return True


if __name__ == "__main__":
    run_test()
