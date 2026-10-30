from pathlib import Path
import tempfile

from project_maintenance.production_historical_artifacts.leaf_qt.repository_source_truth_audit import (
    build_repository_source_truth_audit,
    build_text_report,
)


def test_repository_source_truth_audit_detects_uploaded_source_tree():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        (root / "leaf_qt").mkdir()
        (root / "leaf_qt" / "engine_solver.py").write_text(
            "def live():\n"
            "    return True\n",
            encoding="utf-8",
        )

        (root / "LEAF_UPLOAD" / "leaf_qt").mkdir(parents=True)
        (root / "LEAF_UPLOAD" / "leaf_qt" / "engine_solver.py").write_text(
            "def copied():\n"
            "    return False\n",
            encoding="utf-8",
        )

        audit = build_repository_source_truth_audit(root)

        assert audit["schema"] == "LEAF_REPOSITORY_SOURCE_TRUTH_AUDIT_V1"
        assert audit["passed"] is False
        assert audit["summary"]["blocking_findings"] == 1
        assert audit["summary"]["suspicious_python_files"] == 1
        assert audit["findings"][0]["path"] == "LEAF_UPLOAD"


def test_repository_source_truth_audit_passes_clean_tree():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        (root / "leaf_qt").mkdir()
        (root / "leaf_qt" / "engine_solver.py").write_text(
            "def live():\n"
            "    return True\n",
            encoding="utf-8",
        )

        audit = build_repository_source_truth_audit(root)

        assert audit["passed"] is True
        assert audit["summary"]["blocking_findings"] == 0


def test_repository_source_truth_audit_report_contains_status():
    audit = {
        "schema": "LEAF_REPOSITORY_SOURCE_TRUTH_AUDIT_V1",
        "passed": True,
        "summary": {
            "findings": 0,
            "blocking_findings": 0,
            "suspicious_python_files": 0,
        },
        "findings": [],
    }

    report = build_text_report(audit)

    assert "LEAF REPOSITORY SOURCE TRUTH AUDIT" in report
    assert "passed=True" in report


if __name__ == "__main__":
    test_repository_source_truth_audit_detects_uploaded_source_tree()
    test_repository_source_truth_audit_passes_clean_tree()
    test_repository_source_truth_audit_report_contains_status()
    print("PASS_REPOSITORY_SOURCE_TRUTH_AUDIT_TEST")
