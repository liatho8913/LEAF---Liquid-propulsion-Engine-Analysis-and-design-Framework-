from __future__ import annotations

from leaf_qt.regen_optimisation_narrative_master_gate import (
    attach_regen_optimisation_narrative_master_gate,
    build_regen_optimisation_narrative_master_gate,
)


VALID_RESULTS = {
    "regen_optimisation_narrative_owner_complete": True,
    "regen_optimisation_proof_owner_complete": True,
    "regen_optimisation_narrative_status": "PASS_REGEN_OPTIMISATION_NARRATIVE_OWNER",
    "regen_optimisation_proof_status": "PASS_REGEN_OPTIMISATION_PROOF_OWNER",
    "regen_optimisation_narrative": "Candidate improved wall margin while preserving channel fit.",
    "regen_optimisation_proof_payload": {
        "attempt": 1,
        "decision": "ACCEPT",
        "reason": "Improved validation margin.",
    },
}


def test_phase_16t3k5_preserves_legacy_pass_contract() -> None:
    payload = build_regen_optimisation_narrative_master_gate(dict(VALID_RESULTS))

    assert payload["regen_optimisation_narrative_master_gate_status"] == "PASS_REGEN_OPTIMISATION_NARRATIVE_MASTER_GATE"
    assert payload["regen_optimisation_narrative_master_gate_ready"] is True
    assert payload["regen_optimisation_narrative_master_gate_complete"] is True
    assert payload["phase_11b_1o_regen_optimisation_narrative_master_gate_complete"] is True


def test_phase_16t3k5_adds_structured_findings_and_global_pass() -> None:
    payload = build_regen_optimisation_narrative_master_gate(dict(VALID_RESULTS))

    assert payload["regen_optimisation_narrative_master_gate_structured_findings"]
    assert payload["regen_optimisation_narrative_master_gate_global_status"] == "PASS"
    assert payload["regen_optimisation_narrative_master_gate_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["regen_optimisation_narrative_master_gate_report"]


def test_phase_16t3k5_narrative_owner_incomplete_blocks() -> None:
    data = dict(VALID_RESULTS)
    data["regen_optimisation_narrative_owner_complete"] = False

    payload = build_regen_optimisation_narrative_master_gate(data)

    assert payload["regen_optimisation_narrative_master_gate_status"] == "FAIL_REGEN_OPTIMISATION_NARRATIVE_MASTER_GATE_NARRATIVE_INCOMPLETE"
    assert payload["regen_optimisation_narrative_master_gate_ready"] is False
    assert payload["regen_optimisation_narrative_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k5_proof_owner_incomplete_blocks() -> None:
    data = dict(VALID_RESULTS)
    data["regen_optimisation_proof_owner_complete"] = False

    payload = build_regen_optimisation_narrative_master_gate(data)

    assert payload["regen_optimisation_narrative_master_gate_status"] == "FAIL_REGEN_OPTIMISATION_NARRATIVE_MASTER_GATE_PROOF_INCOMPLETE"
    assert payload["regen_optimisation_narrative_master_gate_ready"] is False
    assert payload["regen_optimisation_narrative_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k5_bad_narrative_status_blocks() -> None:
    data = dict(VALID_RESULTS)
    data["regen_optimisation_narrative_status"] = "WARN_REGEN_OPTIMISATION_NARRATIVE_REVIEW"

    payload = build_regen_optimisation_narrative_master_gate(data)

    assert payload["regen_optimisation_narrative_master_gate_status"] == "FAIL_REGEN_OPTIMISATION_NARRATIVE_MASTER_GATE_NARRATIVE_MISSING"
    assert payload["regen_optimisation_narrative_master_gate_ready"] is False
    assert payload["regen_optimisation_narrative_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k5_malformed_payload_fails() -> None:
    data = dict(VALID_RESULTS)
    data["regen_optimisation_narrative"] = ""
    data["regen_optimisation_proof_payload"] = {}
    data.pop("regen_optimisation_narrative_report", None)

    payload = build_regen_optimisation_narrative_master_gate(data)

    assert payload["regen_optimisation_narrative_master_gate_status"] == "FAIL_REGEN_OPTIMISATION_NARRATIVE_MASTER_GATE_MALFORMED_PAYLOAD"
    assert payload["regen_optimisation_narrative_master_gate_ready"] is False
    assert payload["regen_optimisation_narrative_master_gate_global_status"] == "FAIL"


def test_phase_16t3k5_attach_preserves_mutating_contract() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_regen_optimisation_narrative_master_gate(data)

    assert returned is data
    assert data["regen_optimisation_narrative_master_gate_status"] == "PASS_REGEN_OPTIMISATION_NARRATIVE_MASTER_GATE"
    assert data["regen_optimisation_narrative_master_gate_global_status"] == "PASS"
