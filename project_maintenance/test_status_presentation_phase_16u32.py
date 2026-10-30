from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.status_presentation import (
    LegacyCompatibilityProducer,
    ReportFilterModel,
    ReportStatusPresenter,
    StatusVisualStyle,
    StructuredStatusRenderer,
    display_status,
    present_finding,
    present_status,
    should_show_for_filter,
    status_badge,
    status_colour_role,
    status_icon,
    status_severity,
)


PASS_BANNER = "PASS_PHASE_16U32_SHARED_STATUS_PRESENTATION_LAYER"


def test_status_presentation_phase_16u32():
    assert status_severity("PASS") == "PASS"
    assert status_severity("PASS_WITH_WARNINGS") == "WARN"
    assert status_severity("WARN") == "WARN"
    assert status_severity("FAIL") == "FAIL"
    assert status_severity("BLOCKED") == "FAIL"
    assert status_severity(None) == "UNKNOWN"

    assert display_status("PASS") == "PASS"
    assert display_status("FAIL") == "FAIL"
    assert display_status("WARN") == "REVIEW"

    assert status_colour_role("PASS") == "success"
    assert status_colour_role("WARN") == "warning"
    assert status_colour_role("FAIL") == "danger"

    assert status_icon("PASS") == "✓"
    assert status_icon("WARN") == "!"
    assert status_icon("FAIL") == "✕"

    assert status_badge("PASS").endswith("PASS")
    assert present_status("FAIL").is_negative is True
    assert present_status("PASS").is_positive is True
    assert present_status("WARN").is_attention is True

    assert present_finding({"severity": "FAIL"}).severity == "FAIL"
    assert present_finding({"status": "PASS"}).severity == "PASS"
    assert present_finding({"passed": False}).severity == "FAIL"

    assert StructuredStatusRenderer.severity("BLOCKED") == "FAIL"
    assert StatusVisualStyle.colour_role("PASS") == "success"

    assert ReportStatusPresenter.render_check({"name": "Example", "passed": True}) == "Example: ✓ PASS"

    assert ReportFilterModel.options() == ["FAIL", "WARN", "PASS", "UNKNOWN", "NOT_AVAILABLE"]
    assert should_show_for_filter("FAIL", "FAIL") is True
    assert should_show_for_filter("PASS", "FAIL") is False
    assert should_show_for_filter("MISSING", "NOT_AVAILABLE") is True

    assert LegacyCompatibilityProducer.status_from_bool(True) == "PASS"
    assert LegacyCompatibilityProducer.status_from_bool(False) == "FAIL"


if __name__ == "__main__":
    test_status_presentation_phase_16u32()
    print(PASS_BANNER)
