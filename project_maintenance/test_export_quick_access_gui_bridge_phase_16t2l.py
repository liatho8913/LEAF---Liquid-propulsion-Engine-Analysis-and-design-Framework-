from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.export_quick_access_gui_bridge_phase_16t2l import (
    PASS_STATUS,
    export_category_rows,
    recent_export_rows,
    gui_bridge_payload,
    build_export_gui_bridge_report,
    write_export_gui_bridge_report,
)


def main() -> int:
    categories = export_category_rows()

    assert categories
    assert any(row["category"] == "regen" for row in categories)
    assert all("label" in row for row in categories)
    assert all("relative_folder" in row for row in categories)

    recent = recent_export_rows(limit=10)
    assert isinstance(recent, list)

    payload = gui_bridge_payload(limit=10)

    assert payload["status"] == PASS_STATUS
    assert payload["passed"] is True
    assert payload["category_count"] >= 8
    assert "recent_exports" in payload

    report = build_export_gui_bridge_report()

    assert "EXPORT QUICK ACCESS GUI BRIDGE" in report
    assert "EXPORT CATEGORY BUTTONS" in report
    assert "SAFETY RULE" in report

    report_path = write_export_gui_bridge_report()

    assert report_path.exists()
    assert report_path.parent.name == "audits"

    print("PASS_EXPORT_QUICK_ACCESS_GUI_BRIDGE_PHASE_16T2L")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
