from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(LEAF_QT) not in sys.path:
    sys.path.insert(0, str(LEAF_QT))

from regen_source_validation_gate import (
    audit_regen_source_validation,
    _leaf_16t3q9_original_audit_regen_source_validation,
)


ADAPTER_STATUS = "PASS_REGEN_SOURCE_VALIDATION_GATE_STATUS_ADAPTER_PHASE_16T3Q9"


def assert_adapter_payload(payload):
    assert payload["phase_16t3q9_status_adapter_complete"] is True
    assert payload["phase_16t3q9_regen_source_validation_gate_status_adapter_complete"] is True
    assert payload["regen_source_validation_gate_status_adapter_complete"] is True
    assert payload["regen_source_validation_gate_status_adapter_status"] == ADAPTER_STATUS

    assert isinstance(payload["regen_source_validation_gate_structured_findings"], list)
    assert isinstance(payload["regen_source_validation_gate_global_status"], str)
    assert isinstance(payload["regen_source_validation_gate_global_status_payload"], dict)
    assert isinstance(payload["regen_source_validation_gate_adapter_report"], str)

    assert payload["structured_findings"] == payload["regen_source_validation_gate_structured_findings"]
    assert payload["global_status"] == payload["regen_source_validation_gate_global_status"]
    assert payload["global_status_payload"] == payload["regen_source_validation_gate_global_status_payload"]
    assert payload["adapter_report"] == payload["regen_source_validation_gate_adapter_report"]

    report = payload["regen_source_validation_gate_adapter_report"]
    assert "LEAF PHASE 16T.3Q.9 STATUS ADAPTER" in report
    assert "Compatibility:" in report


def test_adapter_fields_added_without_removing_original_payload_fields():
    results = {}

    original = _leaf_16t3q9_original_audit_regen_source_validation(results)
    adapted = audit_regen_source_validation(results)

    assert isinstance(original, dict)
    assert isinstance(adapted, dict)

    for key in original:
        assert key in adapted, key
        assert adapted[key] == original[key], key

    assert_adapter_payload(adapted)


def test_empty_results_emit_structured_status():
    payload = audit_regen_source_validation({})

    assert_adapter_payload(payload)

    assert payload["regen_source_validation_gate_global_status"] in {
        "FAIL",
        "REVIEW_REQUIRED",
        "BLOCKED",
        "PASS",
    }

    assert payload["regen_source_validation_gate_structured_findings"]


def test_placeholder_modes_block_or_require_review():
    results = {
        "regen_material_source_validation_mode": "PLACEHOLDER_MODE",
        "regen_coating_source_validation_mode": "PLACEHOLDER_MODE",
        "regen_material_source_quality_score": 0,
        "regen_coating_source_quality_score": 0,
    }

    payload = audit_regen_source_validation(results)

    assert_adapter_payload(payload)

    findings = payload["regen_source_validation_gate_structured_findings"]

    assert findings

    assert payload["regen_source_validation_gate_global_status"] in {
        "BLOCKED",
        "FAIL",
        "REVIEW_REQUIRED",
    }

    assert any(
        finding["severity"] in {"BLOCKED", "FAIL", "REVIEW_REQUIRED"}
        for finding in findings
    )


def test_global_status_payload_shape():
    payload = audit_regen_source_validation({})

    assert_adapter_payload(payload)

    gsp = payload["regen_source_validation_gate_global_status_payload"]

    assert gsp["owner"] == "regen_source_validation_gate"
    assert gsp["phase"] == "16T.3Q.9"
    assert gsp["adapter"] == "wave_2_status_adapter"
    assert gsp["adapter_phase"] == "16T.3Q.9"
    assert isinstance(gsp["severity_counts"], dict)
    assert isinstance(gsp["findings"], list)


def run_all():
    test_adapter_fields_added_without_removing_original_payload_fields()
    test_empty_results_emit_structured_status()
    test_placeholder_modes_block_or_require_review()
    test_global_status_payload_shape()

    print("PASS_REGEN_SOURCE_VALIDATION_GATE_STATUS_ADAPTER_PHASE_16T3Q9")
    return True


if __name__ == "__main__":
    run_all()
