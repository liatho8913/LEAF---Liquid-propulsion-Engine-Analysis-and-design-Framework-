from regen_exploration_controller import attach_regen_exploration_controller
from regen_exploration_history_owner import attach_regen_exploration_history_owner
from regen_exploration_report_owner import attach_regen_exploration_report_owner
from regen_exploration_master_gate import attach_regen_exploration_master_gate


def apply_chain(results):
    results = attach_regen_exploration_controller(results)
    results = attach_regen_exploration_history_owner(results)
    results = attach_regen_exploration_report_owner(results)
    results = attach_regen_exploration_master_gate(results)
    return results


def base_ready_results():
    return {
        "regen_adaptive_mutation_master_gate_ready": True,
        "regen_adaptive_diversity_master_gate_ready": True,
        "regen_convergence_monitor_master_gate_ready": True,
        "regen_termination_master_gate_ready": True,
        "regen_adaptive_mutation_mode": "STABLE_REFINEMENT",
        "regen_adaptive_diversity_mode": "DIVERSITY_STABLE",
        "regen_adaptive_diversity_action": "MAINTAIN_CURRENT_DIVERSITY",
        "regen_convergence_monitor_status": (
            "PASS_REGEN_CONVERGENCE_MONITOR_IMPROVING"
        ),
        "regen_termination_decision": "CONTINUE_OPTIMISATION",
        "regen_convergence_monitor_metrics": {
            "latest_improvement": 10.0,
        },
        "regen_population_diversity_metrics": {
            "mean_normalised_spread": 0.05,
        },
    }


def test_exploration_controller_balanced_search():
    results = apply_chain(base_ready_results())

    assert results["phase_11b_2c_regen_exploration_controller_complete"] is True
    assert results["phase_11b_2c_regen_exploration_history_complete"] is True
    assert results["phase_11b_2c_regen_exploration_report_complete"] is True
    assert results["phase_11b_2c_regen_exploration_master_gate_complete"] is True

    assert results["regen_exploration_controller_status"] == (
        "PASS_REGEN_EXPLORATION_CONTROLLER_READY"
    )
    assert results["regen_exploration_master_gate_status"] == (
        "PASS_REGEN_EXPLORATION_GATE_READY"
    )
    assert results["regen_exploration_mode"] == "BALANCED_SEARCH"

    assert results["regen_exploration_solver_executed"] is False
    assert results["regen_exploration_live_geometry_modified"] is False
    assert results["regen_exploration_candidate_committed"] is False


def test_exploration_controller_escape_local_minimum():
    results = base_ready_results()
    results["regen_adaptive_diversity_mode"] = "COLLAPSE_RECOVERY"
    results["regen_adaptive_diversity_action"] = "INJECT_EXPLORATION_CANDIDATES"
    results["regen_population_diversity_metrics"]["mean_normalised_spread"] = 0.0
    results["regen_convergence_monitor_metrics"]["latest_improvement"] = 0.0

    results = apply_chain(results)

    assert results["regen_exploration_mode"] == "ESCAPE_LOCAL_MINIMUM"
    assert results["regen_exploration_action"] == "FORCE_BROAD_EXPLORATION"
    assert results["regen_exploration_pressure"] == 1.0


def test_exploration_controller_locked_when_terminated():
    results = base_ready_results()
    results["regen_termination_decision"] = "TERMINATE_CONVERGED"

    results = apply_chain(results)

    assert results["regen_exploration_mode"] == "SEARCH_LOCKED_TERMINATED"
    assert results["regen_exploration_action"] == "HOLD_FINAL_CANDIDATE"
    assert results["regen_exploration_pressure"] == 0.0


def test_exploration_controller_blocks_without_required_gates():
    results = {}

    results = apply_chain(results)

    assert results["regen_exploration_controller_ready"] is False
    assert results["regen_exploration_master_gate_ready"] is False


if __name__ == "__main__":
    test_exploration_controller_balanced_search()
    test_exploration_controller_escape_local_minimum()
    test_exploration_controller_locked_when_terminated()
    test_exploration_controller_blocks_without_required_gates()
    print("PASS_REGEN_EXPLORATION_CONTROLLER_PHASE_11B2C")