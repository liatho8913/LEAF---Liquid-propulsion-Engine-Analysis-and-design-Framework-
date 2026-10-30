from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.duplicate_functionality_detection_engine import (
    write_duplicate_functionality_report,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c10a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "duplicate_functionality_detection_engine.py"
SCHEMA = "LEAF_DUPLICATE_FUNCTIONALITY_DETECTION_GATE_PHASE_17C10A_V1"


def main() -> None:
    failures: list[str] = []
    warnings: list[str] = []

    try:
        py_compile.compile(str(ENGINE), doraise=True)
    except Exception as exc:
        failures.append(f"compile_failure={ENGINE.relative_to(ROOT)}:{exc!r}")

    report = write_duplicate_functionality_report(ROOT)
    summary = report["summary"]

    if summary["active_python_files_scanned"] <= 0:
        failures.append("no_active_python_files_scanned")

    if summary["function_signatures"] <= 0:
        failures.append("no_function_signatures_detected")

    if report["mode"] != "PROOF_ONLY_NO_MOVE_NO_ARCHIVE_NO_DELETE":
        failures.append("not_proof_only_mode")

    if summary["automatic_move_allowed"]:
        failures.append("automatic_move_enabled")

    if summary["automatic_archive_allowed"]:
        failures.append("automatic_archive_enabled")

    if summary["automatic_delete_allowed"]:
        failures.append("automatic_delete_enabled")

    if summary["high_confidence_group_count"] == 0:
        warnings.append("no_high_confidence_duplicates_found")

    result = {
        "phase": "17C.10A",
        "feature": "DUPLICATE_FUNCTIONALITY_DETECTION",
        "schema": SCHEMA,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "summary": summary,
        "safety_policy": report["safety_policy"],
        "warnings": warnings,
        "failures": failures,
        "artefacts": report["artefacts"],
        "completion_notice": (
            "PHASE_17C10A_COMPLETE_DUPLICATE_FUNCTIONALITY_DETECTION_ESTABLISHED"
            if not failures
            else "PHASE_17C10A_BLOCKED"
        ),
        "next_phase": "17C.10B_UNUSED_FILE_PROOF_ENGINE",
    }

    json_path = OUT_DIR / "duplicate_functionality_detection_gate_phase_17c10a.json"
    txt_path = OUT_DIR / "duplicate_functionality_detection_gate_phase_17c10a.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.10A DUPLICATE FUNCTIONALITY DETECTION GATE",
            "==============================================================",
            f"passed={result['passed']}",
            f"active_python_files_scanned={summary['active_python_files_scanned']}",
            f"function_signatures={summary['function_signatures']}",
            f"duplicate_group_count={summary['duplicate_group_count']}",
            f"high_confidence_group_count={summary['high_confidence_group_count']}",
            f"medium_confidence_group_count={summary['medium_confidence_group_count']}",
            f"affected_file_count={summary['affected_file_count']}",
            f"automatic_move_allowed={summary['automatic_move_allowed']}",
            f"automatic_archive_allowed={summary['automatic_archive_allowed']}",
            f"automatic_delete_allowed={summary['automatic_delete_allowed']}",
            f"warnings={len(warnings)}",
            f"failures={len(failures)}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"report={txt_path.relative_to(ROOT)}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C10A_DUPLICATE_FUNCTIONALITY_DETECTION" if result["passed"] else "FAIL_PHASE_17C10A_DUPLICATE_FUNCTIONALITY_DETECTION")
    print(f"active_python_files_scanned={summary['active_python_files_scanned']}")
    print(f"function_signatures={summary['function_signatures']}")
    print(f"duplicate_group_count={summary['duplicate_group_count']}")
    print(f"high_confidence_group_count={summary['high_confidence_group_count']}")
    print(f"medium_confidence_group_count={summary['medium_confidence_group_count']}")
    print(f"affected_file_count={summary['affected_file_count']}")
    print(f"automatic_move_allowed={summary['automatic_move_allowed']}")
    print(f"automatic_archive_allowed={summary['automatic_archive_allowed']}")
    print(f"automatic_delete_allowed={summary['automatic_delete_allowed']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
