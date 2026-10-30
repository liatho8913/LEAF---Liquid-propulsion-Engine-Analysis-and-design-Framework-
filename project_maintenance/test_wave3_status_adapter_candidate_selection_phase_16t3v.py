from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave3_status_adapter_candidate_selection_phase_16t3v import (
    PASS_STATUS,
    select_wave3_candidates,
)


def test_wave3_candidate_selection_runs():
    result = select_wave3_candidates()

    assert result["passed"] is True
    assert result["status"] == PASS_STATUS
    assert result["candidate_count"] >= result["selected_count"]
    assert result["selected_count"] > 0
    assert result["wave3_status_adapter_candidate_selection_complete"] is True
    assert result["phase_16t3v_wave3_status_adapter_candidate_selection_complete"] is True


def test_wave3_selected_candidate_shape():
    result = select_wave3_candidates()

    for item in result["selected_candidates"]:
        assert "path" in item
        assert "classification" in item
        assert "score" in item
        assert "legacy_status_count" in item
        assert "legacy_status_examples" in item
        assert item["legacy_status_count"] > 0


def test_wave3_report_present():
    result = select_wave3_candidates()

    report = result["report"]

    assert "LEAF PHASE 16T.3V" in report
    assert "WAVE 3 STATUS ADAPTER CANDIDATE SELECTION" in report
    assert PASS_STATUS in report
    assert "Selected Candidates:" in report
    assert "Selection Policy:" in report


def run_all():
    test_wave3_candidate_selection_runs()
    test_wave3_selected_candidate_shape()
    test_wave3_report_present()

    print("PASS_WAVE3_STATUS_ADAPTER_CANDIDATE_SELECTION_TEST_PHASE_16T3V")
    return True


if __name__ == "__main__":
    run_all()
