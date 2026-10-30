from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.solver_status_access import (
    solver_aggregate_status,
    solver_blocks,
    solver_fail,
    solver_findings_highest_severity,
    solver_highest_severity,
    solver_pass,
    solver_payload_status,
    solver_status,
    solver_status_record,
    solver_warn,
)


PASS_BANNER = "PASS_PHASE_16U5_SOLVER_STATUS_ACCESS_WRAPPERS"


def test_solver_status_access_phase_16u5():
    assert solver_status("PASS_WITH_MARGIN") == "PASS"
    assert solver_status("WARN_LIMITED") == "WARN"
    assert solver_status("FAIL_THERMAL_STRESS") == "FAIL"

    assert solver_pass("PASS") is True
    assert solver_warn("PARTIAL_SOURCE_MODE") is True
    assert solver_fail("INVALID_GEOMETRY") is True
    assert solver_blocks("FAIL") is True

    assert solver_aggregate_status(["PASS", "PASS_WITH_MARGIN"]) == "PASS"
    assert solver_aggregate_status(["PASS", "WARN_LIMITED"]) == "WARN"
    assert solver_aggregate_status(["PASS", "FAIL"]) == "FAIL"

    assert solver_highest_severity(["PASS", "WARN", "FAIL"]) == "FAIL"
    assert solver_findings_highest_severity(
        [{"status": "PASS"}, {"severity": "WARN"}]
    ) == "WARN"

    assert solver_payload_status({"status": "PASS_WITH_MARGIN"}) == "PASS"
    assert solver_payload_status({"passed": False}) == "FAIL"

    record = solver_status_record("WARN_LIMITED", source="phase_16u5_test")
    assert record["canonical"] == "WARN"
    assert record["warning"] is True
    assert record["source"] == "phase_16u5_test"


if __name__ == "__main__":
    test_solver_status_access_phase_16u5()
    print(PASS_BANNER)
