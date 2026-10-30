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

    assert results["regen_candidate_mutation_master_gate_complete"] is True
    assert results["phase_11b_5f_regen_candidate_mutation_master_gate_complete"] is True
    assert results["regen_candidate_mutation_master_gate_ready"] is True

    assert (
        results["regen_candidate_mutation_master_gate_status"]
        == "PASS_REGEN_CANDIDATE_MUTATION_MASTER_GATE_PHASE_11B5F"
    )

    assert results["regen_candidate_mutation_architecture_complete"] is True
    assert results["phase_11b_5_candidate_mutation_architecture_complete"] is True

    assert results["regen_candidate_evolution_architecture_allowed"] is True
    assert results["phase_11b_6_candidate_evolution_architecture_allowed"] is True

    assert results["regen_candidate_runtime_offspring_ranking_allowed"] is False
    assert results["regen_candidate_runtime_selection_allowed"] is False
    assert results["regen_candidate_runtime_evolution_allowed"] is False
    assert results["regen_candidate_runtime_solver_allowed"] is False
    assert results["regen_candidate_runtime_live_commit_allowed"] is False
    assert results["regen_candidate_runtime_acceptance_allowed"] is False

    assert results["regen_candidate_mutation_master_gate_offspring_ranked"] is False
    assert results["regen_candidate_mutation_master_gate_selection_executed"] is False
    assert results["regen_candidate_mutation_master_gate_evolution_executed"] is False
    assert results["regen_candidate_mutation_master_gate_solver_executed"] is False
    assert results["regen_candidate_mutation_master_gate_live_commit_executed"] is False
    assert results["regen_candidate_mutation_master_gate_candidate_acceptance_executed"] is False

    checks = results["regen_candidate_mutation_master_gate_checks"]
    failed = results["regen_candidate_mutation_master_gate_failed_checks"]

    assert isinstance(checks, list)
    assert len(checks) > 0
    assert failed == []

    report = results["regen_candidate_mutation_master_gate_report"]

    assert "LEAF PHASE 11B.5F" in report
    assert "Mutation architecture complete: True" in report
    assert "Evolution architecture may begin: True" in report
    assert "Runtime evolution allowed: False" in report
    assert "Failed checks: 0" in report

    print("PASS_REGEN_CANDIDATE_MUTATION_MASTER_GATE_PHASE_11B5F")
    return True


if __name__ == "__main__":
    run_test()
