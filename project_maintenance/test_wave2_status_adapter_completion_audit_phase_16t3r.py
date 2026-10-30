from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave2_status_adapter_completion_audit_phase_16t3r import (
    run_wave2_status_adapter_completion_audit,
)


def test_wave2_completion_audit_passes():
    result = run_wave2_status_adapter_completion_audit()

    assert result["passed"] is True
    assert result["status"] == "PASS_WAVE2_STATUS_ADAPTER_COMPLETION_AUDIT_PHASE_16T3R"
    assert result["module_count"] == 12
    assert result["module_pass_count"] == 12
    assert not result["missing_source_files"]
    assert not result["failed_modules"]


def test_wave2_completion_audit_report_present():
    result = run_wave2_status_adapter_completion_audit()

    assert "LEAF PHASE 16T.3R" in result["report"]
    assert "WAVE 2 STATUS ADAPTER COMPLETION AUDIT" in result["report"]
    assert "Modules audited: 12 / 12" in result["report"]


def run_all():
    test_wave2_completion_audit_passes()
    test_wave2_completion_audit_report_present()

    print("PASS_WAVE2_STATUS_ADAPTER_COMPLETION_AUDIT_TEST_PHASE_16T3R")
    return True


if __name__ == "__main__":
    run_all()
