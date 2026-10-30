from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(LEAF_QT) not in sys.path:
    sys.path.insert(0, str(LEAF_QT))

from regen_candidate_acceptance_master_gate import (
    attach_regen_candidate_acceptance_master_gate,
    _leaf_16t3q11_original_attach_regen_candidate_acceptance_master_gate,
)


ADAPTER_STATUS = "PASS_REGEN_CANDIDATE_ACCEPTANCE_STATUS_ADAPTER_PHASE_16T3Q11"


def baseline_results():
    return {
        "regen_candidate_acceptance_master_gate_ready": True,
        "regen_candidate_acceptance_master_gate_complete": True,
        "regen_candidate_acceptance_master_gate_status": (
            "PASS_REGEN_CANDIDATE_ACCEPTANCE_MASTER_GATE"
        ),
        "regen_candidate_acceptance_master_gate_checks": [
            {
                "name": "acceptance_registered",
                "passed": True,
                "message": "Candidate acceptance is registered.",
            }
        ],
        "regen_candidate_acceptance_master_gate_failed_checks": [],
        "regen_candidate_accepted_candidate": {
            "candidate_id": "RPOP-G0-0001",
            "score": 99.0,
        },
    }


def assert_adapter_payload(payload):
    assert payload["phase_16t3q11_status_adapter_complete"] is True
    assert payload["phase_16t3q11_regen_candidate_acceptance_status_adapter_complete"] is True
    assert payload["regen_candidate_acceptance_status_adapter_complete"] is True
    assert payload["regen_candidate_acceptance_status_adapter_status"] == ADAPTER_STATUS

    assert isinstance(payload["regen_candidate_acceptance_master_gate_structured_findings"], list)
    assert isinstance(payload["regen_candidate_acceptance_master_gate_global_status"], str)
    assert isinstance(payload["regen_candidate_acceptance_master_gate_global_status_payload"], dict)
    assert isinstance(payload["regen_candidate_acceptance_master_gate_adapter_report"], str)

    assert payload["structured_findings"] == payload["regen_candidate_acceptance_master_gate_structured_findings"]
    assert payload["global_status"] == payload["regen_candidate_acceptance_master_gate_global_status"]
    assert payload["global_status_payload"] == payload["regen_candidate_acceptance_master_gate_global_status_payload"]
    assert payload["adapter_report"] == payload["regen_candidate_acceptance_master_gate_adapter_report"]

    report = payload["regen_candidate_acceptance_master_gate_adapter_report"]
    assert "LEAF PHASE 16T.3Q.11 STATUS ADAPTER" in report
    assert "Compatibility:" in report


def test_adapter_fields_added_without_removing_original_payload_fields():
    results = baseline_results()

    original = _leaf_16t3q11_original_attach_regen_candidate_acceptance_master_gate(
        dict(results)
    )
    adapted = attach_regen_candidate_acceptance_master_gate(dict(results))

    assert isinstance(original, dict)
    assert isinstance(adapted, dict)

    for key in original:
        assert key in adapted, key
        assert adapted[key] == original[key], key

    assert_adapter_payload(adapted)


def test_empty_results_emit_structured_status():
    payload = attach_regen_candidate_acceptance_master_gate({})

    assert_adapter_payload(payload)

    assert payload["regen_candidate_acceptance_master_gate_global_status"] in {
        "FAIL",
        "REVIEW_REQUIRED",
        "BLOCKED",
        "PASS",
    }

    assert payload["regen_candidate_acceptance_master_gate_structured_findings"]


def test_missing_candidate_requires_review_or_failure():
    results = baseline_results()
    results.pop("regen_candidate_accepted_candidate", None)

    payload = attach_regen_candidate_acceptance_master_gate(results)

    assert_adapter_payload(payload)

    codes = {
        finding["code"]
        for finding in payload["regen_candidate_acceptance_master_gate_structured_findings"]
    }

    assert (
        "ACCEPTED_CANDIDATE_MISSING" in codes
        or "ACCEPTED_CANDIDATE_PRESENT" in codes
        or "ACCEPTED_CANDIDATE_INVALID" in codes
    )


def test_global_status_payload_shape():
    payload = attach_regen_candidate_acceptance_master_gate(baseline_results())

    assert_adapter_payload(payload)

    gsp = payload["regen_candidate_acceptance_master_gate_global_status_payload"]

    assert gsp["owner"] == "regen_candidate_acceptance_master_gate"
    assert gsp["phase"] == "16T.3Q.11"
    assert gsp["adapter"] == "wave_2_status_adapter"
    assert gsp["adapter_phase"] == "16T.3Q.11"
    assert isinstance(gsp["severity_counts"], dict)
    assert isinstance(gsp["findings"], list)


def run_all():
    test_adapter_fields_added_without_removing_original_payload_fields()
    test_empty_results_emit_structured_status()
    test_missing_candidate_requires_review_or_failure()
    test_global_status_payload_shape()

    print("PASS_REGEN_CANDIDATE_ACCEPTANCE_STATUS_ADAPTER_PHASE_16T3Q11")
    return True


if __name__ == "__main__":
    run_all()
