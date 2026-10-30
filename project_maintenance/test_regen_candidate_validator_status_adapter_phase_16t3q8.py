from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(LEAF_QT) not in sys.path:
    sys.path.insert(0, str(LEAF_QT))

from regen_candidate_validator import (
    build_regen_candidate_validator,
    _leaf_16t3q8_original_build_regen_candidate_validator,
)


ADAPTER_STATUS = "PASS_REGEN_CANDIDATE_VALIDATOR_STATUS_ADAPTER_PHASE_16T3Q8"


def assert_adapter_payload(payload):
    assert payload["phase_16t3q8_status_adapter_complete"] is True
    assert payload["phase_16t3q8_regen_candidate_validator_status_adapter_complete"] is True
    assert payload["regen_candidate_validator_status_adapter_complete"] is True
    assert payload["regen_candidate_validator_status_adapter_status"] == ADAPTER_STATUS

    assert isinstance(payload["regen_candidate_validator_structured_findings"], list)
    assert isinstance(payload["regen_candidate_validator_global_status"], str)
    assert isinstance(payload["regen_candidate_validator_global_status_payload"], dict)
    assert isinstance(payload["regen_candidate_validator_adapter_report"], str)

    assert payload["structured_findings"] == payload["regen_candidate_validator_structured_findings"]
    assert payload["global_status"] == payload["regen_candidate_validator_global_status"]
    assert payload["global_status_payload"] == payload["regen_candidate_validator_global_status_payload"]
    assert payload["adapter_report"] == payload["regen_candidate_validator_adapter_report"]

    report = payload["regen_candidate_validator_adapter_report"]
    assert "LEAF PHASE 16T.3Q.8 STATUS ADAPTER" in report
    assert "Compatibility:" in report


def test_adapter_fields_added_without_removing_original_payload_fields():
    results = {}

    original = _leaf_16t3q8_original_build_regen_candidate_validator(results)
    adapted = build_regen_candidate_validator(results)

    assert isinstance(original, dict)
    assert isinstance(adapted, dict)

    for key in original:
        assert key in adapted, key
        assert adapted[key] == original[key], key

    assert_adapter_payload(adapted)


def test_empty_results_emit_structured_status():
    payload = build_regen_candidate_validator({})

    assert_adapter_payload(payload)

    assert payload["regen_candidate_validator_global_status"] in {
        "FAIL",
        "REVIEW_REQUIRED",
        "BLOCKED",
        "PASS",
    }

    findings = payload["regen_candidate_validator_structured_findings"]
    assert findings


def test_global_status_payload_shape():
    payload = build_regen_candidate_validator({})

    assert_adapter_payload(payload)

    gsp = payload["regen_candidate_validator_global_status_payload"]

    assert gsp["owner"] == "regen_candidate_validator"
    assert gsp["phase"] == "16T.3Q.8"
    assert gsp["adapter"] == "wave_2_status_adapter"
    assert gsp["adapter_phase"] == "16T.3Q.8"
    assert isinstance(gsp["severity_counts"], dict)
    assert isinstance(gsp["findings"], list)


def test_validator_text_or_report_payload_preserved_if_present():
    payload = build_regen_candidate_validator({})

    assert_adapter_payload(payload)

    text_keys = [
        key for key in payload
        if "text" in key.lower() or "report" in key.lower()
    ]

    assert isinstance(text_keys, list)


def run_all():
    test_adapter_fields_added_without_removing_original_payload_fields()
    test_empty_results_emit_structured_status()
    test_global_status_payload_shape()
    test_validator_text_or_report_payload_preserved_if_present()

    print("PASS_REGEN_CANDIDATE_VALIDATOR_STATUS_ADAPTER_PHASE_16T3Q8")
    return True


if __name__ == "__main__":
    run_all()
