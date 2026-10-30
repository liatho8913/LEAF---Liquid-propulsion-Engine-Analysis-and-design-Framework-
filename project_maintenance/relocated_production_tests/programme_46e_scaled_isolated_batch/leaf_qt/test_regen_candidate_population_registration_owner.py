from regen_candidate_population_generation_owner import (
    build_regen_candidate_population_generation_owner,
)
from regen_candidate_population_report_owner import (
    build_regen_candidate_population_report_owner,
)
from regen_candidate_population_registration_owner import (
    build_regen_candidate_population_registration_owner,
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

    assert results["regen_candidate_population_registration_owner_complete"] is True
    assert results["phase_11b_3c_regen_candidate_population_registration_owner_complete"] is True
    assert results["regen_candidate_population_registration_ready"] is True

    assert (
        results["regen_candidate_population_registration_status"]
        == "PASS_REGEN_CANDIDATE_POPULATION_REGISTRATION_OWNER_PHASE_11B3C"
    )

    assert (
        "regen_candidate_population_report"
        in results["regen_candidate_population_registered_report_keys"]
    )

    assert (
        "regen_candidate_population_report_bundle"
        in results["regen_candidate_population_registered_bundle_keys"]
    )

    report_registry = results["regen_candidate_population_report_registry"]
    viewer_registry = results["regen_candidate_population_viewer_registry"]
    export_registry = results["regen_candidate_population_export_registry"]

    assert "regen_candidate_population_report" in report_registry["registered_report_keys"]
    assert "regen_candidate_population_report" in viewer_registry["viewer_report_keys"]
    assert "regen_candidate_population_report" in export_registry["export_report_keys"]

    entry = results["regen_candidate_population_registry_entry"]

    assert entry["registered"] is True
    assert entry["viewer_visible"] is True
    assert entry["export_visible"] is True
    assert entry["ranking_allowed"] is False
    assert entry["mutation_allowed"] is False
    assert entry["candidate_solving_allowed"] is False
    assert entry["live_commit_allowed"] is False

    registration_report = results["regen_candidate_population_registration_report"]

    assert "LEAF PHASE 11B.3C" in registration_report
    assert "Registered Report Keys" in registration_report
    assert "Viewer Report Keys" in registration_report
    assert "Export Report Keys" in registration_report
    assert "Safety Locks" in registration_report

    assert results["regen_candidate_population_registration_ranking_allowed"] is False
    assert results["regen_candidate_population_registration_mutation_allowed"] is False
    assert results["regen_candidate_population_registration_solver_allowed"] is False
    assert results["regen_candidate_population_registration_live_commit_allowed"] is False

    print("PASS_REGEN_CANDIDATE_POPULATION_REGISTRATION_OWNER_PHASE_11B3C")
    return True


if __name__ == "__main__":
    run_test()
