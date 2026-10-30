from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.structured_status_consumer_discovery_phase_16u1 import (
    PASS_BANNER,
    build_consumer_discovery,
)


def test_structured_status_consumer_discovery_phase_16u1():
    result = build_consumer_discovery()

    assert result["status"] == PASS_BANNER
    assert result["phase"] == "16U.1"
    assert result["files_scanned"] > 0
    assert result["finding_count"] > 0
    assert "findings" in result
    assert "high_priority_findings" in result
    assert result["phase_16u1_structured_status_consumer_discovery_complete"] is True


if __name__ == "__main__":
    test_structured_status_consumer_discovery_phase_16u1()
    print(PASS_BANNER)
