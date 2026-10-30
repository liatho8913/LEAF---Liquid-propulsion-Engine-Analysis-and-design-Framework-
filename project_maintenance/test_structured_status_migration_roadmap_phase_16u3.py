from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.structured_status_migration_roadmap_phase_16u3 import (
    PASS_BANNER,
    build_structured_status_migration_roadmap,
)


def test_structured_status_migration_roadmap_phase_16u3():
    result = build_structured_status_migration_roadmap()

    assert result["status"] == PASS_BANNER
    assert result["phase"] == "16U.3"
    assert result["source_migration_required_count"] > 0
    assert result["roadmap_item_count"] == result["source_migration_required_count"]
    assert "by_wave" in result
    assert "roadmap" in result
    assert result["phase_16u3_structured_status_migration_roadmap_complete"] is True


if __name__ == "__main__":
    test_structured_status_migration_roadmap_phase_16u3()
    print(PASS_BANNER)
