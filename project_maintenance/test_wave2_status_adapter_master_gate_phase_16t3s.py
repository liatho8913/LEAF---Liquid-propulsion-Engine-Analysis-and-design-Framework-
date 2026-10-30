from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave2_status_adapter_master_gate_phase_16t3s import (
    PASS_STATUS,
    run_wave2_status_adapter_master_gate,
)


def test_wave2_master_gate_passes():
    result = run_wave2_status_adapter_master_gate()

    assert result["passed"] is True
    assert result["status"] == PASS_STATUS
    assert result["canonical_status"] == "PASS"
    assert result["global_status"] == "PASS"
    assert result["wave2_status_adapter_master_gate_complete"] is True
    assert result["phase_16t3s_wave2_status_adapter_master_gate_complete"] is True


def test_wave2_master_gate_payload_shape():
    result = run_wave2_status_adapter_master_gate()

    assert isinstance(result["structured_findings"], list)
    assert isinstance(result["global_status_payload"], dict)
    assert isinstance(result["adapter_report"], str)
    assert isinstance(result["completion_audit"], dict)

    payload = result["global_status_payload"]

    assert payload["owner"] == "wave2_status_adapter_master_gate"
    assert payload["phase"] == "16T.3S"
    assert payload["canonical_status"] == "PASS"
    assert payload["global_status"] == "PASS"
    assert payload["legacy_status"] == PASS_STATUS
    assert isinstance(payload["severity_counts"], dict)
    assert isinstance(payload["findings"], list)


def test_wave2_master_gate_report_present():
    result = run_wave2_status_adapter_master_gate()

    report = result["report"]

    assert "LEAF PHASE 16T.3S" in report
    assert "WAVE 2 STATUS ADAPTER MASTER GATE" in report
    assert PASS_STATUS in report
    assert "Wave 2 status adapter migration is formally signed off." in report


def run_all():
    test_wave2_master_gate_passes()
    test_wave2_master_gate_payload_shape()
    test_wave2_master_gate_report_present()

    print("PASS_WAVE2_STATUS_ADAPTER_MASTER_GATE_TEST_PHASE_16T3S")
    return True


if __name__ == "__main__":
    run_all()
