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

    assert results["regen_candidate_mutation_owner_complete"] is True
    assert results["phase_11b_5b_regen_candidate_mutation_owner_complete"] is True
    assert results["regen_candidate_mutation_ready"] is True

    assert (
        results["regen_candidate_mutation_status"]
        == "PASS_REGEN_CANDIDATE_MUTATION_OWNER_PHASE_11B5B"
    )

    parent = results["regen_candidate_parent_candidate"]
    offspring = results["regen_candidate_offspring_candidate"]
    delta = results["regen_candidate_mutation_delta"]
    safety = results["regen_candidate_mutation_safety"]

    assert isinstance(parent, dict)
    assert isinstance(offspring, dict)
    assert isinstance(delta, dict)
    assert isinstance(safety, dict)

    assert offspring["candidate_parent"] == parent["candidate_id"]
    assert offspring["candidate_status"] == "MUTATED_NOT_RANKED_NOT_SOLVED_NOT_COMMITTED"
    assert offspring["candidate_rank_status"] == "MUTATED_NOT_RANKED_NOT_SOLVED_NOT_COMMITTED"
    assert offspring["candidate_mutation_owner"] == "REGEN_CANDIDATE_MUTATION_OWNER"
    assert offspring["candidate_mutation_phase"] == "11B.5B"

    assert "ranking" not in offspring

    assert safety["ready"] is True
    assert safety["failed_checks"] == []

    assert results["regen_candidate_mutation_owner_mutation_executed"] is True
    assert results["regen_candidate_mutation_owner_offspring_created"] is True

    assert results["regen_candidate_mutation_owner_offspring_ranked"] is False
    assert results["regen_candidate_mutation_owner_selection_executed"] is False
    assert results["regen_candidate_mutation_owner_evolution_executed"] is False
    assert results["regen_candidate_mutation_owner_solver_executed"] is False
    assert results["regen_candidate_mutation_owner_live_commit_executed"] is False
    assert results["regen_candidate_mutation_owner_candidate_acceptance_executed"] is False

    assert results["regen_candidate_mutation_report_owner_allowed"] is True
    assert results["phase_11b_5c_candidate_mutation_report_owner_allowed"] is True

    report = results["regen_candidate_mutation_report"]

    assert "LEAF PHASE 11B.5B" in report
    assert "Offspring ranked: False" in report
    assert "Evolution executed: False" in report
    assert "Candidate acceptance executed: False" in report

    print("PASS_REGEN_CANDIDATE_MUTATION_OWNER_PHASE_11B5B")
    return True


if __name__ == "__main__":
    run_test()
