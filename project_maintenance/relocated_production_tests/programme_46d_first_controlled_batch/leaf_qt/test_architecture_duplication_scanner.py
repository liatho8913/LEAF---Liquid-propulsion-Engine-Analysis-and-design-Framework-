from pathlib import Path
import tempfile

from core.architecture.duplication import (
    scan_file_for_architecture_duplication,
    build_architecture_duplication_report,
    build_duplication_text_report,
)


def test_duplication_scanner_detects_manual_json_and_write_text():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "tool.py"
        target.write_text(
            "import json\n"
            "payload = json.loads('{}')\n"
            "text = json.dumps(payload)\n"
            "path.parent.mkdir(parents=True, exist_ok=True)\n"
            "path.write_text(text)\n",
            encoding="utf-8",
        )

        findings = scan_file_for_architecture_duplication(target, root)
        codes = {finding.code for finding in findings}

        assert "MANUAL_WRITE_TEXT" in codes
        assert "MANUAL_PARENT_MKDIR" in codes


def test_architecture_duplication_report_scans_leaf_qt_only():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "leaf_qt").mkdir()
        (root / "other").mkdir()

        (root / "leaf_qt" / "tool.py").write_text(
            "path.write_text('x')\n",
            encoding="utf-8",
        )

        (root / "other" / "ignored.py").write_text(
            "path.write_text('x')\n",
            encoding="utf-8",
        )

        report = build_architecture_duplication_report(root)

        assert report.schema == "LEAF_ARCHITECTURE_DUPLICATION_REPORT_V1"
        assert report.summary["files_with_findings"] == 1
        assert report.findings[0].path == "leaf_qt/tool.py"


def test_architecture_duplication_report_ignores_tests_by_default():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "leaf_qt").mkdir()

        (root / "leaf_qt" / "test_tool.py").write_text(
            "path.write_text('fixture')\n",
            encoding="utf-8",
        )

        report = build_architecture_duplication_report(root)

        assert report.summary["files_with_findings"] == 0
        assert report.summary["findings"] == 0


def test_architecture_duplication_report_can_include_tests_when_requested():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "leaf_qt").mkdir()

        (root / "leaf_qt" / "test_tool.py").write_text(
            "path.write_text('fixture')\n",
            encoding="utf-8",
        )

        report = build_architecture_duplication_report(root, include_tests=True)

        assert report.summary["files_with_findings"] == 1
        assert report.findings[0].path == "leaf_qt/test_tool.py"


def test_duplication_text_report_contains_counts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "leaf_qt").mkdir()
        (root / "leaf_qt" / "tool.py").write_text(
            "path.write_text('x')\n",
            encoding="utf-8",
        )

        report = build_architecture_duplication_report(root)
        text = build_duplication_text_report(report)

        assert "LEAF ARCHITECTURE DUPLICATION REPORT" in text
        assert "MANUAL_WRITE_TEXT" in text


if __name__ == "__main__":
    test_duplication_scanner_detects_manual_json_and_write_text()
    test_architecture_duplication_report_scans_leaf_qt_only()
    test_architecture_duplication_report_ignores_tests_by_default()
    test_architecture_duplication_report_can_include_tests_when_requested()
    test_duplication_text_report_contains_counts()
    print("PASS_ARCHITECTURE_DUPLICATION_SCANNER_TEST")
