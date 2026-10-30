from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_intelligence_api import RepositoryIntelligenceAPI
from project_maintenance.repository_architecture.repository_architecture_validator import build_architecture_validation

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9f"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXECUTION_JSON = ROOT / "_leaf_artifacts/repository_architecture/phase_17c9e/controlled_movement_execution_gate_phase_17c9e.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    compile_failures: list[str] = []

    if not EXECUTION_JSON.exists():
        failures.append("phase_17c9e_execution_json_missing")
        execution = {}
        executed = []
    else:
        execution = load_json(EXECUTION_JSON)
        executed = execution.get("executed", [])

    if execution and not execution.get("passed"):
        failures.append("phase_17c9e_not_passed")

    if not executed:
        failures.append("no_executed_moves_to_validate")

    for item in executed:
        destination = ROOT / item["destination"]
        source = ROOT / item["source"]

        if not destination.exists():
            failures.append(f"moved_destination_missing={item['destination']}")

        if source.exists():
            failures.append(f"old_source_still_exists={item['source']}")

        if destination.exists() and destination.suffix == ".py":
            try:
                py_compile.compile(str(destination), doraise=True)
            except Exception as exc:
                compile_failures.append(f"{item['destination']}:{exc!r}")

    if compile_failures:
        failures.append("moved_python_compile_failures_present")

    validation = build_architecture_validation(ROOT)
    api = RepositoryIntelligenceAPI(ROOT)
    summary = api.summary()

    if validation["summary"]["error_count"] != 0:
        failures.append("architecture_errors_present_after_movement")

    missing_from_api = []
    for item in executed:
        explanation = api.explain_file(item["destination"])
        if not explanation.get("found"):
            missing_from_api.append(item["destination"])

    if missing_from_api:
        failures.append("moved_files_missing_from_repository_intelligence_api")

    result = {
        "phase": "17C.9F",
        "feature": "POST_MOVEMENT_ARCHITECTURE_VALIDATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "summary": {
            "executed_move_count": len(executed),
            "moved_python_compile_failures": len(compile_failures),
            "architecture_errors": validation["summary"]["error_count"],
            "architecture_warnings": validation["summary"]["warning_count"],
            "repository_supported_files": summary["supported_files"],
            "repository_python_files": summary["python_files"],
            "file_nodes": summary["file_nodes"],
            "missing_from_api_count": len(missing_from_api),
            "failure_count": len(failures),
        },
        "compile_failures": compile_failures,
        "missing_from_api": missing_from_api,
        "failures": failures,
        "completion_notice": (
            "PHASE_17C9F_COMPLETE_POST_MOVEMENT_ARCHITECTURE_VALIDATION_PASSED"
            if not failures
            else "PHASE_17C9F_BLOCKED"
        ),
        "next_phase": "17C.9G_IMPORT_REWRITE_PLANNING_GATE",
    }

    json_path = OUT_DIR / "post_movement_architecture_validation_phase_17c9f.json"
    txt_path = OUT_DIR / "post_movement_architecture_validation_phase_17c9f.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.9F POST-MOVEMENT ARCHITECTURE VALIDATION",
            "=========================================================",
            f"passed={result['passed']}",
            f"executed_move_count={result['summary']['executed_move_count']}",
            f"moved_python_compile_failures={result['summary']['moved_python_compile_failures']}",
            f"architecture_errors={result['summary']['architecture_errors']}",
            f"architecture_warnings={result['summary']['architecture_warnings']}",
            f"repository_supported_files={result['summary']['repository_supported_files']}",
            f"repository_python_files={result['summary']['repository_python_files']}",
            f"file_nodes={result['summary']['file_nodes']}",
            f"missing_from_api_count={result['summary']['missing_from_api_count']}",
            f"failure_count={result['summary']['failure_count']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9F_POST_MOVEMENT_ARCHITECTURE_VALIDATION" if result["passed"] else "FAIL_PHASE_17C9F_POST_MOVEMENT_ARCHITECTURE_VALIDATION")
    print(f"executed_move_count={result['summary']['executed_move_count']}")
    print(f"moved_python_compile_failures={result['summary']['moved_python_compile_failures']}")
    print(f"architecture_errors={result['summary']['architecture_errors']}")
    print(f"architecture_warnings={result['summary']['architecture_warnings']}")
    print(f"missing_from_api_count={result['summary']['missing_from_api_count']}")
    print(f"failure_count={result['summary']['failure_count']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
