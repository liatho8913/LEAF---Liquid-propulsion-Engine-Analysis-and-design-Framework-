from pathlib import Path
import ast
import importlib.util
import sys


SOURCE = Path("leaf_qt/foundation_verification_harness.py")


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "foundation_verification_harness_phase_16t3w1",
        SOURCE,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_public_api_preserved():
    tree = ast.parse(SOURCE.read_text())
    public_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }

    required = {
        "build_foundation_verification_seed",
        "build_foundation_verification_cases",
        "run_foundation_verification_harness",
        "build_foundation_verification_report",
        "attach_foundation_verification_harness",
    }

    missing = sorted(required - public_functions)
    assert not missing, f"Missing public functions: {missing}"


def test_legacy_report_generation_unchanged():
    module = _load_module()

    tests = [
        {
            "case": "demo",
            "name": "Example passing check",
            "passed": True,
            "detail": "legacy detail",
        },
        {
            "case": "demo",
            "name": "Example failing check",
            "passed": False,
            "detail": "legacy failure",
        },
    ]

    report = module.build_foundation_verification_report(
        "FAIL_FOUNDATION_VERIFICATION",
        1,
        1,
        tests,
    )

    assert "LEAF FOUNDATION VERIFICATION HARNESS" in report
    assert "Status: FAIL_FOUNDATION_VERIFICATION" in report
    assert "[PASS] Example passing check" in report
    assert "[FAIL] Example failing check" in report
    assert "legacy detail" in report
    assert "legacy failure" in report


def test_status_adapter_adds_structured_payload_without_removing_legacy_fields():
    module = _load_module()

    result = {
        "foundation_verification_status": "PASS_FOUNDATION_VERIFICATION",
        "foundation_verification_passed_count": 12,
        "foundation_verification_failed_count": 0,
        "foundation_verification_tests": [],
        "foundation_verification_text": "legacy report text",
        "foundation_layer_verified": True,
    }

    before_keys = set(result)
    adapted = module._leaf_16t3w1_apply_status_adapter(dict(result))

    for key in before_keys:
        assert key in adapted, f"Legacy key removed: {key}"
        assert adapted[key] == result[key], f"Legacy value changed: {key}"

    assert adapted["phase_16t3w1_status_adapter_complete"] is True
    assert adapted["foundation_verification_harness_status_adapter_complete"] is True
    assert adapted["foundation_verification_harness_status_adapter_status"] == (
        "PASS_PHASE_16T3W1_STATUS_ADAPTER"
    )
    assert adapted["foundation_verification_harness_legacy_status"] == (
        "PASS_FOUNDATION_VERIFICATION"
    )

    assert isinstance(adapted["foundation_verification_harness_structured_findings"], list)
    assert adapted["foundation_verification_harness_global_status"] in {
        "PASS",
        "REVIEW_REQUIRED",
        "BLOCKED",
        "FAIL",
        "NOT_STARTED",
        "RUNNING",
    }
    assert isinstance(adapted["foundation_verification_harness_global_status_payload"], dict)
    assert "FOUNDATION VERIFICATION HARNESS STATUS ADAPTER" in (
        adapted["foundation_verification_harness_adapter_report"]
    )

    assert adapted["structured_findings"] == adapted[
        "foundation_verification_harness_structured_findings"
    ]
    assert adapted["global_status"] == adapted[
        "foundation_verification_harness_global_status"
    ]
    assert adapted["global_status_payload"] == adapted[
        "foundation_verification_harness_global_status_payload"
    ]
    assert adapted["adapter_report"] == adapted[
        "foundation_verification_harness_adapter_report"
    ]


def test_file_audit_adapter_is_additive():
    text = SOURCE.read_text()

    required_tokens = [
        "phase_16t3w1_status_adapter_complete",
        "foundation_verification_harness_structured_findings",
        "foundation_verification_harness_global_status",
        "foundation_verification_harness_global_status_payload",
        "foundation_verification_harness_adapter_report",
        "foundation_verification_harness_legacy_status",
        "return _leaf_16t3w1_apply_status_adapter(verification_result)",
    ]

    missing = [token for token in required_tokens if token not in text]
    assert not missing, f"Missing adapter tokens: {missing}"

    forbidden_tokens = [
        "def run_foundation_verification_harness_v2",
        "class FoundationVerificationHarness",
    ]

    present_forbidden = [token for token in forbidden_tokens if token in text]
    assert not present_forbidden, f"Unexpected redesign tokens: {present_forbidden}"


if __name__ == "__main__":
    test_public_api_preserved()
    test_legacy_report_generation_unchanged()
    test_status_adapter_adds_structured_payload_without_removing_legacy_fields()
    test_file_audit_adapter_is_additive()
    print("PASS_PHASE_16T3W1_FOUNDATION_VERIFICATION_HARNESS_STATUS_ADAPTER")
