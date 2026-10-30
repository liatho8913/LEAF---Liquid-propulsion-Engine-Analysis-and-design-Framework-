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

    assert results["regen_evolution_loop_input_audit_complete"] is True
    assert results["phase_11b_6a_regen_evolution_loop_input_audit_complete"] is True
    assert results["regen_evolution_loop_input_audit_ready"] is True

    assert (
        results["regen_evolution_loop_input_audit_status"]
        == "PASS_REGEN_EVOLUTION_LOOP_INPUT_AUDIT_PHASE_11B6A"
    )

    assert results["regen_evolution_loop_owner_architecture_allowed"] is True
    assert results["phase_11b_6b_evolution_loop_owner_allowed"] is True

    assert results["regen_evolution_loop_input_audit_generation_advanced"] is False
    assert results["regen_evolution_loop_input_audit_evolution_executed"] is False
    assert results["regen_evolution_loop_input_audit_offspring_ranked"] is False
    assert results["regen_evolution_loop_input_audit_selection_executed"] is False
    assert results["regen_evolution_loop_input_audit_convergence_checked"] is False
    assert results["regen_evolution_loop_input_audit_solver_executed"] is False
    assert results["regen_evolution_loop_input_audit_live_commit_executed"] is False
    assert results["regen_evolution_loop_input_audit_candidate_acceptance_executed"] is False

    assert results["regen_candidate_runtime_generation_advance_allowed"] is False
    assert results["regen_candidate_runtime_evolution_allowed"] is False
    assert results["regen_candidate_runtime_offspring_ranking_allowed"] is False
    assert results["regen_candidate_runtime_selection_allowed"] is False
    assert results["regen_candidate_runtime_convergence_allowed"] is False
    assert results["regen_candidate_runtime_solver_allowed"] is False
    assert results["regen_candidate_runtime_live_commit_allowed"] is False
    assert results["regen_candidate_runtime_acceptance_allowed"] is False

    failed = results["regen_evolution_loop_input_audit_failed_checks"]
    assert failed == []

    report = results["regen_evolution_loop_input_audit_report"]

    assert "LEAF PHASE 11B.6A" in report
    assert "11B.6B Evolution Loop Owner architecture allowed: True" in report
    assert "Runtime evolution allowed: False" in report
    assert "Failed checks: 0" in report

    print("PASS_REGEN_EVOLUTION_LOOP_INPUT_AUDIT_PHASE_11B6A")
    return True


if __name__ == "__main__":
    run_test()
