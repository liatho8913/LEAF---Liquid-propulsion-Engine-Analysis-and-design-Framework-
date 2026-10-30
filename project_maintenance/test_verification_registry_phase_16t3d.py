from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.verification_registry_phase_16t3d import (
    PASS_STATUS,
    WARN_STATUS,
    REGISTRY_PATH,
    build_verification_registry,
    build_verification_registry_report,
    write_verification_registry_report,
)


def main() -> int:
    registry = build_verification_registry()

    assert registry["status"] in {PASS_STATUS, WARN_STATUS}
    assert registry["passed"] is True
    assert registry["record_count"] >= 1
    assert "records" in registry

    first = registry["records"][0]
    required_keys = {
        "id",
        "phase",
        "filename",
        "source_path",
        "target_path",
        "domain",
        "subsystem",
        "owner",
        "lifecycle",
        "permanent",
        "can_archive",
        "exists",
        "command",
        "last_result",
    }

    assert required_keys.issubset(first.keys())
    assert REGISTRY_PATH.exists()

    report = build_verification_registry_report()

    assert "VERIFICATION REGISTRY & METADATA SYSTEM" in report
    assert "DOMAIN COUNTS" in report
    assert "LIFECYCLE COUNTS" in report
    assert "SAFETY RULE" in report

    report_path = write_verification_registry_report()

    assert report_path.exists()
    assert report_path.parent.name == "reports"

    print("PASS_VERIFICATION_REGISTRY_PHASE_16T3D")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
