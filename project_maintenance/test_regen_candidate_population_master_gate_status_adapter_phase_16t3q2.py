from __future__ import annotations

from leaf_qt.regen_candidate_population_master_gate import (
    attach_regen_candidate_population_master_gate_status_adapter,
)


VALID_RESULTS = {
    "regen_candidate_population_master_gate_status": "PASS_REGEN_CANDIDATE_POPULATION_MASTER_GATE",
    "regen_candidate_population_status": "PASS",
    "regen_candidate_population_count": 24,
    "regen_candidate_survivor_count": 12,
    "regen_candidate_population": [{"id": "A"}, {"id": "B"}],
}


def test_phase_16t3q2_valid_population_passes() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_regen_candidate_population_master_gate_status_adapter(data)

    assert returned is data
    assert data["regen_candidate_population_master_gate_status_adapter_status"] == "PASS_REGEN_CANDIDATE_POPULATION_MASTER_GATE_STATUS_ADAPTER"
    assert data["regen_candidate_population_master_gate_global_status"] == "PASS"
    assert data["phase_16t3q2_status_adapter_complete"] is True


def test_phase_16t3q2_adds_structured_findings_and_report() -> None:
    data = dict(VALID_RESULTS)
    attach_regen_candidate_population_master_gate_status_adapter(data)

    assert data["regen_candidate_population_master_gate_structured_findings"]
    assert data["regen_candidate_population_master_gate_global_status_payload"]["passed"] is True
    assert "REGEN CANDIDATE POPULATION MASTER GATE STATUS ADAPTER" in data["regen_candidate_population_master_gate_status_adapter_report"]


def test_phase_16t3q2_warning_status_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["regen_candidate_population_status"] = "WARN_REVIEW_REQUIRED"

    attach_regen_candidate_population_master_gate_status_adapter(data)

    assert data["regen_candidate_population_master_gate_status_adapter_status"] == "WARN_REGEN_CANDIDATE_POPULATION_MASTER_GATE_STATUS_ADAPTER_REVIEW_REQUIRED"
    assert data["regen_candidate_population_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3q2_failure_status_fails_global_status() -> None:
    data = dict(VALID_RESULTS)
    data["regen_candidate_population_status"] = "FAIL_REGEN_CANDIDATE_POPULATION"

    attach_regen_candidate_population_master_gate_status_adapter(data)

    assert data["regen_candidate_population_master_gate_status_adapter_status"] == "FAIL_REGEN_CANDIDATE_POPULATION_MASTER_GATE_STATUS_ADAPTER"
    assert data["regen_candidate_population_master_gate_global_status"] == "FAIL"


def test_phase_16t3q2_missing_population_count_blocks() -> None:
    data = dict(VALID_RESULTS)
    data.pop("regen_candidate_population_count")
    data.pop("regen_candidate_population")

    attach_regen_candidate_population_master_gate_status_adapter(data)

    assert data["regen_candidate_population_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3q2_empty_population_fails() -> None:
    data = dict(VALID_RESULTS)
    data["regen_candidate_population_count"] = 0

    attach_regen_candidate_population_master_gate_status_adapter(data)

    assert data["regen_candidate_population_master_gate_global_status"] == "FAIL"


def test_phase_16t3q2_zero_survivors_blocks_review() -> None:
    data = dict(VALID_RESULTS)
    data["regen_candidate_survivor_count"] = 0

    attach_regen_candidate_population_master_gate_status_adapter(data)

    assert data["regen_candidate_population_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3q2_non_dict_preserved() -> None:
    assert attach_regen_candidate_population_master_gate_status_adapter(None) is None
