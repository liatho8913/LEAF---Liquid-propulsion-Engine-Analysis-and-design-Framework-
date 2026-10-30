from pathlib import Path
from tempfile import TemporaryDirectory
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.maintenance_workspace_architecture_phase_16t2h1 import (
    PASS_STATUS,
    ensure_maintenance_workspace_architecture,
    build_maintenance_workspace_architecture_report,
    write_maintenance_workspace_architecture_report,
)


def main() -> int:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)

        audit = ensure_maintenance_workspace_architecture(root)

        assert audit["status"] == PASS_STATUS
        assert audit["passed"] is True
        assert (root / "project_maintenance" / "audits" / "__init__.py").exists()
        assert (root / "project_maintenance" / "cleanup" / "__init__.py").exists()
        assert (root / "_leaf_artifacts" / "reports").is_dir()
        assert (root / "_leaf_artifacts" / "zips").is_dir()
        assert (root / "_leaf_archive" / "legacy_python").is_dir()

        report = build_maintenance_workspace_architecture_report(root)
        assert "MAINTENANCE WORKSPACE ARCHITECTURE" in report
        assert "SAFETY RULE" in report

        output = write_maintenance_workspace_architecture_report(root)
        assert output.exists()
        assert output.parent.name == "reports"

    print("PASS_MAINTENANCE_WORKSPACE_ARCHITECTURE_PHASE_16T2H1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
