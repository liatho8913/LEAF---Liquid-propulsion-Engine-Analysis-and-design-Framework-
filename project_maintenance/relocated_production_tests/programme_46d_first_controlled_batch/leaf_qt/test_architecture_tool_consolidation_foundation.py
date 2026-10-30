from pathlib import Path
import tempfile

from core.architecture.models import ArchitectureFinding, ArchitectureReport
from core.architecture.io import write_json_artifact, read_json_artifact, write_text_artifact
from core.architecture.reporting import build_standard_architecture_text_report


def test_architecture_report_model_passes_when_findings_pass():
    report = ArchitectureReport(
        schema="TEST_SCHEMA_V1",
        title="TEST REPORT",
        summary={"checks": 1},
        findings=[
            ArchitectureFinding(
                status="PASS",
                code="OK",
                message="Everything passed.",
                path="leaf_qt/example.py",
            )
        ],
    )

    data = report.to_dict()

    assert report.passed is True
    assert data["passed"] is True
    assert data["schema"] == "TEST_SCHEMA_V1"
    assert data["findings"][0]["path"] == "leaf_qt/example.py"


def test_architecture_report_model_fails_when_finding_fails():
    report = ArchitectureReport(
        schema="TEST_SCHEMA_V1",
        title="TEST REPORT",
        summary={"checks": 1},
        findings=[
            ArchitectureFinding(
                status="FAIL",
                code="BROKEN",
                message="Something failed.",
            )
        ],
    )

    assert report.passed is False
    assert report.to_dict()["passed"] is False


def test_architecture_artifact_io_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        json_path = root / "artifacts" / "report.json"
        txt_path = root / "artifacts" / "report.txt"

        write_json_artifact({"schema": "X", "value": 1}, json_path)
        loaded = read_json_artifact(json_path)

        write_text_artifact("hello", txt_path)

        assert loaded["schema"] == "X"
        assert loaded["value"] == 1
        assert txt_path.read_text(encoding="utf-8") == "hello"


def test_standard_architecture_text_report():
    report = ArchitectureReport(
        schema="TEST_SCHEMA_V1",
        title="TEST REPORT",
        summary={"files": 2},
        findings=[
            ArchitectureFinding(
                status="PASS",
                code="CHECKED",
                message="Checked successfully.",
                path="leaf_qt/a.py",
            )
        ],
        safe_to_modify_files=False,
    )

    text = build_standard_architecture_text_report(report)

    assert "TEST REPORT" in text
    assert "schema=TEST_SCHEMA_V1" in text
    assert "files=2" in text
    assert "PASS | CHECKED" in text


if __name__ == "__main__":
    test_architecture_report_model_passes_when_findings_pass()
    test_architecture_report_model_fails_when_finding_fails()
    test_architecture_artifact_io_roundtrip()
    test_standard_architecture_text_report()
    print("PASS_ARCHITECTURE_TOOL_CONSOLIDATION_FOUNDATION_TEST")
