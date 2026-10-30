from __future__ import annotations

from leaf_qt.foundation_final_signoff_controller import evaluate_foundation_final_signoff


VALID_RESULTS = {
    "foundation_attachment_pipeline_status": "PASS",
    "foundation_result_key_audit_status": "PASS",
    "foundation_save_load_verification_status": "PASS_FOUNDATION_SAVE_LOAD_VERIFICATION",
    "foundation_ui_launch_verification_status": "PASS_FOUNDATION_UI_LAUNCH_VERIFICATION",
    "foundation_verification_status": "PASS_FOUNDATION_VERIFICATION",
    "foundation_verification_passed_count": 396,
    "foundation_verification_failed_count": 0,
}


def test_phase_16t3k1_preserves_legacy_pass_contract() -> None:
    payload = evaluate_foundation_final_signoff(dict(VALID_RESULTS))

    assert payload["foundation_final_signoff_status"] == "PASS_FOUNDATION_FINAL_SIGNOFF"
    assert payload["foundation_final_signoff_complete"] is True
    assert payload["foundation_final_signoff_blocking_reasons"] == []
    assert payload["foundation_final_signoff_warning_reasons"] == []


def test_phase_16t3k1_adds_structured_findings_and_global_pass() -> None:
    payload = evaluate_foundation_final_signoff(dict(VALID_RESULTS))

    assert payload["foundation_final_signoff_structured_findings"]
    assert payload["foundation_final_signoff_global_status"] == "PASS"
    assert payload["foundation_final_signoff_global_status_payload"]["passed"] is True


def test_phase_16t3k1_warning_escalates_to_blocked_in_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["foundation_verification_passed_count"] = 0

    payload = evaluate_foundation_final_signoff(data)

    assert payload["foundation_final_signoff_status"] == "WARN_FOUNDATION_FINAL_SIGNOFF_REVIEW"
    assert payload["foundation_final_signoff_complete"] is False
    assert payload["foundation_final_signoff_global_status"] == "BLOCKED"


def test_phase_16t3k1_blocking_failure_maps_to_fail() -> None:
    data = dict(VALID_RESULTS)
    data["foundation_verification_failed_count"] = 2

    payload = evaluate_foundation_final_signoff(data)

    assert payload["foundation_final_signoff_status"] == "FAIL_FOUNDATION_FINAL_SIGNOFF"
    assert payload["foundation_final_signoff_complete"] is False
    assert payload["foundation_final_signoff_global_status"] == "FAIL"


def test_phase_16t3k1_invalid_input_preserves_legacy_failure_and_adds_global_status() -> None:
    payload = evaluate_foundation_final_signoff(None)

    assert payload["foundation_final_signoff_status"] == "FAIL_INVALID_RESULTS"
    assert payload["foundation_final_signoff_complete"] is False
    assert payload["foundation_final_signoff_global_status"] == "FAIL"
    assert payload["foundation_final_signoff_structured_findings"]
