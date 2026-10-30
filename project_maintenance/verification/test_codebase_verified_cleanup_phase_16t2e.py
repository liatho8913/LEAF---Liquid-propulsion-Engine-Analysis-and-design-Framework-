from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.codebase_verified_cleanup_phase_16t2e import (
    ARCHIVE_DIR,
    REPORT_DIR,
    ZIP_DIR,
    PASS_STATUS,
    build_verified_cleanup_plan,
    build_verified_cleanup_report,
)


def main() -> int:
    plan = build_verified_cleanup_plan()

    assert "phase" in plan
    assert "items" in plan
    assert "candidate_count" in plan
    assert Path(plan["report_dir"]).name == REPORT_DIR.name
    assert Path(plan["zip_dir"]).name == ZIP_DIR.name
    assert Path(plan["archive_dir"]).name == ARCHIVE_DIR.name

    report = build_verified_cleanup_report(plan, executed=False)

    assert "VERIFIED CODEBASE CLEANUP EXECUTION PLAN" in report
    assert "SAFETY GUARANTEE" in report
    assert "_leaf_archive" in report
    assert "_leaf_artifacts" in report

    print(PASS_STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
