from regen_candidate_population_generation_owner import (
    build_regen_candidate_population_generation_owner,
)
from regen_candidate_population_report_owner import (
    build_regen_candidate_population_report_owner,
)
from regen_candidate_population_registration_owner import (
    build_regen_candidate_population_registration_owner,
)
from regen_candidate_population_completion_audit import (
    build_regen_candidate_population_completion_audit,
)
from regen_candidate_population_master_gate import (
    build_regen_candidate_population_master_gate,
)


def run_test():
    results = {
        "phase_11b_2t_regen_objective_decision_master_gate_complete": True,
        "regen_objective_decision_architecture_complete": True,
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

    assert results["regen_candidate_population_master_gate_complete"] is True
    assert results["phase_11b_3e_regen_candidate_population_master_gate_complete"] is True
    assert results["regen_candidate_population_master_gate_ready"] is True

    assert (
        results["regen_candidate_population_master_gate_status"]
        == "PASS_REGEN_CANDIDATE_POPULATION_MASTER_GATE_PHASE_11B3E"
    )

    assert results["regen_population_master_gate_complete"] is True
    assert results["regen_population_master_gate_ready"] is True

    checks = results["regen_candidate_population_master_gate_checks"]
    failed = results["regen_candidate_population_master_gate_failed_checks"]

    assert isinstance(checks, list)
    assert len(checks) > 0
    assert failed == []

    assert results["regen_candidate_ranking_architecture_allowed"] is True
    assert results["phase_11b_4_candidate_ranking_architecture_allowed"] is True

    assert results["regen_candidate_population_master_gate_ranking_executed"] is False
    assert results["regen_candidate_population_master_gate_mutation_executed"] is False
    assert results["regen_candidate_population_master_gate_solver_executed"] is False
    assert results["regen_candidate_population_master_gate_live_commit_executed"] is False

    assert results["regen_candidate_population_runtime_ranking_allowed"] is False
    assert results["regen_candidate_population_runtime_mutation_allowed"] is False
    assert results["regen_candidate_population_runtime_solver_allowed"] is False
    assert results["regen_candidate_population_runtime_live_commit_allowed"] is False

    report = results["regen_candidate_population_master_gate_report"]

    assert "LEAF PHASE 11B.3E" in report
    assert "11B.4 Candidate Ranking Architecture allowed: True" in report
    assert "Runtime candidate ranking allowed: False" in report
    assert "Failed checks: 0" in report

    print("PASS_REGEN_CANDIDATE_POPULATION_MASTER_GATE_PHASE_11B3E")
    return True


if __name__ == "__main__":
    run_test()
