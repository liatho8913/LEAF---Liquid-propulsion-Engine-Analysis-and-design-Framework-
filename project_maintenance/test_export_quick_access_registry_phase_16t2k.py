from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.export_quick_access_registry_phase_16t2k import (
    PASS_STATUS,
    ensure_registry_architecture,
    register_export,
    recent_exports,
    build_export_quick_access_report,
    write_export_quick_access_report,
)


def main() -> int:
    audit = ensure_registry_architecture()

    assert audit["status"] == PASS_STATUS
    assert audit["passed"] is True
    assert "_leaf_artifacts/exports/_registry" in audit["registry_path"]

    sample = ROOT / "_leaf_artifacts" / "exports" / "reports" / "test_export_registry_sample.txt"
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_text("sample", encoding="utf-8")

    record = register_export(
        sample,
        category="reports",
        label="Test Export Registry Sample",
        export_type="TXT",
        source="test",
    )

    assert record["category"] == "reports"
    assert record["exists"] is True

    recent = recent_exports(limit=5)
    assert recent
    assert any(item["label"] == "Test Export Registry Sample" for item in recent)

    report = build_export_quick_access_report()
    assert "EXPORT QUICK ACCESS REGISTRY" in report
    assert "RECENT EXPORTS" in report
    assert "SAFETY RULE" in report

    report_path = write_export_quick_access_report()
    assert report_path.exists()
    assert report_path.parent.name == "audits"

    print("PASS_EXPORT_QUICK_ACCESS_REGISTRY_PHASE_16T2K")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
