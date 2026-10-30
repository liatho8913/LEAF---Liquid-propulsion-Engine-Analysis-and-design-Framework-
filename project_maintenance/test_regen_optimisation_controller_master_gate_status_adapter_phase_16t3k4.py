from __future__ import annotations

from leaf_qt.regen_optimisation_controller_master_gate import (
    attach_regen_optimisation_controller_master_gate,
    build_regen_optimisation_controller_master_gate,
)


BASE_RESULTS = {
    "regen_optimisation_controller_complete": True,
    "regen_optimisation_history_complete": True,
    "regen_optimisation_history_status": "PASS_REGEN_OPTIMISATION_HISTORY_STORED",
    "regen_optimisation_controller_status": "PASS_REGEN_OPTIMISATION_CONTROLLER",
}


def test_phase_16t3k4_preserves_legacy_converged_contract() -> None:
    payload = build_regen_optimisation_controller_master_gate({
        **BASE_RESULTS,
        "regen_optimisation_next_action": "STOP_CONVERGED",
    })

    assert payload["regen_optimisation_master_gate_status"] == "PASS_REGEN_OPTIMISATION_MASTER_GATE_CONVERGED"
    assert payload["regen_optimisation_master_gate_ready"] is True
    assert payload["regen_optimisation_master_gate_complete"] is True
    assert payload["phase_11b_1n_regen_optimisation_master_gate_complete"] is True


def test_phase_16t3k4_adds_structured_findings_and_global_pass() -> None:
    payload = build_regen_optimisation_controller_master_gate({
        **BASE_RESULTS,
        "regen_optimisation_next_action": "STOP_CONVERGED",
    })

    assert payload["regen_optimisation_master_gate_structured_findings"]
    assert payload["regen_optimisation_master_gate_global_status"] == "PASS"
    assert payload["regen_optimisation_master_gate_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["regen_optimisation_master_gate_report"]


def test_phase_16t3k4_next_generation_maps_to_running_not_pass() -> None:
    payload = build_regen_optimisation_controller_master_gate({
        **BASE_RESULTS,
        "regen_optimisation_next_action": "GENERATE_NEXT_GENERATION",
    })

    assert payload["regen_optimisation_master_gate_status"] == "WARN_REGEN_OPTIMISATION_MASTER_GATE_NEXT_GENERATION_READY"
    assert payload["regen_optimisation_master_gate_ready"] is True
    assert payload["regen_optimisation_master_gate_global_status"] == "RUNNING"


def test_phase_16t3k4_waiting_warning_blocks_production_gate() -> None:
    payload = build_regen_optimisation_controller_master_gate({
        **BASE_RESULTS,
        "regen_optimisation_next_action": "WAIT_FOR_INPUT",
    })

    assert payload["regen_optimisation_master_gate_status"] == "WARN_REGEN_OPTIMISATION_MASTER_GATE_WAITING"
    assert payload["regen_optimisation_master_gate_ready"] is False
    assert payload["regen_optimisation_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k4_controller_incomplete_maps_to_blocked() -> None:
    payload = build_regen_optimisation_controller_master_gate({
        **BASE_RESULTS,
        "regen_optimisation_controller_complete": False,
        "regen_optimisation_next_action": None,
    })

    assert payload["regen_optimisation_master_gate_status"] == "FAIL_REGEN_OPTIMISATION_MASTER_GATE_CONTROLLER_INCOMPLETE"
    assert payload["regen_optimisation_master_gate_ready"] is False
    assert payload["regen_optimisation_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k4_history_failure_maps_to_blocked() -> None:
    payload = build_regen_optimisation_controller_master_gate({
        **BASE_RESULTS,
        "regen_optimisation_history_status": "FAIL_REGEN_OPTIMISATION_HISTORY",
        "regen_optimisation_next_action": "STOP_CONVERGED",
    })

    assert payload["regen_optimisation_master_gate_status"] == "FAIL_REGEN_OPTIMISATION_MASTER_GATE_HISTORY_FAILED"
    assert payload["regen_optimisation_master_gate_ready"] is False
    assert payload["regen_optimisation_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k4_controller_blocked_maps_to_fail() -> None:
    payload = build_regen_optimisation_controller_master_gate({
        **BASE_RESULTS,
        "regen_optimisation_controller_status": "FAIL_REGEN_OPTIMISATION_CONTROLLER_BLOCKED",
        "regen_optimisation_next_action": "STOP_CONVERGED",
    })

    assert payload["regen_optimisation_master_gate_status"] == "FAIL_REGEN_OPTIMISATION_MASTER_GATE_BLOCKED"
    assert payload["regen_optimisation_master_gate_ready"] is False
    assert payload["regen_optimisation_master_gate_global_status"] == "FAIL"


def test_phase_16t3k4_attach_preserves_mutating_contract() -> None:
    data = {
        **BASE_RESULTS,
        "regen_optimisation_next_action": "STOP_CONVERGED",
    }

    returned = attach_regen_optimisation_controller_master_gate(data)

    assert returned is data
    assert data["regen_optimisation_master_gate_status"] == "PASS_REGEN_OPTIMISATION_MASTER_GATE_CONVERGED"
    assert data["regen_optimisation_master_gate_global_status"] == "PASS"
