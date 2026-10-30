from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave2_status_adapter_integration_review_phase_16t3t import (
    PASS_STATUS,
    run_wave2_status_adapter_integration_review,
)


def test_wave2_integration_review_passes():
    result = run_wave2_status_adapter_integration_review()

    assert result["passed"] is True
    assert result["status"] == PASS_STATUS
    assert result["canonical_status"] == "PASS"
    assert result["global_status"] == "PASS"
    assert result["wave2_status_adapter_integration_review_complete"] is True
    assert result["phase_16t3t_wave2_status_adapter_integration_review_complete"] is True


def test_wave2_integration_review_payload_shape():
    result = run_wave2_status_adapter_integration_review()

    assert isinstance(result["structured_findings"], list)
    assert isinstance(result["global_status_payload"], dict)
    assert isinstance(result["adapter_report"], str)
    assert isinstance(result["master_gate"], dict)
    assert isinstance(result["residual_risks"], list)

    payload = result["global_status_payload"]

    assert payload["owner"] == "wave2_status_adapter_integration_review"
    assert payload["phase"] == "16T.3T"
    assert payload["canonical_status"] == "PASS"
    assert payload["global_status"] == "PASS"
    assert payload["legacy_status"] == PASS_STATUS
    assert isinstance(payload["severity_counts"], dict)
    assert isinstance(payload["findings"], list)


def test_wave2_integration_review_report_present():
    result = run_wave2_status_adapter_integration_review()

    report = result["report"]

    assert "LEAF PHASE 16T.3T" in report
    assert "WAVE 2 STATUS ADAPTER INTEGRATION REVIEW" in report
    assert PASS_STATUS in report
    assert "Residual Risks:" in report
    assert "Wave 2 integration review is complete and non-blocking." in report


def run_all():
    test_wave2_integration_review_passes()
    test_wave2_integration_review_payload_shape()
    test_wave2_integration_review_report_present()

    print("PASS_WAVE2_STATUS_ADAPTER_INTEGRATION_REVIEW_TEST_PHASE_16T3T")
    return True


if __name__ == "__main__":
    run_all()
