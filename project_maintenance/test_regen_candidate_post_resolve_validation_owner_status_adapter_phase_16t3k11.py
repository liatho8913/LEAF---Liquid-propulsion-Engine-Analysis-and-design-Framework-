from __future__ import annotations

from leaf_qt.regen_candidate_post_resolve_validation_owner import (
    attach_regen_candidate_post_resolve_validation_owner,
    build_regen_candidate_post_resolve_validation_owner,
)


VALID_RESULTS = {
    "candidate_id": "RPOP-G0-0001",
    "regen_candidate_resolved": True,
    "winner_selected": True,
    "post_resolve_geometry_valid": True,
    "post_resolve_solver_valid": True,
    "regen_validation_master_gate_status": "PASS_REGEN_VALIDATION_MASTER_GATE",
    "regen_geometry_status": "PASS",
    "regen_overall_status": "PASS",
    "viewer_channel_fit_ratio": 0.92,
    "hot_gas_wall_thickness": 0.0011,
    "coolant_channel_width": 0.0015,
    "coolant_channel_height": 0.002,
}


def test_phase_16t3k11_preserves_legacy_pass_contract() -> None:
    payload = build_regen_candidate_post_resolve_validation_owner(dict(VALID_RESULTS))

    assert payload["regen_candidate_post_resolve_validation_owner_status"] == "PASS_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    assert payload["regen_candidate_post_resolve_validation_owner_complete"] is True
    assert payload["regen_candidate_post_resolve_validation_pass"] is True
    assert payload["phase_16t3k11_status_adapter_complete"] is True


def test_phase_16t3k11_adds_structured_findings_and_global_pass() -> None:
    payload = build_regen_candidate_post_resolve_validation_owner(dict(VALID_RESULTS))

    assert payload["regen_candidate_post_resolve_validation_structured_findings"]
    assert payload["regen_candidate_post_resolve_validation_global_status"] == "PASS"
    assert payload["regen_candidate_post_resolve_validation_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["regen_candidate_post_resolve_validation_report"]


def test_phase_16t3k11_unresolved_candidate_blocks() -> None:
    data = dict(VALID_RESULTS)
    data["regen_candidate_resolved"] = False

    payload = build_regen_candidate_post_resolve_validation_owner(data)

    assert payload["regen_candidate_post_resolve_validation_owner_status"] == "FAIL_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    assert payload["regen_candidate_post_resolve_validation_pass"] is False
    assert payload["regen_candidate_post_resolve_validation_global_status"] == "BLOCKED"


def test_phase_16t3k11_invalid_geometry_fails() -> None:
    data = dict(VALID_RESULTS)
    data["post_resolve_geometry_valid"] = False

    payload = build_regen_candidate_post_resolve_validation_owner(data)

    assert payload["regen_candidate_post_resolve_validation_owner_status"] == "FAIL_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    assert payload["regen_candidate_post_resolve_validation_global_status"] == "FAIL"


def test_phase_16t3k11_failed_status_fails() -> None:
    data = dict(VALID_RESULTS)
    data["regen_overall_status"] = "FAIL"

    payload = build_regen_candidate_post_resolve_validation_owner(data)

    assert payload["regen_candidate_post_resolve_validation_owner_status"] == "FAIL_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    assert payload["regen_candidate_post_resolve_validation_global_status"] == "FAIL"


def test_phase_16t3k11_warning_status_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["regen_overall_status"] = "WARN_REVIEW_REQUIRED"

    payload = build_regen_candidate_post_resolve_validation_owner(data)

    assert payload["regen_candidate_post_resolve_validation_owner_status"] == "PASS_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    assert payload["regen_candidate_post_resolve_validation_pass"] is True
    assert payload["regen_candidate_post_resolve_validation_global_status"] == "BLOCKED"


def test_phase_16t3k11_fit_ratio_above_one_fails() -> None:
    data = dict(VALID_RESULTS)
    data["viewer_channel_fit_ratio"] = 1.15

    payload = build_regen_candidate_post_resolve_validation_owner(data)

    assert payload["regen_candidate_post_resolve_validation_owner_status"] == "FAIL_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    assert payload["regen_candidate_post_resolve_validation_global_status"] == "FAIL"


def test_phase_16t3k11_negative_geometry_value_fails() -> None:
    data = dict(VALID_RESULTS)
    data["coolant_channel_width"] = -0.001

    payload = build_regen_candidate_post_resolve_validation_owner(data)

    assert payload["regen_candidate_post_resolve_validation_owner_status"] == "FAIL_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    assert payload["regen_candidate_post_resolve_validation_global_status"] == "FAIL"


def test_phase_16t3k11_attach_preserves_mutating_contract() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_regen_candidate_post_resolve_validation_owner(data)

    assert returned is data
    assert data["regen_candidate_post_resolve_validation_owner_status"] == "PASS_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    assert data["regen_candidate_post_resolve_validation_global_status"] == "PASS"


def test_phase_16t3k11_non_dict_attach_preserves_input() -> None:
    assert attach_regen_candidate_post_resolve_validation_owner(None) is None
