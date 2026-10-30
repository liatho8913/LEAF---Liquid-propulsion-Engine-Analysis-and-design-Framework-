from regen_convergence_monitor import attach_regen_convergence_monitor
from regen_convergence_monitor_history_owner import (
    attach_regen_convergence_monitor_history_owner,
)
from regen_convergence_monitor_report_owner import (
    attach_regen_convergence_monitor_report_owner,
)
from regen_convergence_monitor_master_gate import (
    attach_regen_convergence_monitor_master_gate,
)


def test_convergence_monitor_detects_improvement():
    results = {
        "regen_generation_archive": [
            {
                "generation": 1,
                "winner_id": "RGEN1-0001",
                "winner_score": 100.0,
            },
            {
                "generation": 2,
                "winner_id": "RGEN2-0001",
                "winner_score": 120.0,
            },
        ]
    }

    results = attach_regen_convergence_monitor(results)
    results = attach_regen_convergence_monitor_history_owner(results)
    results = attach_regen_convergence_monitor_report_owner(results)
    results = attach_regen_convergence_monitor_master_gate(results)

    assert results["phase_11b_1x_regen_convergence_monitor_complete"] is True
    assert results["phase_11b_1x_regen_convergence_monitor_history_complete"] is True
    assert results["phase_11b_1x_regen_convergence_monitor_report_complete"] is True
    assert results["phase_11b_1x_regen_convergence_monitor_master_gate_complete"] is True

    assert results["regen_convergence_monitor_status"] == (
        "PASS_REGEN_CONVERGENCE_MONITOR_IMPROVING"
    )
    assert results["regen_convergence_monitor_master_gate_status"] == (
        "PASS_REGEN_CONVERGENCE_MONITOR_GATE_READY"
    )
    assert results["regen_convergence_monitor_converged"] is False
    assert results["regen_convergence_converged"] is False

    metrics = results["regen_convergence_monitor_metrics"]

    assert metrics["record_count"] == 2
    assert metrics["latest_improvement"] == 20.0
    assert metrics["total_improvement"] == 20.0

    assert results["regen_convergence_monitor_solver_executed"] is False
    assert results["regen_convergence_monitor_live_geometry_modified"] is False
    assert results["regen_convergence_monitor_candidate_committed"] is False


def test_convergence_monitor_detects_plateau():
    results = {
        "regen_generation_archive": [
            {
                "generation": 1,
                "winner_id": "RGEN1-0001",
                "winner_score": 100.0,
            },
            {
                "generation": 2,
                "winner_id": "RGEN2-0001",
                "winner_score": 100.0,
            },
        ]
    }

    results = attach_regen_convergence_monitor(results)
    results = attach_regen_convergence_monitor_history_owner(results)
    results = attach_regen_convergence_monitor_report_owner(results)
    results = attach_regen_convergence_monitor_master_gate(results)

    assert results["regen_convergence_monitor_status"] == (
        "WARN_REGEN_CONVERGENCE_MONITOR_PLATEAU_DETECTED"
    )
    assert results["regen_convergence_monitor_converged"] is True
    assert results["regen_convergence_converged"] is True
    assert results["regen_convergence_monitor_master_gate_ready"] is True


def test_convergence_monitor_blocks_without_archive():
    results = {}

    results = attach_regen_convergence_monitor(results)
    results = attach_regen_convergence_monitor_history_owner(results)
    results = attach_regen_convergence_monitor_report_owner(results)
    results = attach_regen_convergence_monitor_master_gate(results)

    assert results["regen_convergence_monitor_ready"] is False
    assert results["regen_convergence_monitor_master_gate_ready"] is False


if __name__ == "__main__":
    test_convergence_monitor_detects_improvement()
    test_convergence_monitor_detects_plateau()
    test_convergence_monitor_blocks_without_archive()
    print("PASS_REGEN_CONVERGENCE_MONITOR_PHASE_11B1X")