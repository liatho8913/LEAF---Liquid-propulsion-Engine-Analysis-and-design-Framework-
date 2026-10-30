from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.reference_classification_engine_phase_16t2f1 import (
    REF_GENERATED_AUDIT_REPORT,
    REF_RUNTIME_IMPORT,
    PASS_STATUS,
    WARN_STATUS,
    classify_reference,
    build_reference_classification_audit,
    build_reference_classification_report,
    write_reference_classification_report,
)


def main() -> int:
    report_path = ROOT / "_leaf_artifacts" / "reports" / "FAKE_AUDIT_REPORT.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    ref_type, evidence = classify_reference(
        report_path,
        "phase_16a_register_result_keys.py",
        "phase_16a_register_result_keys.py",
    )
    assert ref_type == REF_GENERATED_AUDIT_REPORT

    py_path = ROOT / "fake_runtime_import.py"
    py_path.write_text("import phase_16a_register_result_keys\n", encoding="utf-8")
    try:
        ref_type, evidence = classify_reference(
            py_path,
            py_path.read_text(encoding="utf-8"),
            "phase_16a_register_result_keys.py",
        )
        assert ref_type == REF_RUNTIME_IMPORT
    finally:
        py_path.unlink(missing_ok=True)

    audit = build_reference_classification_audit()
    assert audit["status"] in {PASS_STATUS, WARN_STATUS}
    assert audit["passed"] is True
    assert "reference_type_counts" in audit

    report = build_reference_classification_report()
    assert "REFERENCE CLASSIFICATION ENGINE" in report
    assert "SAFETY RULE" in report

    output = write_reference_classification_report()
    assert output.exists()
    assert output.parent.name == "reports"

    print("PASS_REFERENCE_CLASSIFICATION_ENGINE_PHASE_16T2F1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
