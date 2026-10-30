from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from project_maintenance.production_historical_artifacts.leaf_qt.presentation_layer_repository_audit_owner import write_audit_outputs


if __name__ == "__main__":
    result = write_audit_outputs(ROOT)

    print(result["status"])
    print(f"scanned_files={result['scanned_files']}")
    print(f"finding_count={result['finding_count']}")
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"text_report={result['text_report']}")
    print(f"json_report={result['json_report']}")

    if not result["passed"]:
        raise SystemExit(1)
