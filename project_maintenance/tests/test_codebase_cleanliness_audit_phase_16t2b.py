from pathlib import Path
from tempfile import TemporaryDirectory

from codebase_cleanliness_audit_phase_16t2b import (
    PASS_STATUS,
    WARN_STATUS,
    build_codebase_cleanliness_audit,
    build_codebase_cleanliness_report,
    write_codebase_cleanliness_report,
)


def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        (root / "main.py").write_text("import useful_module\n", encoding="utf-8")
        (root / "useful_module.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "test_useful_module.py").write_text("import useful_module\n", encoding="utf-8")

        audit = build_codebase_cleanliness_audit(root)

        assert audit["status"] in {PASS_STATUS, WARN_STATUS}
        assert audit["passed"] is True
        assert audit["python_file_count"] == 3
        assert audit["test_file_count"] == 1
        assert audit["exact_duplicate_group_count"] >= 0

        report = build_codebase_cleanliness_report(root)
        assert "PYTHON CODEBASE CLEANLINESS AUDIT" in report
        assert audit["status"] in report

    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        duplicate_source = "VALUE = 123\n"
        (root / "main.py").write_text("import active\n", encoding="utf-8")
        (root / "active.py").write_text("VALUE = 1\n", encoding="utf-8")
        (root / "module_copy.py").write_text(duplicate_source, encoding="utf-8")
        (root / "module_backup.py").write_text(duplicate_source, encoding="utf-8")

        audit = build_codebase_cleanliness_audit(root)

        assert audit["status"] == WARN_STATUS
        assert audit["passed"] is True
        assert audit["exact_duplicate_group_count"] >= 1
        assert audit["suspicious_file_count"] == 2
        assert audit["likely_unreferenced_module_count"] >= 2

        output = write_codebase_cleanliness_report(root, root / "audit.txt")
        assert output.exists()

        text = output.read_text(encoding="utf-8")
        assert "module_copy.py" in text
        assert audit["status"] in text

    print("PASS_CODEBASE_CLEANLINESS_AUDIT_PHASE_16T2B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
