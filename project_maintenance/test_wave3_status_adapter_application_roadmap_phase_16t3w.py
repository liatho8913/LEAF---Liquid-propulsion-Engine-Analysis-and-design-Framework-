from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave3_status_adapter_application_roadmap_phase_16t3w import (
    PASS_STATUS,
    build_wave3_status_adapter_application_roadmap,
)


def test_wave3_roadmap_passes():
    result = build_wave3_status_adapter_application_roadmap()

    assert result["passed"] is True
    assert result["status"] == PASS_STATUS
    assert result["roadmap_count"] > 0
    assert result["active_candidate_count"] >= result["roadmap_count"]
    assert result["wave3_status_adapter_application_roadmap_complete"] is True
    assert result["phase_16t3w_wave3_status_adapter_application_roadmap_complete"] is True


def test_wave3_roadmap_excludes_upload_duplicates():
    result = build_wave3_status_adapter_application_roadmap()

    for item in result["roadmap"]:
        assert "LEAF_UPLOAD/" not in item["target"]
        assert "archive/" not in item["target"]
        assert "backup/" not in item["target"]


def test_wave3_roadmap_shape():
    result = build_wave3_status_adapter_application_roadmap()

    for item in result["roadmap"]:
        assert "phase" in item
        assert "target" in item
        assert "classification" in item
        assert "legacy_status_count" in item
        assert "implementation_policy" in item
        assert isinstance(item["implementation_policy"], list)


def test_wave3_roadmap_report_present():
    result = build_wave3_status_adapter_application_roadmap()

    report = result["report"]

    assert "LEAF PHASE 16T.3W" in report
    assert "WAVE 3 STATUS ADAPTER APPLICATION ROADMAP" in report
    assert PASS_STATUS in report
    assert "Archive / Upload Filtering:" in report
    assert "Roadmap:" in report


def run_all():
    test_wave3_roadmap_passes()
    test_wave3_roadmap_excludes_upload_duplicates()
    test_wave3_roadmap_shape()
    test_wave3_roadmap_report_present()

    print("PASS_WAVE3_STATUS_ADAPTER_APPLICATION_ROADMAP_TEST_PHASE_16T3W")
    return True


if __name__ == "__main__":
    run_all()
