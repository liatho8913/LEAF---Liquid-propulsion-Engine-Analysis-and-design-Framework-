from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.engine_solver_status_consumer_integration_audit_phase_16u6 import (
    PASS_BANNER,
    build_engine_solver_status_consumer_integration_audit,
)


def test_engine_solver_status_consumer_integration_audit_phase_16u6():
    result = build_engine_solver_status_consumer_integration_audit()

    assert result["status"] == PASS_BANNER
    assert result["phase"] == "16U.6"
    assert result["solver_candidate_count"] > 0
    assert result["low_risk_count"] >= 0
    assert "candidates" in result
    assert "low_risk_candidates" in result
    assert result["phase_16u6_engine_solver_status_consumer_integration_audit_complete"] is True


if __name__ == "__main__":
    test_engine_solver_status_consumer_integration_audit_phase_16u6()
    print(PASS_BANNER)
