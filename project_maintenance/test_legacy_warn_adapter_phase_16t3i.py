from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.global_status_classification_engine_phase_16t3g import (
    STATUS_REVIEW_REQUIRED,
    STATUS_BLOCKED,
    STATUS_FAIL,
)
from project_maintenance.legacy_warn_adapter_phase_16t3i import (
    infer_category_from_legacy_warning,
    adapt_legacy_warning,
    adapt_legacy_status_payload,
    build_legacy_warn_adapter_report,
    write_legacy_warn_adapter_report,
)


def main() -> int:
    assert infer_category_from_legacy_warning("WARN_REGEN_CONVERGENCE_RUNNING") == "MANUAL_REVIEW_REQUIRED"
    assert infer_category_from_legacy_warning("WARN_REGEN_CONVERGENCE_MAX_GENERATIONS_REACHED") == "MAX_GENERATIONS_REACHED"
    assert infer_category_from_legacy_warning("WARN_IMPORT_FAILED_PHASE_16N6") == "BROKEN_IMPORT"
    assert infer_category_from_legacy_warning("WARN_NO_STATION_PROFILE") == "NO_STATION_PROFILE"
    assert infer_category_from_legacy_warning("NEGATIVE_WALL_THICKNESS_WARNING") == "PHYSICS_INVALID"

    review = adapt_legacy_warning(
        "WARN_REGEN_CONVERGENCE_RUNNING",
        owner="Convergence Owner",
    )
    assert review["category"] == "MANUAL_REVIEW_REQUIRED"
    assert review["severity"] == "REVIEW_REQUIRED"

    blocked_payload = adapt_legacy_status_payload(
        {
            "status": "WARN_OLD",
            "warnings": ["WARN_NO_STATION_PROFILE"],
        },
        owner="Viewer Owner",
    )
    assert blocked_payload["global_status"] == STATUS_BLOCKED

    review_payload = adapt_legacy_status_payload(
        {
            "status": "WARN_OLD",
            "warnings": ["WARN_REGEN_CONVERGENCE_MAX_GENERATIONS_REACHED"],
        },
        owner="Convergence Owner",
    )
    assert review_payload["global_status"] == STATUS_REVIEW_REQUIRED

    fail_payload = adapt_legacy_status_payload(
        {
            "status": "WARN_OLD",
            "warnings": ["NEGATIVE_WALL_THICKNESS_WARNING"],
        },
        owner="Geometry Solver",
    )
    assert fail_payload["global_status"] == STATUS_FAIL

    report = build_legacy_warn_adapter_report()
    assert "LEGACY WARN ADAPTER UTILITY" in report
    assert "EXAMPLE ADAPTATION" in report
    assert "SAFETY RULE" in report

    output = write_legacy_warn_adapter_report()
    assert output.exists()
    assert output.parent.name == "reports"

    print("PASS_LEGACY_WARN_ADAPTER_PHASE_16T3I")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
