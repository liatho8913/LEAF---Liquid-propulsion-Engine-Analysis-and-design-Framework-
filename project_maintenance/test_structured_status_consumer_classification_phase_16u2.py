from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.structured_status_consumer_classification_phase_16u2 import (
    PASS_BANNER,
    build_structured_status_consumer_classification,
)


def test_structured_status_consumer_classification_phase_16u2():
    result = build_structured_status_consumer_classification()

    assert result["status"] == PASS_BANNER
    assert result["phase"] == "16U.2"
    assert result["source_finding_count"] > 0
    assert result["classified_finding_count"] == result["source_finding_count"]
    assert "by_classification" in result
    assert "migration_required_findings" in result
    assert result["phase_16u2_structured_status_consumer_classification_complete"] is True


if __name__ == "__main__":
    test_structured_status_consumer_classification_phase_16u2()
    print(PASS_BANNER)
