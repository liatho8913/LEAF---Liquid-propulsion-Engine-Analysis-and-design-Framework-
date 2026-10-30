from regen_autonomous_optimisation_completion_audit import (
    attach_regen_autonomous_optimisation_completion_audit,
)
from regen_autonomous_optimisation_completion_history_owner import (
    attach_regen_autonomous_optimisation_completion_history_owner,
)
from regen_autonomous_optimisation_completion_report_owner import (
    attach_regen_autonomous_optimisation_completion_report_owner,
)
from regen_autonomous_optimisation_completion_master_gate import (
    attach_regen_autonomous_optimisation_completion_master_gate,
)


def apply_completion_chain(results):
    results = attach_regen_autonomous_optimisation_completion_audit(results)
    results = attach_regen_autonomous_optimisation_completion_history_owner(results)
    results = attach_regen_autonomous_optimisation_completion_report_owner(results)
    results = attach_regen_autonomous_optimisation_completion_master_gate(results)
    return results


def build_complete_results():
    results = {}

    completion_keys = [
        "regen_generation_builder_complete",
        "regen_generation_validation_complete",
        "regen_generation_scoring_complete",
        "regen_generation_selection_complete",
        "regen_generation_selection_history_complete",
        "regen_generation_selection_report_complete",
        "regen_generation_selection_master_gate_complete",
        "regen_generation_evolution_complete",
        "regen_generation_evolution_history_complete",
        "regen_generation_evolution_master_gate_complete",
        "regen_evolution_loop_complete",
        "regen_evolution_loop_history_complete",
        "regen_evolution_loop_master_gate_complete",
        "regen_generation_persistence_complete",
        "regen_generation_persistence_master_gate_complete",
        "regen_mutation_engine_complete",
        "regen_mutation_history_complete",
        "regen_mutation_report_complete",
        "regen_mutation_master_gate_complete",
        "regen_population_diversity_complete",
        "regen_population_diversity_history_complete",
        "regen_population_diversity_report_complete",
        "regen_population_diversity_master_gate_complete",
        "regen_convergence_monitor_complete",
        "regen_convergence_monitor_history_complete",
        "regen_convergence_monitor_report_complete",
        "regen_convergence_monitor_master_gate_complete",
        "regen_termination_complete",
        "regen_termination_history_complete",
        "regen_termination_report_complete",
        "regen_termination_master_gate_complete",
    ]

    ready_keys = [
        "regen_generation_ready",
        "regen_generation_selection_master_gate_ready",
        "regen_generation_evolution_master_gate_ready",
        "regen_evolution_loop_master_gate_ready",
        "regen_generation_persistence_master_gate_ready",
        "regen_mutation_master_gate_ready",
        "regen_population_diversity_master_gate_ready",
        "regen_convergence_monitor_master_gate_ready",
        "regen_termination_master_gate_ready",
    ]

    false_safety_keys = [
        "regen_generation_solver_executed",
        "regen_generation_live_geometry_modified",
        "regen_generation_candidate_committed",
        "regen_generation_validation_solver_executed",
        "regen_generation_validation_live_geometry_modified",
        "regen_generation_validation_candidate_committed",
        "regen_generation_scoring_solver_executed",
        "regen_generation_scoring_live_geometry_modified",
        "regen_generation_scoring_candidate_committed",
        "regen_generation_selection_solver_executed",
        "regen_generation_selection_live_geometry_modified",
        "regen_generation_selection_candidate_committed",
        "regen_generation_evolution_solver_executed",
        "regen_generation_evolution_live_geometry_modified",
        "regen_generation_evolution_candidate_committed",
        "regen_evolution_loop_solver_executed",
        "regen_evolution_loop_live_geometry_modified",
        "regen_evolution_loop_candidate_committed",
        "regen_generation_persistence_solver_executed",
        "regen_generation_persistence_live_geometry_modified",
        "regen_generation_persistence_candidate_committed",
        "regen_mutation_solver_executed",
        "regen_mutation_live_geometry_modified",
        "regen_mutation_candidate_committed",
        "regen_population_diversity_solver_executed",
        "regen_population_diversity_live_geometry_modified",
        "regen_population_diversity_candidate_committed",
        "regen_convergence_monitor_solver_executed",
        "regen_convergence_monitor_live_geometry_modified",
        "regen_convergence_monitor_candidate_committed",
        "regen_termination_solver_executed",
        "regen_termination_live_geometry_modified",
        "regen_termination_candidate_committed",
    ]

    for key in completion_keys:
        results[key] = True

    for key in ready_keys:
        results[key] = True

    for key in false_safety_keys:
        results[key] = False

    return results


def test_autonomous_optimisation_completion_audit_passes_complete_stack():
    results = apply_completion_chain(build_complete_results())

    assert (
        results[
            "phase_11b_1z_regen_autonomous_optimisation_completion_audit_complete"
        ]
        is True
    )
    assert (
        results[
            "phase_11b_1z_regen_autonomous_optimisation_completion_history_complete"
        ]
        is True
    )
    assert (
        results[
            "phase_11b_1z_regen_autonomous_optimisation_completion_report_complete"
        ]
        is True
    )
    assert (
        results[
            "phase_11b_1z_regen_autonomous_optimisation_completion_master_gate_complete"
        ]
        is True
    )

    assert results["regen_autonomous_optimisation_completion_audit_status"] == (
        "PASS_REGEN_AUTONOMOUS_OPTIMISATION_COMPLETION_AUDIT"
    )
    assert results["regen_autonomous_optimisation_completion_master_gate_status"] == (
        "PASS_REGEN_AUTONOMOUS_OPTIMISATION_COMPLETION_GATE_READY"
    )

    assert results["regen_autonomous_optimisation_foundation_complete"] is True
    assert (
        results["phase_11b_1_autonomous_regen_optimisation_foundation_complete"]
        is True
    )

    assert (
        results["regen_autonomous_optimisation_completion_audit_solver_executed"]
        is False
    )
    assert (
        results[
            "regen_autonomous_optimisation_completion_audit_live_geometry_modified"
        ]
        is False
    )
    assert (
        results[
            "regen_autonomous_optimisation_completion_audit_candidate_committed"
        ]
        is False
    )


def test_autonomous_optimisation_completion_audit_fails_missing_layer():
    results = build_complete_results()
    del results["regen_mutation_master_gate_complete"]

    results = apply_completion_chain(results)

    assert results["regen_autonomous_optimisation_completion_audit_ready"] is False
    assert results["regen_autonomous_optimisation_foundation_complete"] is False
    assert results["regen_autonomous_optimisation_completion_master_gate_ready"] is False
    assert results["regen_autonomous_optimisation_completion_missing_layers"]


def test_autonomous_optimisation_completion_audit_fails_safety_violation():
    results = build_complete_results()
    results["regen_mutation_live_geometry_modified"] = True

    results = apply_completion_chain(results)

    assert results["regen_autonomous_optimisation_completion_audit_ready"] is False
    assert results["regen_autonomous_optimisation_foundation_complete"] is False
    assert results["regen_autonomous_optimisation_completion_safety_violations"]


if __name__ == "__main__":
    test_autonomous_optimisation_completion_audit_passes_complete_stack()
    test_autonomous_optimisation_completion_audit_fails_missing_layer()
    test_autonomous_optimisation_completion_audit_fails_safety_violation()
    print("PASS_REGEN_AUTONOMOUS_OPTIMISATION_COMPLETION_AUDIT_PHASE_11B1Z")