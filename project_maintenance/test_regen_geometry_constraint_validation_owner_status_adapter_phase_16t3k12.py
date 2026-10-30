from __future__ import annotations

from leaf_qt.regen_geometry_constraint_validation_owner import (
    attach_regen_geometry_constraint_validation_owner,
    build_regen_geometry_constraint_validation_owner,
)


VALID_RESULTS = {
    "hot_gas_wall_thickness": 0.001104,
    "coolant_channel_width": 0.0015,
    "coolant_channel_height": 0.002,
    "rib_width": 0.001,
    "number_of_coolant_channels": 80,
    "viewer_channel_fit_ratio": 0.92,
    "viewer_cooling_coverage": 0.85,
    "viewer_channel_geometry_valid": True,
    "regen_geometry_status": "PASS",
    "regen_overall_status": "PASS",
}


def test_phase_16t3k12_preserves_legacy_pass_contract() -> None:
    payload = build_regen_geometry_constraint_validation_owner(dict(VALID_RESULTS))

    assert payload["regen_geometry_constraint_validation_owner_status"] == "PASS_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert payload["regen_geometry_constraint_validation_owner_complete"] is True
    assert payload["regen_geometry_constraint_validation_pass"] is True
    assert payload["phase_16t3k12_status_adapter_complete"] is True


def test_phase_16t3k12_adds_structured_findings_and_global_pass() -> None:
    payload = build_regen_geometry_constraint_validation_owner(dict(VALID_RESULTS))

    assert payload["regen_geometry_constraint_validation_structured_findings"]
    assert payload["regen_geometry_constraint_validation_global_status"] == "PASS"
    assert payload["regen_geometry_constraint_validation_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["regen_geometry_constraint_validation_report"]


def test_phase_16t3k12_missing_geometry_blocks() -> None:
    data = dict(VALID_RESULTS)
    data.pop("coolant_channel_width")

    payload = build_regen_geometry_constraint_validation_owner(data)

    assert payload["regen_geometry_constraint_validation_owner_status"] == "FAIL_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert payload["regen_geometry_constraint_validation_pass"] is False
    assert payload["regen_geometry_constraint_validation_global_status"] == "BLOCKED"


def test_phase_16t3k12_negative_wall_thickness_fails() -> None:
    data = dict(VALID_RESULTS)
    data["hot_gas_wall_thickness"] = -0.001

    payload = build_regen_geometry_constraint_validation_owner(data)

    assert payload["regen_geometry_constraint_validation_owner_status"] == "FAIL_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert payload["regen_geometry_constraint_validation_global_status"] == "FAIL"


def test_phase_16t3k12_zero_channel_count_fails() -> None:
    data = dict(VALID_RESULTS)
    data["number_of_coolant_channels"] = 0

    payload = build_regen_geometry_constraint_validation_owner(data)

    assert payload["regen_geometry_constraint_validation_owner_status"] == "FAIL_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert payload["regen_geometry_constraint_validation_global_status"] == "FAIL"


def test_phase_16t3k12_non_integer_channel_count_fails() -> None:
    data = dict(VALID_RESULTS)
    data["number_of_coolant_channels"] = 80.5

    payload = build_regen_geometry_constraint_validation_owner(data)

    assert payload["regen_geometry_constraint_validation_owner_status"] == "FAIL_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert payload["regen_geometry_constraint_validation_global_status"] == "FAIL"


def test_phase_16t3k12_fit_ratio_above_one_fails() -> None:
    data = dict(VALID_RESULTS)
    data["viewer_channel_fit_ratio"] = 1.15

    payload = build_regen_geometry_constraint_validation_owner(data)

    assert payload["regen_geometry_constraint_validation_owner_status"] == "FAIL_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert payload["regen_geometry_constraint_validation_global_status"] == "FAIL"


def test_phase_16t3k12_low_fit_ratio_warning_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["viewer_channel_fit_ratio"] = 0.1

    payload = build_regen_geometry_constraint_validation_owner(data)

    assert payload["regen_geometry_constraint_validation_owner_status"] == "PASS_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert payload["regen_geometry_constraint_validation_pass"] is True
    assert payload["regen_geometry_constraint_validation_global_status"] == "BLOCKED"


def test_phase_16t3k12_warning_status_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["regen_geometry_status"] = "WARN_REVIEW_REQUIRED"

    payload = build_regen_geometry_constraint_validation_owner(data)

    assert payload["regen_geometry_constraint_validation_owner_status"] == "PASS_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert payload["regen_geometry_constraint_validation_pass"] is True
    assert payload["regen_geometry_constraint_validation_global_status"] == "BLOCKED"


def test_phase_16t3k12_attach_preserves_mutating_contract() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_regen_geometry_constraint_validation_owner(data)

    assert returned is data
    assert data["regen_geometry_constraint_validation_owner_status"] == "PASS_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    assert data["regen_geometry_constraint_validation_global_status"] == "PASS"


def test_phase_16t3k12_non_dict_attach_preserves_input() -> None:
    assert attach_regen_geometry_constraint_validation_owner(None) is None
