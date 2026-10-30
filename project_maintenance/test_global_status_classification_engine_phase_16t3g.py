from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.global_status_classification_engine_phase_16t3g import (
    STATUS_PASS,
    STATUS_REVIEW_REQUIRED,
    STATUS_BLOCKED,
    STATUS_FAIL,
    STATUS_RUNNING,
    STATUS_NOT_STARTED,
    make_finding,
    classify_status,
    legacy_warn_to_finding,
    build_global_status_engine_report,
    write_global_status_engine_report,
)


def main() -> int:
    passed = classify_status([
        make_finding("Complete.", "OK", "Test Owner")
    ])
    assert passed["status"] == STATUS_PASS
    assert passed["passed"] is True

    review = classify_status([
        make_finding("Candidate ready.", "CANDIDATE_AVAILABLE", "Optimisation Owner")
    ])
    assert review["status"] == STATUS_REVIEW_REQUIRED
    assert review["requires_human_review"] is True

    blocked = classify_status([
        make_finding("Missing data.", "MISSING_REQUIRED_DATA", "Solver Owner")
    ])
    assert blocked["status"] == STATUS_BLOCKED
    assert blocked["blocked"] is True

    failed = classify_status([
        make_finding("Negative wall.", "NEGATIVE_WALL_THICKNESS", "Geometry Solver")
    ])
    assert failed["status"] == STATUS_FAIL
    assert failed["failed"] is True

    running = classify_status([], lifecycle=STATUS_RUNNING)
    assert running["status"] == STATUS_RUNNING

    not_started = classify_status([], lifecycle=STATUS_NOT_STARTED)
    assert not_started["status"] == STATUS_NOT_STARTED

    production_review = classify_status([
        make_finding("Manual review needed.", "MANUAL_REVIEW_REQUIRED", "Gate Owner")
    ], production_gate=True)
    assert production_review["status"] == STATUS_BLOCKED

    legacy = legacy_warn_to_finding(
        "Old warning string.",
        owner="Legacy Adapter",
        category="MANUAL_REVIEW_REQUIRED",
        allowlisted=True,
    )
    assert legacy["severity"] == "REVIEW_REQUIRED"

    report = build_global_status_engine_report()
    assert "GLOBAL STATUS CLASSIFICATION ENGINE" in report
    assert "CANONICAL STATUSES" in report
    assert "SAFETY RULE" in report

    output = write_global_status_engine_report()
    assert output.exists()
    assert output.parent.name == "reports"

    print("PASS_GLOBAL_STATUS_CLASSIFICATION_ENGINE_PHASE_16T3G")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
