from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.warning_escalation_policy_phase_16t3e import (
    PASS_STATUS,
    WARN_STATUS,
    FAIL_STATUS,
    classify_warning,
    evaluate_warning_policy,
    build_warning_policy_report,
    write_warning_policy_report,
)


def main() -> int:
    allowed = classify_warning(
        "Archive cleanup debt exists.",
        category="ARCHIVE_ELIGIBLE",
        owner="Verification Registry",
        allowlisted=True,
    )
    assert allowed["allowed_as_warning"] is True
    assert allowed["escalates_to_fail"] is False

    missing_owner = classify_warning(
        "Something vague happened.",
        category="MANUAL_REVIEW_REQUIRED",
    )
    assert missing_owner["escalates_to_fail"] is True

    blocking = classify_warning(
        "Required data missing.",
        category="MISSING_REQUIRED_DATA",
        owner="Solver Owner",
    )
    assert blocking["escalates_to_fail"] is True

    production_unlisted = classify_warning(
        "Cleanup debt in production gate.",
        category="CLEANUP_DEBT",
        owner="Release Gate",
        production_gate=True,
        allowlisted=False,
    )
    assert production_unlisted["escalates_to_fail"] is True

    policy = evaluate_warning_policy([
        {
            "message": "Archive eligible development checks.",
            "category": "ARCHIVE_ELIGIBLE",
            "owner": "Verification Registry",
            "allowlisted": True,
        }
    ])

    assert policy["status"] == WARN_STATUS
    assert policy["passed"] is True

    fail_policy = evaluate_warning_policy([
        {
            "message": "Missing required field.",
            "category": "MISSING_REQUIRED_DATA",
            "owner": "Solver Owner",
        }
    ])

    assert fail_policy["status"] == FAIL_STATUS
    assert fail_policy["passed"] is False

    report = build_warning_policy_report()
    assert "GLOBAL WARNING ESCALATION POLICY" in report
    assert "BLOCKING CATEGORIES" in report
    assert "NONBLOCKING CATEGORIES" in report
    assert "SAFETY RULE" in report

    output = write_warning_policy_report()
    assert output.exists()
    assert output.parent.name == "reports"

    print("PASS_WARNING_ESCALATION_POLICY_PHASE_16T3E")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
