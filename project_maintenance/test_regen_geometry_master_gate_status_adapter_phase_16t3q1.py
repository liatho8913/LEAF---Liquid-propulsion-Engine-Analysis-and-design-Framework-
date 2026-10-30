from __future__ import annotations

from leaf_qt.regen_geometry_master_gate import (
    attach_regen_geometry_master_gate_status_adapter,
)


VALID_RESULTS = {
    "regen_geometry_master_gate_status": "PASS_REGEN_GEOMETRY_MASTER_GATE",
    "regen_geometry_status": "PASS",
    "regen_overall_status": "PASS",
    "viewer_channel_geometry_valid": True,
    "viewer_channel_fit_ratio": 0.92,
    "viewer_cooling_coverage": 0.85,
    "hot_gas_wall_thickness": 0.001104,
    "coolant_channel_width": 0.0015,
    "coolant_channel_height": 0.002,
    "number_of_coolant_channels": 80,
}


def test_phase_16t3q1_valid_geometry_master_gate_output_passes() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_regen_geometry_master_gate_status_adapter(data)

    assert returned is data
    assert data["regen_geometry_master_gate_status_adapter_status"] == "PASS_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER"
    assert data["regen_geometry_master_gate_global_status"] == "PASS"
    assert data["phase_16t3q1_status_adapter_complete"] is True


def test_phase_16t3q1_adds_structured_findings_and_report() -> None:
    data = dict(VALID_RESULTS)
    attach_regen_geometry_master_gate_status_adapter(data)

    assert data["regen_geometry_master_gate_structured_findings"]
    assert data["regen_geometry_master_gate_global_status_payload"]["passed"] is True
    assert "REGEN GEOMETRY MASTER GATE STATUS ADAPTER" in data["regen_geometry_master_gate_status_adapter_report"]


def test_phase_16t3q1_warning_status_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["regen_geometry_status"] = "WARN_REVIEW_REQUIRED"

    attach_regen_geometry_master_gate_status_adapter(data)

    assert data["regen_geometry_master_gate_status_adapter_status"] == "WARN_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_REVIEW_REQUIRED"
    assert data["regen_geometry_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3q1_failure_status_fails_global_status() -> None:
    data = dict(VALID_RESULTS)
    data["regen_geometry_status"] = "FAIL_REGEN_GEOMETRY_INVALID"

    attach_regen_geometry_master_gate_status_adapter(data)

    assert data["regen_geometry_master_gate_status_adapter_status"] == "FAIL_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER"
    assert data["regen_geometry_master_gate_global_status"] == "FAIL"


def test_phase_16t3q1_false_geometry_flag_fails() -> None:
    data = dict(VALID_RESULTS)
    data["viewer_channel_geometry_valid"] = False

    attach_regen_geometry_master_gate_status_adapter(data)

    assert data["regen_geometry_master_gate_global_status"] == "FAIL"


def test_phase_16t3q1_negative_wall_thickness_fails() -> None:
    data = dict(VALID_RESULTS)
    data["hot_gas_wall_thickness"] = -0.001

    attach_regen_geometry_master_gate_status_adapter(data)

    assert data["regen_geometry_master_gate_global_status"] == "FAIL"


def test_phase_16t3q1_fit_ratio_above_one_fails() -> None:
    data = dict(VALID_RESULTS)
    data["viewer_channel_fit_ratio"] = 1.1

    attach_regen_geometry_master_gate_status_adapter(data)

    assert data["regen_geometry_master_gate_global_status"] == "FAIL"


def test_phase_16t3q1_low_fit_ratio_blocks_review() -> None:
    data = dict(VALID_RESULTS)
    data["viewer_channel_fit_ratio"] = 0.1

    attach_regen_geometry_master_gate_status_adapter(data)

    assert data["regen_geometry_master_gate_status_adapter_status"] == "WARN_REGEN_GEOMETRY_MASTER_GATE_STATUS_ADAPTER_REVIEW_REQUIRED"
    assert data["regen_geometry_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3q1_zero_channel_count_fails() -> None:
    data = dict(VALID_RESULTS)
    data["number_of_coolant_channels"] = 0

    attach_regen_geometry_master_gate_status_adapter(data)

    assert data["regen_geometry_master_gate_global_status"] == "FAIL"


def test_phase_16t3q1_non_dict_preserved() -> None:
    assert attach_regen_geometry_master_gate_status_adapter(None) is None
