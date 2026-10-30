from pathlib import Path
from tempfile import TemporaryDirectory

from codebase_project_intelligence_audit_phase_16t2c import (
    ACTIVE_SOURCE,
    ARCHIVE_OR_UPLOAD_COPY,
    PASS_STATUS,
    WARN_STATUS,
    build_project_intelligence_audit,
    build_project_intelligence_report,
    write_project_intelligence_report,
)


def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        (root / "main.py").write_text("import engine_solver\n", encoding="utf-8")
        (root / "engine_solver.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "test_engine_solver.py").write_text("import engine_solver\n", encoding="utf-8")

        archive = root / "LEAF_UPLOAD"
        archive.mkdir()
        (archive / "engine_solver.py").write_text("VALUE = 1\n", encoding="utf-8")

        audit = build_project_intelligence_audit(root)

        assert audit["status"] in {PASS_STATUS, WARN_STATUS}
        assert audit["passed"] is True
        assert audit["python_file_count"] == 4
        assert audit["category_counts"][ACTIVE_SOURCE] == 2
        assert audit["category_counts"][ARCHIVE_OR_UPLOAD_COPY] == 1
        assert audit["all_duplicate_group_count"] >= 1
        assert audit["active_duplicate_group_count"] == 0
        assert audit["archive_or_upload_duplicate_count"] >= 1

        report = build_project_intelligence_report(root)
        assert "PROJECT-AWARE CODE INTELLIGENCE AUDIT" in report
        assert "Archive/upload duplicate groups ignored" in report

        output = write_project_intelligence_report(root, root / "report.txt")
        assert output.exists()

    print("PASS_CODEBASE_PROJECT_INTELLIGENCE_AUDIT_PHASE_16T2C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
