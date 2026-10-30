from regen_adaptive_mutation_controller import (
    attach_regen_adaptive_mutation_controller,
)
from regen_adaptive_mutation_history_owner import (
    attach_regen_adaptive_mutation_history_owner,
)
from regen_adaptive_mutation_report_owner import (
    attach_regen_adaptive_mutation_report_owner,
)
from regen_adaptive_mutation_master_gate import (
    attach_regen_adaptive_mutation_master_gate,
)


def apply_chain(results):
    results = attach_regen_adaptive_mutation_controller(results)
    results = attach_regen_adaptive_mutation_history_owner(results)
    results = attach_regen_adaptive_mutation_report_owner(results)
    results = attach_regen_adaptive_mutation_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_population_diversity_master_gate_ready": True,
        "regen_convergence_monitor_master_gate_ready": True,
        "regen_termination_master_gate_ready": True,
        "regen_termination_decision": "CONTINUE_OPTIMISATION",
        "regen_population_diversity_metrics": {
            "mean_normalised_spread": 0.05,
        },
        "regen_convergence_monitor_metrics": {
            "latest_improvement": 10.0,
        },
        "regen_mutation_strength": 0.05,
    }


def test_adaptive_mutation_stable_refinement():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2a_regen_adaptive_mutation_complete"] is True
    assert results["phase_11b_2a_regen_adaptive_mutation_history_complete"] is True
    assert results["phase_11b_2a_regen_adaptive_mutation_report_complete"] is True
    assert results["phase_11b_2a_regen_adaptive_mutation_master_gate_complete"] is True

    assert results["regen_adaptive_mutation_status"] == (
        "PASS_REGEN_ADAPTIVE_MUTATION_READY"
    )
    assert results["regen_adaptive_mutation_master_gate_status"] == (
        "PASS_REGEN_ADAPTIVE_MUTATION_GATE_READY"
    )
    assert results["regen_adaptive_mutation_mode"] == "STABLE_REFINEMENT"

    assert results["regen_adaptive_mutation_solver_executed"] is False
    assert results["regen_adaptive_mutation_live_geometry_modified"] is False
    assert results["regen_adaptive_mutation_candidate_committed"] is False


def test_adaptive_mutation_increases_when_stagnant_and_low_diversity():
    results = base_ready_results()
    results["regen_population_diversity_metrics"]["mean_normalised_spread"] = 0.005
    results["regen_convergence_monitor_metrics"]["latest_improvement"] = 0.0

    results = apply_chain(results)

    assert results["regen_adaptive_mutation_mode"] == "BROAD_EXPLORATION"
    assert results["regen_adaptive_mutation_strength"] > 0.05


def test_adaptive_mutation_reduces_when_improving_and_broad():
    results = base_ready_results()
    results["regen_population_diversity_metrics"]["mean_normalised_spread"] = 0.20
    results["regen_convergence_monitor_metrics"]["latest_improvement"] = 20.0

    results = apply_chain(results)

    assert results["regen_adaptive_mutation_mode"] == "FOCUSED_EXPLOITATION"
    assert results["regen_adaptive_mutation_strength"] < 0.05


def test_adaptive_mutation_blocks_without_required_gates():
    results = {}

    results = apply_chain(results)

    assert results["regen_adaptive_mutation_ready"] is False
    assert results["regen_adaptive_mutation_master_gate_ready"] is False


if __name__ == "__main__":
    test_adaptive_mutation_stable_refinement()
    test_adaptive_mutation_increases_when_stagnant_and_low_diversity()
    test_adaptive_mutation_reduces_when_improving_and_broad()
    test_adaptive_mutation_blocks_without_required_gates()
    print("PASS_REGEN_ADAPTIVE_MUTATION_CONTROLLER_PHASE_11B2A")