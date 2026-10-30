from __future__ import annotations

from leaf_qt.regen_validation_master_gate import (
    attach_regen_validation_master_gate,
    build_regen_validation_master_gate,
)


VALID_RESULTS = {
    "regen_validation_complete": True,
    "regen_validation_status": "PASS_REGEN_VALIDATION_OWNER",
    "regen_validation_mode": "SOURCED_VALIDATION_MODE",
    "regen_sourced_validation_complete": True,
    "regen_placeholder_only": False,
    "regen_partial_source_mode": False,
}


def test_phase_16t3k6_preserves_legacy_pass_contract() -> None:
    payload = build_regen_validation_master_gate(dict(VALID_RESULTS))

    assert payload["regen_validation_master_gate_status"] == "PASS_REGEN_VALIDATION_MASTER_GATE"
    assert payload["regen_validation_master_gate_ready"] is True
    assert payload["regen_validation_master_gate_complete"] is True
    assert payload["phase_11b_1p_regen_validation_master_gate_complete"] is True


def test_phase_16t3k6_adds_structured_findings_and_global_pass() -> None:
    payload = build_regen_validation_master_gate(dict(VALID_RESULTS))

    assert payload["regen_validation_master_gate_structured_findings"]
    assert payload["regen_validation_master_gate_global_status"] == "PASS"
    assert payload["regen_validation_master_gate_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["regen_validation_master_gate_report"]


def test_phase_16t3k6_incomplete_validation_blocks() -> None:
    data = dict(VALID_RESULTS)
    data["regen_validation_complete"] = False

    payload = build_regen_validation_master_gate(data)

    assert payload["regen_validation_master_gate_status"] == "FAIL_REGEN_VALIDATION_MASTER_GATE_INCOMPLETE"
    assert payload["regen_validation_master_gate_ready"] is False
    assert payload["regen_validation_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k6_placeholder_only_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["regen_placeholder_only"] = True
    data["regen_validation_mode"] = "PLACEHOLDER_MODE"

    payload = build_regen_validation_master_gate(data)

    assert payload["regen_validation_master_gate_status"] == "WARN_REGEN_VALIDATION_MASTER_GATE_PLACEHOLDER_ONLY"
    assert payload["regen_validation_master_gate_ready"] is False
    assert payload["regen_validation_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k6_partial_source_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["regen_partial_source_mode"] = True
    data["regen_validation_mode"] = "PARTIAL_SOURCE_MODE"

    payload = build_regen_validation_master_gate(data)

    assert payload["regen_validation_master_gate_status"] == "WARN_REGEN_VALIDATION_MASTER_GATE_PARTIAL_SOURCE_REVIEW"
    assert payload["regen_validation_master_gate_ready"] is False
    assert payload["regen_validation_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k6_failed_validation_maps_to_fail() -> None:
    data = dict(VALID_RESULTS)
    data["regen_validation_status"] = "FAIL_REGEN_VALIDATION_INVALID_GEOMETRY"
    data["regen_validation_mode"] = "SOURCED_VALIDATION_MODE"
    data["regen_sourced_validation_complete"] = False

    payload = build_regen_validation_master_gate(data)

    assert payload["regen_validation_master_gate_status"] == "FAIL_REGEN_VALIDATION_MASTER_GATE_FAILED"
    assert payload["regen_validation_master_gate_ready"] is False
    assert payload["regen_validation_master_gate_global_status"] == "FAIL"


def test_phase_16t3k6_missing_pass_status_blocks() -> None:
    data = dict(VALID_RESULTS)
    data["regen_validation_status"] = "UNKNOWN_REGEN_VALIDATION_STATUS"
    data["regen_validation_mode"] = "UNKNOWN_MODE"
    data["regen_sourced_validation_complete"] = False

    payload = build_regen_validation_master_gate(data)

    assert payload["regen_validation_master_gate_status"] == "FAIL_REGEN_VALIDATION_MASTER_GATE_MISSING_PASS_STATUS"
    assert payload["regen_validation_master_gate_ready"] is False
    assert payload["regen_validation_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k6_attach_preserves_mutating_contract() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_regen_validation_master_gate(data)

    assert returned is data
    assert data["regen_validation_master_gate_status"] == "PASS_REGEN_VALIDATION_MASTER_GATE"
    assert data["regen_validation_master_gate_global_status"] == "PASS"
