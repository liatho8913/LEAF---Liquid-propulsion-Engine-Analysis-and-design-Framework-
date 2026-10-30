from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.allowlist_constrained_move_execution_phase_16t2h import (
    PASS_STATUS,
    WARN_STATUS,
    build_allowlist_move_plan,
    build_allowlist_move_report,
)


def main() -> int:
    plan = build_allowlist_move_plan()

    assert plan["status"] in {PASS_STATUS, WARN_STATUS}
    assert plan["passed"] is True
    assert "allowlist_path" in plan
    assert "items" in plan
    assert plan["allowed_count"] >= 0
    assert plan["move_count"] >= 0

    report = build_allowlist_move_report(plan, executed=False)

    assert "ALLOWLIST-CONSTRAINED MOVE EXECUTION" in report
    assert "SAFETY GUARANTEE" in report
    assert "MOVE PLAN" in report

    print("PASS_ALLOWLIST_CONSTRAINED_MOVE_EXECUTION_PHASE_16T2H")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
