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
from regen_candidate_ranking_input_audit import (
    build_regen_candidate_ranking_input_audit,
)
from regen_candidate_ranking_owner import (
    build_regen_candidate_ranking_owner,
)
from regen_candidate_ranking_report_owner import (
    build_regen_candidate_ranking_report_owner,
)
from regen_candidate_ranking_registration_owner import (
    build_regen_candidate_ranking_registration_owner,
)


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

    assert results["regen_candidate_ranking_registration_owner_complete"] is True
    assert results["phase_11b_4d_regen_candidate_ranking_registration_owner_complete"] is True
    assert results["regen_candidate_ranking_registration_ready"] is True

    assert (
        results["regen_candidate_ranking_registration_status"]
        == "PASS_REGEN_CANDIDATE_RANKING_REGISTRATION_OWNER_PHASE_11B4D"
    )

    assert results["regen_candidate_ranking_report_registered"] is True
    assert results["regen_candidate_ranking_report_viewer_registered"] is True
    assert results["regen_candidate_ranking_report_export_registered"] is True

    assert "regen_candidate_ranking_report" in results["regen_candidate_ranking_registered_report_keys"]
    assert "regen_candidate_ranking_report_bundle" in results["regen_candidate_ranking_registered_bundle_keys"]
    assert "regen_candidate_ranking_export" in results["regen_candidate_ranking_registered_export_keys"]

    registry_entry = results["regen_candidate_ranking_registry_entry"]
    report_registry = results["regen_candidate_ranking_report_registry"]
    viewer_registry = results["regen_candidate_ranking_viewer_registry"]
    export_registry = results["regen_candidate_ranking_export_registry"]
    optimisation_registry = results["regen_candidate_ranking_future_optimisation_registry"]

    assert registry_entry["registered"] is True
    assert registry_entry["viewer_visible"] is True
    assert registry_entry["export_visible"] is True
    assert registry_entry["future_optimisation_visible"] is True
    assert registry_entry["mutation_allowed"] is False
    assert registry_entry["evolution_allowed"] is False
    assert registry_entry["solver_allowed"] is False
    assert registry_entry["live_commit_allowed"] is False
    assert registry_entry["candidate_acceptance_allowed"] is False

    assert "regen_candidate_ranking_report" in report_registry["registered_report_keys"]
    assert "regen_candidate_ranking_report" in viewer_registry["viewer_report_keys"]
    assert "regen_candidate_ranking_report" in export_registry["export_report_keys"]

    assert "ranked_population" in optimisation_registry["optimisation_keys"]
    assert "best_ranked_candidate" in optimisation_registry["optimisation_keys"]
    assert "ranking_statistics" in optimisation_registry["optimisation_keys"]

    assert results["regen_candidate_ranking_completion_audit_allowed"] is True
    assert results["phase_11b_4e_candidate_ranking_completion_audit_allowed"] is True
    assert results["regen_candidate_mutation_architecture_allowed"] is False
    assert results["regen_candidate_evolution_architecture_allowed"] is False

    assert results["regen_candidate_ranking_registration_mutation_executed"] is False
    assert results["regen_candidate_ranking_registration_evolution_executed"] is False
    assert results["regen_candidate_ranking_registration_solver_executed"] is False
    assert results["regen_candidate_ranking_registration_live_commit_executed"] is False
    assert results["regen_candidate_ranking_registration_candidate_acceptance_executed"] is False

    report = results["regen_candidate_ranking_registration_report"]

    assert "LEAF PHASE 11B.4D" in report
    assert "Registered Report Keys" in report
    assert "Viewer Report Keys" in report
    assert "Export Report Keys" in report
    assert "Future Optimisation Keys" in report
    assert "Mutation allowed: False" in report
    assert "Evolution allowed: False" in report

    print("PASS_REGEN_CANDIDATE_RANKING_REGISTRATION_OWNER_PHASE_11B4D")
    return True


if __name__ == "__main__":
    run_test()
