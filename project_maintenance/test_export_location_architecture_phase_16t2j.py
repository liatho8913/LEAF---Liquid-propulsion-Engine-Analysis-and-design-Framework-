from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.export_location_architecture_phase_16t2j import (
    PASS_STATUS,
    ensure_export_architecture,
    export_path,
    write_text_export,
    build_export_architecture_report,
    write_export_architecture_report,
)


def main() -> int:
    audit = ensure_export_architecture()

    assert audit["status"] == PASS_STATUS
    assert audit["passed"] is True
    assert "_leaf_artifacts/exports" in audit["export_root"]

    p = export_path("regen", "Regen Final Report", ".txt")
    assert p.parent.name == "regen"
    assert "Regen_Final_Report" in p.name
    assert p.suffix == ".txt"

    written = write_text_export("audits", "Export Architecture Test", "PASS")
    assert written.exists()
    assert written.parent.name == "audits"

    report = build_export_architecture_report()
    assert "EXPORT LOCATION ARCHITECTURE" in report
    assert "FILENAME RULE" in report
    assert "SAFETY RULE" in report

    report_path = write_export_architecture_report()
    assert report_path.exists()

    print("PASS_EXPORT_LOCATION_ARCHITECTURE_PHASE_16T2J")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
