from regen_termination_owner import attach_regen_termination_owner
from regen_termination_history_owner import attach_regen_termination_history_owner
from regen_termination_report_owner import attach_regen_termination_report_owner
from regen_termination_master_gate import attach_regen_termination_master_gate


def apply_termination_chain(results):
    results = attach_regen_termination_owner(results)
    results = attach_regen_termination_history_owner(results)
    results = attach_regen_termination_report_owner(results)
    results = attach_regen_termination_master_gate(results)
    return results


def test_termination_owner_continues_when_improving():
    results = {
        "regen_convergence_monitor_master_gate_ready": True,
        "regen_convergence_monitor_converged": False,
        "regen_evolution_loop_next_action": "BUILD_NEXT_GENERATION",
        "regen_convergence_generation_count": 2,
        "regen_termination_max_generations": 5,
    }

    results = apply_termination_chain(results)

    assert results["phase_11b_1y_regen_termination_complete"] is True
    assert results["phase_11b_1y_regen_termination_history_complete"] is True
    assert results["phase_11b_1y_regen_termination_report_complete"] is True
    assert results["phase_11b_1y_regen_termination_master_gate_complete"] is True

    assert results["regen_termination_status"] == "PASS_REGEN_TERMINATION_CONTINUE"
    assert results["regen_termination_decision"] == "CONTINUE_OPTIMISATION"
    assert results["regen_termination_terminated"] is False
    assert results["regen_termination_master_gate_status"] == (
        "PASS_REGEN_TERMINATION_GATE_READY"
    )

    assert results["regen_termination_solver_executed"] is False
    assert results["regen_termination_live_geometry_modified"] is False
    assert results["regen_termination_candidate_committed"] is False


def test_termination_owner_stops_when_converged():
    results = {
        "regen_convergence_monitor_master_gate_ready": True,
        "regen_convergence_monitor_converged": True,
        "regen_evolution_loop_next_action": "STOP_CONVERGED",
        "regen_convergence_generation_count": 3,
        "regen_termination_max_generations": 5,
    }

    results = apply_termination_chain(results)

    assert results["regen_termination_status"] == "PASS_REGEN_TERMINATION_CONVERGED"
    assert results["regen_termination_decision"] == "TERMINATE_CONVERGED"
    assert results["regen_termination_terminated"] is True
    assert results["regen_optimisation_terminated"] is True
    assert results["regen_optimisation_next_action"] == "STOP"


def test_termination_owner_stops_at_generation_limit():
    results = {
        "regen_convergence_monitor_master_gate_ready": True,
        "regen_convergence_monitor_converged": False,
        "regen_evolution_loop_next_action": "BUILD_NEXT_GENERATION",
        "regen_convergence_generation_count": 5,
        "regen_termination_max_generations": 5,
    }

    results = apply_termination_chain(results)

    assert results["regen_termination_status"] == (
        "WARN_REGEN_TERMINATION_MAX_GENERATIONS"
    )
    assert results["regen_termination_decision"] == "TERMINATE_MAX_GENERATIONS"
    assert results["regen_termination_terminated"] is True


def test_termination_owner_blocks_without_convergence_gate():
    results = {
        "regen_convergence_monitor_master_gate_ready": False,
        "regen_evolution_loop_next_action": "BUILD_NEXT_GENERATION",
    }

    results = apply_termination_chain(results)

    assert results["regen_termination_ready"] is False
    assert results["regen_termination_decision"] == "BLOCKED"
    assert results["regen_termination_master_gate_ready"] is False


if __name__ == "__main__":
    test_termination_owner_continues_when_improving()
    test_termination_owner_stops_when_converged()
    test_termination_owner_stops_at_generation_limit()
    test_termination_owner_blocks_without_convergence_gate()
    print("PASS_REGEN_TERMINATION_OWNER_PHASE_11B1Y")