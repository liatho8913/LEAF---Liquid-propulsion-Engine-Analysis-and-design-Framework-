from regen_candidate_population_generation_owner import (
    build_regen_candidate_population_generation_owner,
)
from regen_candidate_population_report_owner import (
    build_regen_candidate_population_report_owner,
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

    assert results["regen_candidate_population_report_owner_complete"] is True
    assert results["phase_11b_3b_regen_candidate_population_report_owner_complete"] is True

    assert (
        results["regen_candidate_population_report_owner_status"]
        == "PASS_REGEN_CANDIDATE_POPULATION_REPORT_OWNER_PHASE_11B3B"
    )

    bundle = results["regen_candidate_population_report_bundle"]

    assert bundle["report_key"] == "regen_candidate_population_report"
    assert bundle["owner"] == "REGEN_CANDIDATE_POPULATION_REPORT_OWNER"
    assert bundle["phase"] == "11B.3B"
    assert bundle["complete"] is True
    assert bundle["population_count"] == 16
    assert bundle["architecture"]["report_owner_complete"] is True
    assert bundle["architecture"]["registration_owner_complete"] is False
    assert bundle["architecture"]["completion_audit_complete"] is False
    assert bundle["architecture"]["master_gate_complete"] is False
    assert bundle["architecture"]["ranking_allowed"] is False
    assert bundle["architecture"]["mutation_allowed"] is False

    report = results["regen_candidate_population_report"]

    assert "LEAF PHASE 11B.3B" in report
    assert "Candidate Geometry Table" in report
    assert "Safety Locks" in report
    assert "Ranking allowed: False" in report
    assert "Mutation allowed: False" in report

    assert results["regen_candidate_population_report_ranking_allowed"] is False
    assert results["regen_candidate_population_report_mutation_allowed"] is False
    assert results["regen_candidate_population_report_solver_allowed"] is False
    assert results["regen_candidate_population_report_live_commit_allowed"] is False

    print("PASS_REGEN_CANDIDATE_POPULATION_REPORT_OWNER_PHASE_11B3B")
    return True


if __name__ == "__main__":
    run_test()
