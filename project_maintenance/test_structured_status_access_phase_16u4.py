from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.structured_status_access import (
    aggregate_status,
    canonical_status,
    finding_severity,
    findings_highest_severity,
    findings_pass,
    highest_severity,
    interpret_status,
    is_fail,
    is_pass,
    is_warn,
    payload_status,
    should_block,
)


PASS_BANNER = "PASS_PHASE_16U4_STRUCTURED_STATUS_ACCESS_LAYER"


def test_structured_status_access_phase_16u4():
    assert canonical_status("PASS") == "PASS"
    assert canonical_status("PASS_WITH_MARGIN") == "PASS"
    assert canonical_status("WARN_LIMITED") == "WARN"
    assert canonical_status("FAIL_THERMAL_STRESS") == "FAIL"

    assert is_pass("PASS_WITH_PLACEHOLDER_DATA") is True
    assert is_warn("PARTIAL_SOURCE_MODE") is True
    assert is_fail("INVALID_GEOMETRY") is True
    assert should_block("FAIL") is True

    result = interpret_status("WARN_LIMITED", source="test")
    assert result.canonical == "WARN"
    assert result.warning is True
    assert result.source == "test"

    assert highest_severity(["PASS", "WARN_LIMITED", "FAIL"]) == "FAIL"
    assert aggregate_status(["PASS", "WARN_LIMITED"]) == "WARN"
    assert aggregate_status(["PASS", "PASS_WITH_MARGIN"]) == "PASS"

    assert finding_severity({"passed": True}) == "INFO"
    assert finding_severity({"passed": False}) == "FAIL"
    assert findings_highest_severity([{"severity": "WARN"}, {"status": "PASS"}]) == "WARN"
    assert findings_pass([{"passed": True}, {"status": "PASS"}]) is True

    assert payload_status({"canonical_status": "PASS"}) == "PASS"
    assert payload_status({"global_status": "WARN_LIMITED"}) == "WARN"
    assert payload_status({"passed": False}) == "FAIL"
    assert payload_status({"findings": [{"passed": True}, {"severity": "WARN"}]}) == "WARN"


if __name__ == "__main__":
    test_structured_status_access_phase_16u4()
    print(PASS_BANNER)
