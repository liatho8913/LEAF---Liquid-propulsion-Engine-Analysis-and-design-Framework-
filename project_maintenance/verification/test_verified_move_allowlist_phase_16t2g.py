from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.verified_move_allowlist_phase_16t2g import (
    PASS_STATUS,
    WARN_STATUS,
    build_verified_move_allowlist,
    build_verified_move_allowlist_report,
    write_verified_move_allowlist,
)


def main() -> int:
    allowlist = build_verified_move_allowlist()

    assert allowlist["status"] in {PASS_STATUS, WARN_STATUS}
    assert allowlist["passed"] is True
    assert "allowed" in allowlist
    assert "blocked" in allowlist
    assert allowlist["allowed_count"] >= 0
    assert allowlist["blocked_count"] >= 0

    report = build_verified_move_allowlist_report()

    assert "VERIFIED MOVE ALLOWLIST" in report
    assert "SAFETY RULE" in report
    assert "ALLOWLISTED MOVE-ONLY FILES" in report

    allowlist_path, report_path = write_verified_move_allowlist()

    assert allowlist_path.exists()
    assert report_path.exists()
    assert allowlist_path.parent.name == "allowlists"
    assert report_path.parent.name == "reports"

    print("PASS_VERIFIED_MOVE_ALLOWLIST_PHASE_16T2G")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
