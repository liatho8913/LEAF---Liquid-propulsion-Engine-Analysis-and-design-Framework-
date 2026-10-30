from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_scan_controller_phase_17c11a import (
    write_snapshot_report,
)

ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "repository_scan_controller_phase_17c11a.py"
OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c11a"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(ENGINE), doraise=True)
    except Exception as exc:
        failures.append(f"compile_failure={exc!r}")

    snapshot = write_snapshot_report()
    s = snapshot["summary"]

    if not s["single_scan_complete"]:
        failures.append("single_scan_not_complete")

    if not s["shared_snapshot_available"]:
        failures.append("shared_snapshot_not_available")

    if s["total_files"] <= 0:
        failures.append("no_files_scanned")

    if s["python_files"] <= 0:
        failures.append("no_python_files_scanned")

    if not snapshot.get("files"):
        failures.append("snapshot_file_records_missing")

    passed = not failures

    gate = {
        "phase": "17C.11A",
        "feature": "REPOSITORY_SCAN_CONTROLLER_FOUNDATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": passed,
        "summary": s,
        "failures": failures,
        "completion_notice": (
            "PHASE_17C11A_COMPLETE_REPOSITORY_SCAN_CONTROLLER_FOUNDATION_ESTABLISHED"
            if passed else "PHASE_17C11A_BLOCKED"
        ),
        "next_phase": "17C.11B_SHARED_SNAPSHOT_CONSUMER_ADAPTER",
        "source_report": snapshot["artefacts"],
    }

    json_path = OUT / "repository_scan_controller_gate_phase_17c11a.json"
    txt_path = OUT / "repository_scan_controller_gate_phase_17c11a.txt"

    json_path.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.11A REPOSITORY SCAN CONTROLLER GATE",
            "====================================================",
            f"passed={passed}",
            f"total_files={s['total_files']}",
            f"python_files={s['python_files']}",
            f"top_level_owner_count={s['top_level_owner_count']}",
            f"suffix_count={s['suffix_count']}",
            f"single_scan_complete={s['single_scan_complete']}",
            f"shared_snapshot_available={s['shared_snapshot_available']}",
            f"failures={len(failures)}",
            f"completion_notice={gate['completion_notice']}",
            f"next_phase={gate['next_phase']}",
            f"report={txt_path.relative_to(ROOT)}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C11A_REPOSITORY_SCAN_CONTROLLER" if passed else "FAIL_PHASE_17C11A_REPOSITORY_SCAN_CONTROLLER")
    print(f"total_files={s['total_files']}")
    print(f"python_files={s['python_files']}")
    print(f"top_level_owner_count={s['top_level_owner_count']}")
    print(f"suffix_count={s['suffix_count']}")
    print(f"single_scan_complete={s['single_scan_complete']}")
    print(f"shared_snapshot_available={s['shared_snapshot_available']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
