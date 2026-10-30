from pathlib import Path
from tempfile import TemporaryDirectory

from project_maintenance.production_historical_artifacts.leaf_qt.root_level_review.codebase_safe_cleanup_plan_phase_16t2d import (
    ARCHIVE,
    KEEP_BUT_REVIEW,
    PASS_STATUS,
    WARN_STATUS,
    build_safe_cleanup_plan,
    build_safe_cleanup_plan_report,
    classify_cleanup_action,
    write_safe_cleanup_plan_report,
)


def main() -> int:
    action, reason = classify_cleanup_action("phase_16a_register_result_keys.py")
    assert action == ARCHIVE
    assert "archive" in reason.lower()

    action, reason = classify_cleanup_action("leaf_qt/regen_geometry_preview_viewer.py")
    assert action in {KEEP_BUT_REVIEW, "KEEP"}

    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        (root / "main.py").write_text("import active_runtime\n", encoding="utf-8")
        (root / "active_runtime.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "phase_14a_register_result_keys.py").write_text("VALUE = 2\n", encoding="utf-8")
        (root / "promethean_forge.py").write_text("VALUE = 3\n", encoding="utf-8")

        plan = build_safe_cleanup_plan(root)

        assert plan["status"] in {PASS_STATUS, WARN_STATUS}
        assert plan["passed"] is True
        assert "counts" in plan
        assert "actions" in plan

        report = build_safe_cleanup_plan_report(root)
        assert "SAFE CODEBASE CLEANUP PLAN" in report
        assert "SAFETY RULE" in report

        output = write_safe_cleanup_plan_report(root, root / "cleanup_plan.txt")
        assert output.exists()

    print("PASS_CODEBASE_SAFE_CLEANUP_PLAN_PHASE_16T2D")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
