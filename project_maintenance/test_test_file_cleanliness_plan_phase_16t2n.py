from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.test_file_cleanliness_plan_phase_16t2n import (
    PASS_STATUS,
    WARN_STATUS,
    build_test_file_cleanliness_plan,
    build_test_file_cleanliness_report,
    write_test_file_cleanliness_plan,
)


def main() -> int:
    plan = build_test_file_cleanliness_plan()

    assert plan["status"] in {PASS_STATUS, WARN_STATUS}
    assert plan["passed"] is True
    assert "actions" in plan
    assert "counts" in plan

    report = build_test_file_cleanliness_report()

    assert "TEST FILE CLEANLINESS PLAN" in report
    assert "ACTION COUNTS" in report
    assert "SAFETY RULE" in report

    plan_path, report_path = write_test_file_cleanliness_plan()

    assert plan_path.exists()
    assert report_path.exists()
    assert plan_path.parent.name == "allowlists"
    assert report_path.parent.name == "reports"

    print("PASS_TEST_FILE_CLEANLINESS_PLAN_PHASE_16T2N")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
