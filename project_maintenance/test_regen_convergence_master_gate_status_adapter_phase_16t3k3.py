from __future__ import annotations

from leaf_qt.regen_convergence_master_gate import (
    attach_regen_convergence_master_gate,
    build_regen_convergence_master_gate,
)


BASE_RESULTS = {
    "regen_convergence_complete": True,
    "regen_convergence_history_complete": True,
    "regen_convergence_history_status": "PASS_REGEN_CONVERGENCE_HISTORY_STORED",
}


def test_phase_16t3k3_preserves_legacy_converged_contract() -> None:
    payload = build_regen_convergence_master_gate({
        **BASE_RESULTS,
        "regen_convergence_converged": True,
        "regen_convergence_status": "PASS_REGEN_CONVERGENCE",
    })

    assert payload["regen_convergence_master_gate_status"] == "PASS_REGEN_CONVERGENCE_MASTER_GATE_CONVERGED"
    assert payload["regen_convergence_ready"] is True
    assert payload["regen_convergence_master_gate_complete"] is True
    assert payload["phase_11b_1m_regen_convergence_master_gate_complete"] is True


def test_phase_16t3k3_adds_structured_findings_and_global_pass() -> None:
    payload = build_regen_convergence_master_gate({
        **BASE_RESULTS,
        "regen_convergence_converged": True,
        "regen_convergence_status": "PASS_REGEN_CONVERGENCE",
    })

    assert payload["regen_convergence_master_gate_structured_findings"]
    assert payload["regen_convergence_master_gate_global_status"] == "PASS"
    assert payload["regen_convergence_master_gate_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["regen_convergence_master_gate_report"]


def test_phase_16t3k3_running_maps_to_running_not_pass() -> None:
    payload = build_regen_convergence_master_gate({
        **BASE_RESULTS,
        "regen_convergence_converged": False,
        "regen_convergence_status": "WARN_REGEN_CONVERGENCE_RUNNING",
    })

    assert payload["regen_convergence_master_gate_status"] == "WARN_REGEN_CONVERGENCE_MASTER_GATE_RUNNING"
    assert payload["regen_convergence_ready"] is True
    assert payload["regen_convergence_master_gate_global_status"] == "RUNNING"


def test_phase_16t3k3_max_generation_warning_is_blocked_in_production_gate() -> None:
    payload = build_regen_convergence_master_gate({
        **BASE_RESULTS,
        "regen_convergence_converged": False,
        "regen_convergence_status": "WARN_REGEN_CONVERGENCE_MAX_GENERATIONS_REACHED",
    })

    assert payload["regen_convergence_master_gate_status"] == "WARN_REGEN_CONVERGENCE_MASTER_GATE_MAX_GENERATIONS"
    assert payload["regen_convergence_ready"] is True
    assert payload["regen_convergence_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k3_engine_incomplete_maps_to_blocked() -> None:
    payload = build_regen_convergence_master_gate({
        **BASE_RESULTS,
        "regen_convergence_complete": False,
        "regen_convergence_converged": False,
        "regen_convergence_status": None,
    })

    assert payload["regen_convergence_master_gate_status"] == "FAIL_REGEN_CONVERGENCE_MASTER_GATE_ENGINE_INCOMPLETE"
    assert payload["regen_convergence_ready"] is False
    assert payload["regen_convergence_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k3_history_failure_maps_to_blocked() -> None:
    payload = build_regen_convergence_master_gate({
        **BASE_RESULTS,
        "regen_convergence_converged": False,
        "regen_convergence_history_status": "FAIL_REGEN_CONVERGENCE_HISTORY",
        "regen_convergence_status": "PASS_REGEN_CONVERGENCE",
    })

    assert payload["regen_convergence_master_gate_status"] == "FAIL_REGEN_CONVERGENCE_MASTER_GATE_HISTORY_FAILED"
    assert payload["regen_convergence_ready"] is False
    assert payload["regen_convergence_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k3_blocked_convergence_maps_to_fail() -> None:
    payload = build_regen_convergence_master_gate({
        **BASE_RESULTS,
        "regen_convergence_converged": False,
        "regen_convergence_status": "FAIL_REGEN_CONVERGENCE_SOLVER_ERROR",
    })

    assert payload["regen_convergence_master_gate_status"] == "FAIL_REGEN_CONVERGENCE_MASTER_GATE_BLOCKED"
    assert payload["regen_convergence_ready"] is False
    assert payload["regen_convergence_master_gate_global_status"] == "FAIL"


def test_phase_16t3k3_attach_preserves_mutating_contract() -> None:
    data = {
        **BASE_RESULTS,
        "regen_convergence_converged": True,
        "regen_convergence_status": "PASS_REGEN_CONVERGENCE",
    }

    returned = attach_regen_convergence_master_gate(data)

    assert returned is data
    assert data["regen_convergence_master_gate_status"] == "PASS_REGEN_CONVERGENCE_MASTER_GATE_CONVERGED"
    assert data["regen_convergence_master_gate_global_status"] == "PASS"
