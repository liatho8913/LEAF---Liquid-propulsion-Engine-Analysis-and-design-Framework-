from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(LEAF_QT) not in sys.path:
    sys.path.insert(0, str(LEAF_QT))

from regen_scalability_master_gate import (
    evaluate_regen_scalability_master_gate,
    _leaf_16t3q7_original_evaluate_regen_scalability_master_gate,
)


ADAPTER_STATUS = "PASS_REGEN_SCALABILITY_STATUS_ADAPTER_PHASE_16T3Q7"


def assert_adapter_payload(payload):
    assert payload["phase_16t3q7_status_adapter_complete"] is True
    assert payload["phase_16t3q7_regen_scalability_status_adapter_complete"] is True
    assert payload["regen_scalability_status_adapter_complete"] is True
    assert payload["regen_scalability_status_adapter_status"] == ADAPTER_STATUS

    assert isinstance(payload["regen_scalability_master_gate_structured_findings"], list)
    assert isinstance(payload["regen_scalability_master_gate_global_status"], str)
    assert isinstance(payload["regen_scalability_master_gate_global_status_payload"], dict)
    assert isinstance(payload["regen_scalability_master_gate_adapter_report"], str)

    assert payload["structured_findings"] == payload["regen_scalability_master_gate_structured_findings"]
    assert payload["global_status"] == payload["regen_scalability_master_gate_global_status"]
    assert payload["global_status_payload"] == payload["regen_scalability_master_gate_global_status_payload"]
    assert payload["adapter_report"] == payload["regen_scalability_master_gate_adapter_report"]

    report = payload["regen_scalability_master_gate_adapter_report"]
    assert "LEAF PHASE 16T.3Q.7 STATUS ADAPTER" in report
    assert "Compatibility:" in report


def test_adapter_fields_added_without_removing_original_payload_fields():
    results = {}

    original = _leaf_16t3q7_original_evaluate_regen_scalability_master_gate(results)
    adapted = evaluate_regen_scalability_master_gate(results)

    assert isinstance(original, dict)
    assert isinstance(adapted, dict)

    for key in original:
        assert key in adapted, key
        assert adapted[key] == original[key], key

    assert_adapter_payload(adapted)


def test_empty_results_emit_canonical_failure_or_review():
    payload = evaluate_regen_scalability_master_gate({})

    assert_adapter_payload(payload)

    assert payload["regen_scalability_master_gate_global_status"] in {
        "FAIL",
        "REVIEW_REQUIRED",
        "BLOCKED",
    }

    findings = payload["regen_scalability_master_gate_structured_findings"]
    assert findings

    assert any(
        finding["severity"] in {"FAIL", "REVIEW_REQUIRED", "BLOCKED"}
        for finding in findings
    )


def test_complete_true_payload_preserves_legacy_status_and_adapter_fields():
    results = {
        "stage_v3_regen_scalability_profile_complete": True,
        "stage_v3_regen_geometry_constraint_validation_complete": True,
        "stage_v3_regen_scalability_report_complete": True,
        "stage_v3_regen_failure_mode_owner_complete": True,
        "regen_scalability_master_gate_complete": True,
    }

    payload = evaluate_regen_scalability_master_gate(results)

    assert_adapter_payload(payload)

    assert "regen_scalability_master_gate_status" in payload
    assert "regen_scalability_master_gate_complete" in payload
    assert "stage_v4_regen_scalability_master_gate_complete" in payload


def test_global_status_payload_shape():
    payload = evaluate_regen_scalability_master_gate({})

    assert_adapter_payload(payload)

    gsp = payload["regen_scalability_master_gate_global_status_payload"]

    assert gsp["owner"] == "regen_scalability_master_gate"
    assert gsp["phase"] == "16T.3Q.7"
    assert gsp["adapter"] == "wave_2_status_adapter"
    assert gsp["adapter_phase"] == "16T.3Q.7"
    assert isinstance(gsp["severity_counts"], dict)
    assert isinstance(gsp["findings"], list)


def test_original_text_payload_still_present():
    payload = evaluate_regen_scalability_master_gate({})

    assert_adapter_payload(payload)

    assert "regen_scalability_master_gate_text" in payload
    assert isinstance(payload["regen_scalability_master_gate_text"], str)


def run_all():
    test_adapter_fields_added_without_removing_original_payload_fields()
    test_empty_results_emit_canonical_failure_or_review()
    test_complete_true_payload_preserves_legacy_status_and_adapter_fields()
    test_global_status_payload_shape()
    test_original_text_payload_still_present()

    print("PASS_REGEN_SCALABILITY_STATUS_ADAPTER_PHASE_16T3Q7")
    return True


if __name__ == "__main__":
    run_all()
