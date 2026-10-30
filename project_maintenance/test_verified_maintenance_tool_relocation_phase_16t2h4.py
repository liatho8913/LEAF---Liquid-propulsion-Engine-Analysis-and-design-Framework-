from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.verified_maintenance_tool_relocation_phase_16t2h4 import (
    PASS_STATUS,
    WARN_STATUS,
    build_verified_relocation_plan,
    build_verified_relocation_report,
)


def main() -> int:
    plan = build_verified_relocation_plan()

    assert plan["status"] in {PASS_STATUS, WARN_STATUS}
    assert plan["passed"] is True
    assert "items" in plan
    assert "move_count" in plan
    assert "wrapper_count" in plan

    report = build_verified_relocation_report(plan, executed=False)

    assert "VERIFIED MAINTENANCE TOOL RELOCATION" in report
    assert "SAFETY GUARANTEE" in report
    assert "RELOCATION PLAN" in report

    print("PASS_VERIFIED_MAINTENANCE_TOOL_RELOCATION_PHASE_16T2H4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
