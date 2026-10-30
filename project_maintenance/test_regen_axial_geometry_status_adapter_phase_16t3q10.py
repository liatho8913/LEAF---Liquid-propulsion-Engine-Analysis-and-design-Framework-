from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(LEAF_QT) not in sys.path:
    sys.path.insert(0, str(LEAF_QT))

from project_maintenance.production_historical_artifacts.leaf_qt.regen_axial_geometry_master_gate import (
    run_regen_axial_geometry_master_gate,
    _leaf_16t3q10_original_run_regen_axial_geometry_master_gate,
    flatten_regen_axial_master_gate_result,
)


ADAPTER_STATUS = "PASS_REGEN_AXIAL_GEOMETRY_STATUS_ADAPTER_PHASE_16T3Q10"


def assert_adapter_payload(payload):
    assert payload["phase_16t3q10_status_adapter_complete"] is True
    assert payload["phase_16t3q10_regen_axial_geometry_status_adapter_complete"] is True
    assert payload["regen_axial_geometry_status_adapter_complete"] is True
    assert payload["regen_axial_geometry_status_adapter_status"] == ADAPTER_STATUS

    assert isinstance(payload["regen_axial_geometry_master_gate_structured_findings"], list)
    assert isinstance(payload["regen_axial_geometry_master_gate_global_status"], str)
    assert isinstance(payload["regen_axial_geometry_master_gate_global_status_payload"], dict)
    assert isinstance(payload["regen_axial_geometry_master_gate_adapter_report"], str)

    assert payload["structured_findings"] == payload["regen_axial_geometry_master_gate_structured_findings"]
    assert payload["global_status"] == payload["regen_axial_geometry_master_gate_global_status"]
    assert payload["global_status_payload"] == payload["regen_axial_geometry_master_gate_global_status_payload"]
    assert payload["adapter_report"] == payload["regen_axial_geometry_master_gate_adapter_report"]

    report = payload["regen_axial_geometry_master_gate_adapter_report"]
    assert "LEAF PHASE 16T.3Q.10 STATUS ADAPTER" in report
    assert "Compatibility:" in report


def test_adapter_fields_added_without_removing_original_payload_fields():
    original = _leaf_16t3q10_original_run_regen_axial_geometry_master_gate()
    adapted = run_regen_axial_geometry_master_gate()

    assert isinstance(original, dict)
    assert isinstance(adapted, dict)

    for key in original:
        assert key in adapted, key
        assert adapted[key] == original[key], key

    assert_adapter_payload(adapted)


def test_gate_emits_structured_status():
    payload = run_regen_axial_geometry_master_gate()

    assert_adapter_payload(payload)

    assert payload["regen_axial_geometry_master_gate_global_status"] in {
        "FAIL",
        "REVIEW_REQUIRED",
        "BLOCKED",
        "PASS",
    }

    assert payload["regen_axial_geometry_master_gate_structured_findings"]


def test_global_status_payload_shape():
    payload = run_regen_axial_geometry_master_gate()

    assert_adapter_payload(payload)

    gsp = payload["regen_axial_geometry_master_gate_global_status_payload"]

    assert gsp["owner"] == "regen_axial_geometry_master_gate"
    assert gsp["phase"] == "16T.3Q.10"
    assert gsp["adapter"] == "wave_2_status_adapter"
    assert gsp["adapter_phase"] == "16T.3Q.10"
    assert isinstance(gsp["severity_counts"], dict)
    assert isinstance(gsp["findings"], list)


def test_flatten_helper_still_works_with_adapted_payload():
    payload = run_regen_axial_geometry_master_gate()
    flat = flatten_regen_axial_master_gate_result(payload)

    assert isinstance(flat, dict)
    assert flat


def run_all():
    test_adapter_fields_added_without_removing_original_payload_fields()
    test_gate_emits_structured_status()
    test_global_status_payload_shape()
    test_flatten_helper_still_works_with_adapted_payload()

    print("PASS_REGEN_AXIAL_GEOMETRY_STATUS_ADAPTER_PHASE_16T3Q10")
    return True


if __name__ == "__main__":
    run_all()
