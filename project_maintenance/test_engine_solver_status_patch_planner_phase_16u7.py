from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.engine_solver_status_patch_planner_phase_16u7 import (
    PASS_BANNER,
    build_engine_solver_status_patch_planner,
)


def test_engine_solver_status_patch_planner_phase_16u7():
    result = build_engine_solver_status_patch_planner()

    assert result["status"] == PASS_BANNER
    assert result["phase"] == "16U.7"
    assert result["source_low_risk_count"] > 0
    assert result["unique_patch_item_count"] > 0
    assert "patch_plan" in result
    assert "solver_pass" in result["wrappers_required"]
    assert result["phase_16u7_engine_solver_status_patch_planner_complete"] is True


if __name__ == "__main__":
    test_engine_solver_status_patch_planner_phase_16u7()
    print(PASS_BANNER)
