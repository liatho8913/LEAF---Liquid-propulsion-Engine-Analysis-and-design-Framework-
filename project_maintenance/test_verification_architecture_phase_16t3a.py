from pathlib import Path
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.verification_architecture_phase_16t3a import (
    PASS_STATUS,
    ensure_verification_architecture,
    verification_domain_manifest,
    build_verification_architecture_report,
    write_verification_architecture_report,
)


def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        audit = ensure_verification_architecture(root)

        assert audit["status"] == PASS_STATUS
        assert audit["passed"] is True
        assert (root / "verification" / "regression" / "__init__.py").exists()
        assert (root / "verification" / "engineering" / "regen" / "__init__.py").exists()
        assert (root / "verification" / "certification" / "rl10" / "__init__.py").exists()
        assert (root / "verification" / "production_gates" / "__init__.py").exists()

        manifest = verification_domain_manifest()
        assert "engineering" in manifest
        assert "certification" in manifest
        assert "regression" in manifest

        report = build_verification_architecture_report(root)
        assert "VERIFICATION ARCHITECTURE FOUNDATION" in report
        assert "VERIFICATION DOMAINS" in report
        assert "SAFETY RULE" in report

        output = write_verification_architecture_report(root)
        assert output.exists()
        assert output.parent.name == "reports"

    print("PASS_VERIFICATION_ARCHITECTURE_PHASE_16T3A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
