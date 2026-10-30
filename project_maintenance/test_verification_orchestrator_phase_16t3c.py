from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.verification_orchestrator_phase_16t3c import (
    PASS_STATUS,
    WARN_STATUS,
    load_verification_classification_map,
    build_verification_suite_index,
    build_orchestrator_plan,
    build_orchestrator_report,
    write_orchestrator_report,
)


def main() -> int:
    rows = load_verification_classification_map()
    assert isinstance(rows, list)

    suites = build_verification_suite_index()
    assert isinstance(suites, dict)
    assert "engineering_regen" in suites
    assert "ui" in suites
    assert "production_gates" in suites

    plan = build_orchestrator_plan()

    assert plan["status"] in {PASS_STATUS, WARN_STATUS}
    assert plan["passed"] is True
    assert plan["test_count"] >= 1
    assert "suites" in plan

    regen_plan = build_orchestrator_plan("engineering_regen")
    assert regen_plan["selected_domain"] == "engineering_regen"
    assert regen_plan["passed"] is True

    report = build_orchestrator_report()
    assert "VERIFICATION ORCHESTRATOR FOUNDATION" in report
    assert "DOMAIN EXECUTION PLAN" in report
    assert "SAFETY RULE" in report

    report_path = write_orchestrator_report()
    assert report_path.exists()
    assert report_path.parent.name == "reports"

    print("PASS_VERIFICATION_ORCHESTRATOR_PHASE_16T3C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
