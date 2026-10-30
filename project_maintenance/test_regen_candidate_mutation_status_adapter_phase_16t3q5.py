from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(LEAF_QT) not in sys.path:
    sys.path.insert(0, str(LEAF_QT))

from regen_candidate_mutation_master_gate import (
    build_regen_candidate_mutation_master_gate,
    _leaf_16t3q5_original_build_regen_candidate_mutation_master_gate,
)


ADAPTER_STATUS = "PASS_REGEN_CANDIDATE_MUTATION_STATUS_ADAPTER_PHASE_16T3Q5"


def baseline_results():
    return {
        "regen_candidate_runtime_mutation_allowed": False,
        "regen_candidate_mutation_master_gate_ready": True,
        "regen_candidate_mutation_master_gate_status": (
            "PASS_REGEN_CANDIDATE_MUTATION_MASTER_GATE"
        ),
        "regen_candidate_mutation_master_gate_checks": [
            {
                "name": "mutation_registered",
                "passed": True,
                "message": "Candidate mutation is registered.",
            }
        ],
        "regen_candidate_mutation_master_gate_failed_checks": [],
        "regen_candidate_mutation_payload": {
            "mutation_strategy": "locked_until_runtime",
            "mutation_count": 0,
        },
    }


def assert_adapter_payload(payload):
    assert payload["phase_16t3q5_status_adapter_complete"] is True
    assert payload["phase_16t3q5_regen_candidate_mutation_status_adapter_complete"] is True
    assert payload["regen_candidate_mutation_status_adapter_complete"] is True
    assert payload["regen_candidate_mutation_status_adapter_status"] == ADAPTER_STATUS

    assert isinstance(payload["regen_candidate_mutation_master_gate_structured_findings"], list)
    assert isinstance(payload["regen_candidate_mutation_master_gate_global_status"], str)
    assert isinstance(payload["regen_candidate_mutation_master_gate_global_status_payload"], dict)
    assert isinstance(payload["regen_candidate_mutation_master_gate_adapter_report"], str)

    assert payload["structured_findings"] == payload["regen_candidate_mutation_master_gate_structured_findings"]
    assert payload["global_status"] == payload["regen_candidate_mutation_master_gate_global_status"]
    assert payload["global_status_payload"] == payload["regen_candidate_mutation_master_gate_global_status_payload"]
    assert payload["adapter_report"] == payload["regen_candidate_mutation_master_gate_adapter_report"]

    report = payload["regen_candidate_mutation_master_gate_adapter_report"]
    assert "LEAF PHASE 16T.3Q.5 STATUS ADAPTER" in report
    assert "Compatibility:" in report


def test_adapter_fields_added_without_removing_original_payload_fields():
    results = baseline_results()

    original = _leaf_16t3q5_original_build_regen_candidate_mutation_master_gate(results)
    adapted = build_regen_candidate_mutation_master_gate(results)

    assert isinstance(original, dict)
    assert isinstance(adapted, dict)

    for key in original:
        assert key in adapted, key
        assert adapted[key] == original[key], key

    assert_adapter_payload(adapted)


def test_failed_or_incomplete_payload_emits_structured_status():
    payload = build_regen_candidate_mutation_master_gate({})

    assert isinstance(payload, dict)
    assert_adapter_payload(payload)

    assert payload["regen_candidate_mutation_master_gate_global_status"] in {
        "FAIL",
        "REVIEW_REQUIRED",
        "BLOCKED",
    }

    findings = payload["regen_candidate_mutation_master_gate_structured_findings"]
    assert findings

    severities = {f["severity"] for f in findings}
    assert severities & {"FAIL", "REVIEW_REQUIRED", "BLOCKED"}


def test_failed_checks_force_fail_status():
    results = baseline_results()
    results["regen_candidate_mutation_master_gate_ready"] = False
    results["regen_candidate_mutation_master_gate_status"] = (
        "FAIL_REGEN_CANDIDATE_MUTATION_MASTER_GATE"
    )
    results["regen_candidate_mutation_master_gate_failed_checks"] = [
        {
            "name": "mutation_missing",
            "passed": False,
            "fail_message": "Candidate mutation is missing.",
        }
    ]

    payload = build_regen_candidate_mutation_master_gate(results)

    assert_adapter_payload(payload)
    assert payload["regen_candidate_mutation_master_gate_global_status"] == "FAIL"

    codes = {
        finding["code"]
        for finding in payload["regen_candidate_mutation_master_gate_structured_findings"]
    }

    assert "FAILED_MUTATION_CHECK_0" in codes


def test_runtime_permission_missing_is_classified_or_normalised():
    results = baseline_results()
    results.pop("regen_candidate_runtime_mutation_allowed", None)

    payload = build_regen_candidate_mutation_master_gate(results)

    assert_adapter_payload(payload)

    codes = {
        finding["code"]
        for finding in payload["regen_candidate_mutation_master_gate_structured_findings"]
    }

    assert (
        "RUNTIME_MUTATION_PERMISSION_MISSING" in codes
        or "RUNTIME_MUTATION_LOCKED" in codes
        or "RUNTIME_MUTATION_ALLOWED" in codes
    )


def test_mutation_payload_invalid_is_failed_or_normalised():
    results = baseline_results()
    results["regen_candidate_mutation_payload"] = "not-a-dict"

    payload = build_regen_candidate_mutation_master_gate(results)

    assert_adapter_payload(payload)

    codes = {
        finding["code"]
        for finding in payload["regen_candidate_mutation_master_gate_structured_findings"]
    }

    assert (
        "MUTATION_PAYLOAD_INVALID" in codes
        or "MUTATION_PAYLOAD_MISSING" in codes
        or "MUTATION_PAYLOAD_PRESENT" in codes
    )

    if "MUTATION_PAYLOAD_INVALID" in codes:
        assert payload["regen_candidate_mutation_master_gate_global_status"] == "FAIL"
    else:
        assert payload["regen_candidate_mutation_master_gate_global_status"] in {
            "PASS",
            "REVIEW_REQUIRED",
            "FAIL",
            "BLOCKED",
        }


def test_adapter_payload_contains_canonical_status_payload():
    payload = build_regen_candidate_mutation_master_gate(baseline_results())

    assert_adapter_payload(payload)

    gsp = payload["regen_candidate_mutation_master_gate_global_status_payload"]

    assert gsp["owner"] == "regen_candidate_mutation_master_gate"
    assert gsp["phase"] == "16T.3Q.5"
    assert gsp["adapter"] == "wave_2_status_adapter"
    assert gsp["adapter_phase"] == "16T.3Q.5"
    assert isinstance(gsp["severity_counts"], dict)
    assert isinstance(gsp["findings"], list)


def run_all():
    test_adapter_fields_added_without_removing_original_payload_fields()
    test_failed_or_incomplete_payload_emits_structured_status()
    test_failed_checks_force_fail_status()
    test_runtime_permission_missing_is_classified_or_normalised()
    test_mutation_payload_invalid_is_failed_or_normalised()
    test_adapter_payload_contains_canonical_status_payload()

    print("PASS_REGEN_CANDIDATE_MUTATION_STATUS_ADAPTER_PHASE_16T3Q5")
    return True


if __name__ == "__main__":
    run_all()
