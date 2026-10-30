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

    assert results["regen_candidate_population_completion_audit_complete"] is True
    assert results["phase_11b_3d_regen_candidate_population_completion_audit_complete"] is True
    assert results["regen_candidate_population_completion_audit_ready"] is True

    assert (
        results["regen_candidate_population_completion_audit_status"]
        == "PASS_REGEN_CANDIDATE_POPULATION_COMPLETION_AUDIT_PHASE_11B3D"
    )

    assert results["regen_population_completion_audit_complete"] is True
    assert results["regen_population_completion_audit_ready"] is True

    checks = results["regen_candidate_population_completion_audit_checks"]
    failed = results["regen_candidate_population_completion_audit_failed_checks"]

    assert isinstance(checks, list)
    assert len(checks) > 0
    assert failed == []

    report = results["regen_candidate_population_completion_audit_report"]

    assert "LEAF PHASE 11B.3D" in report
    assert "Total checks:" in report
    assert "Failed checks: 0" in report
    assert "Audit Checks:" in report

    assert results["regen_candidate_population_completion_audit_ranking_allowed"] is False
    assert results["regen_candidate_population_completion_audit_mutation_allowed"] is False
    assert results["regen_candidate_population_completion_audit_solver_allowed"] is False
    assert results["regen_candidate_population_completion_audit_live_commit_allowed"] is False

    print("PASS_REGEN_CANDIDATE_POPULATION_COMPLETION_AUDIT_PHASE_11B3D")
    return True


if __name__ == "__main__":
    run_test()
