from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(LEAF_QT) not in sys.path:
    sys.path.insert(0, str(LEAF_QT))

from regen_optimisation_master_gate import (
    build_regen_optimisation_master_gate,
    _leaf_16t3q6_original_build_regen_optimisation_master_gate,
)


ADAPTER_STATUS = "PASS_REGEN_OPTIMISATION_STATUS_ADAPTER_PHASE_16T3Q6"


def baseline_results():
    return {
        "regen_candidate_runtime_mutation_allowed": False,
        "regen_candidate_runtime_evolution_allowed": False,
        "regen_candidate_runtime_solver_allowed": False,
        "regen_candidate_runtime_acceptance_allowed": False,

        "regen_optimisation_master_gate_ready": True,
        "regen_optimisation_master_gate_status": (
            "PASS_REGEN_OPTIMISATION_MASTER_GATE"
        ),
        "regen_optimisation_master_gate_checks": [
            {
                "name": "optimisation_registered",
                "passed": True,
                "message": "Optimisation is registered.",
            }
        ],
        "regen_optimisation_master_gate_failed_checks": [],
        "regen_optimisation_payload": {
            "optimisation_mode": "locked_until_runtime",
            "candidate_count": 0,
        },
    }


def assert_adapter_payload(payload):
    assert payload["phase_16t3q6_status_adapter_complete"] is True
    assert payload["phase_16t3q6_regen_optimisation_status_adapter_complete"] is True
    assert payload["regen_optimisation_status_adapter_complete"] is True
    assert payload["regen_optimisation_status_adapter_status"] == ADAPTER_STATUS

    assert isinstance(payload["regen_optimisation_master_gate_structured_findings"], list)
    assert isinstance(payload["regen_optimisation_master_gate_global_status"], str)
    assert isinstance(payload["regen_optimisation_master_gate_global_status_payload"], dict)
    assert isinstance(payload["regen_optimisation_master_gate_adapter_report"], str)

    assert payload["structured_findings"] == payload["regen_optimisation_master_gate_structured_findings"]
    assert payload["global_status"] == payload["regen_optimisation_master_gate_global_status"]
    assert payload["global_status_payload"] == payload["regen_optimisation_master_gate_global_status_payload"]
    assert payload["adapter_report"] == payload["regen_optimisation_master_gate_adapter_report"]

    report = payload["regen_optimisation_master_gate_adapter_report"]
    assert "LEAF PHASE 16T.3Q.6 STATUS ADAPTER" in report
    assert "Compatibility:" in report


def test_adapter_fields_added_without_removing_original_payload_fields():
    results = baseline_results()

    original = _leaf_16t3q6_original_build_regen_optimisation_master_gate(results)
    adapted = build_regen_optimisation_master_gate(results)

    assert isinstance(original, dict)
    assert isinstance(adapted, dict)

    for key in original:
        assert key in adapted, key
        assert adapted[key] == original[key], key

    assert_adapter_payload(adapted)


def test_failed_or_incomplete_payload_emits_structured_status():
    payload = build_regen_optimisation_master_gate({})

    assert isinstance(payload, dict)
    assert_adapter_payload(payload)

    assert payload["regen_optimisation_master_gate_global_status"] in {
        "FAIL",
        "REVIEW_REQUIRED",
        "BLOCKED",
    }

    findings = payload["regen_optimisation_master_gate_structured_findings"]
    assert findings

    severities = {f["severity"] for f in findings}
    assert severities & {"FAIL", "REVIEW_REQUIRED", "BLOCKED"}


def test_failed_checks_force_fail_status():
    results = baseline_results()
    results["regen_optimisation_master_gate_ready"] = False
    results["regen_optimisation_master_gate_status"] = (
        "FAIL_REGEN_OPTIMISATION_MASTER_GATE"
    )
    results["regen_optimisation_master_gate_failed_checks"] = [
        {
            "name": "optimisation_missing",
            "passed": False,
            "fail_message": "Optimisation is missing.",
        }
    ]

    payload = build_regen_optimisation_master_gate(results)

    assert_adapter_payload(payload)
    assert payload["regen_optimisation_master_gate_global_status"] == "FAIL"

    findings = payload["regen_optimisation_master_gate_structured_findings"]

    assert any(
        finding["severity"] == "FAIL"
        for finding in findings
    )

    assert any(
        finding["code"] == "OPTIMISATION_MASTER_GATE_NOT_READY"
        or finding["code"].startswith("FAILED_OPTIMISATION_CHECK_")
        for finding in findings
    )


def test_runtime_flags_missing_are_classified_or_normalised():
    results = baseline_results()

    for key in [
        "regen_candidate_runtime_mutation_allowed",
        "regen_candidate_runtime_evolution_allowed",
        "regen_candidate_runtime_solver_allowed",
        "regen_candidate_runtime_acceptance_allowed",
    ]:
        results.pop(key, None)

    payload = build_regen_optimisation_master_gate(results)

    assert_adapter_payload(payload)

    codes = {
        finding["code"]
        for finding in payload["regen_optimisation_master_gate_structured_findings"]
    }

    assert (
        "OPTIMISATION_RUNTIME_FLAGS_MISSING" in codes
        or "OPTIMISATION_RUNTIME_FLAGS_PRESENT" in codes
    )


def test_optimisation_payload_invalid_is_failed_or_normalised():
    results = baseline_results()
    results["regen_optimisation_payload"] = "not-a-dict"

    payload = build_regen_optimisation_master_gate(results)

    assert_adapter_payload(payload)

    codes = {
        finding["code"]
        for finding in payload["regen_optimisation_master_gate_structured_findings"]
    }

    assert (
        "OPTIMISATION_PAYLOAD_INVALID" in codes
        or "OPTIMISATION_PAYLOAD_MISSING" in codes
        or "OPTIMISATION_PAYLOAD_PRESENT" in codes
    )

    if "OPTIMISATION_PAYLOAD_INVALID" in codes:
        assert payload["regen_optimisation_master_gate_global_status"] == "FAIL"


def test_adapter_payload_contains_canonical_status_payload():
    payload = build_regen_optimisation_master_gate(baseline_results())

    assert_adapter_payload(payload)

    gsp = payload["regen_optimisation_master_gate_global_status_payload"]

    assert gsp["owner"] == "regen_optimisation_master_gate"
    assert gsp["phase"] == "16T.3Q.6"
    assert gsp["adapter"] == "wave_2_status_adapter"
    assert gsp["adapter_phase"] == "16T.3Q.6"
    assert isinstance(gsp["severity_counts"], dict)
    assert isinstance(gsp["findings"], list)


def run_all():
    test_adapter_fields_added_without_removing_original_payload_fields()
    test_failed_or_incomplete_payload_emits_structured_status()
    test_failed_checks_force_fail_status()
    test_runtime_flags_missing_are_classified_or_normalised()
    test_optimisation_payload_invalid_is_failed_or_normalised()
    test_adapter_payload_contains_canonical_status_payload()

    print("PASS_REGEN_OPTIMISATION_STATUS_ADAPTER_PHASE_16T3Q6")
    return True


if __name__ == "__main__":
    run_all()
