from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave2_final_status_migration_handover_phase_16t3u import (
    PASS_STATUS,
    run_wave2_final_status_migration_handover,
)


def test_wave2_final_handover_passes():
    result = run_wave2_final_status_migration_handover()

    assert result["passed"] is True
    assert result["status"] == PASS_STATUS
    assert result["canonical_status"] == "PASS"
    assert result["global_status"] == "PASS"
    assert result["wave2_final_status_migration_handover_complete"] is True
    assert result["phase_16t3u_wave2_final_status_migration_handover_complete"] is True


def test_wave2_final_handover_payload_shape():
    result = run_wave2_final_status_migration_handover()

    assert isinstance(result["structured_findings"], list)
    assert isinstance(result["global_status_payload"], dict)
    assert isinstance(result["adapter_report"], str)
    assert isinstance(result["integration_review"], dict)
    assert isinstance(result["completed_phases"], list)
    assert isinstance(result["next_options"], list)

    assert len(result["completed_phases"]) == 15

    payload = result["global_status_payload"]

    assert payload["owner"] == "wave2_final_status_migration_handover"
    assert payload["phase"] == "16T.3U"
    assert payload["canonical_status"] == "PASS"
    assert payload["global_status"] == "PASS"
    assert payload["legacy_status"] == PASS_STATUS
    assert isinstance(payload["severity_counts"], dict)
    assert isinstance(payload["findings"], list)


def test_wave2_final_handover_report_present():
    result = run_wave2_final_status_migration_handover()

    report = result["report"]

    assert "LEAF PHASE 16T.3U" in report
    assert "WAVE 2 FINAL STATUS MIGRATION HANDOVER" in report
    assert PASS_STATUS in report
    assert "Completed Phases:" in report
    assert "Next Options:" in report
    assert "PHASE 16T.3V — Wave 3 Candidate Selection" in report
    assert "Wave 2 final migration handover is complete." in report


def run_all():
    test_wave2_final_handover_passes()
    test_wave2_final_handover_payload_shape()
    test_wave2_final_handover_report_present()

    print("PASS_WAVE2_FINAL_STATUS_MIGRATION_HANDOVER_TEST_PHASE_16T3U")
    return True


if __name__ == "__main__":
    run_all()
