from __future__ import annotations

import json
import shutil
import py_compile
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9e"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VALIDATION_JSON = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9d" / "dry_run_validation_gate_phase_17c9d.json"
PLAN_JSON = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9c" / "intelligence_guided_dry_run_movement_plan_phase_17c9c.json"
EXECUTION_SCRIPT = ROOT / "project_maintenance" / "repository_architecture" / "controlled_movement_execution_gate_phase_17c9e.py"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    executed: list[dict] = []
    skipped: list[dict] = []

    try:
        py_compile.compile(str(EXECUTION_SCRIPT), doraise=True)
    except Exception as exc:
        failures.append(f"execution_script_compile_failure={exc!r}")

    if not VALIDATION_JSON.exists():
        failures.append("phase_17c9d_validation_json_missing")

    if not PLAN_JSON.exists():
        failures.append("phase_17c9c_plan_json_missing")

    if failures:
        validation = {}
        plan = {}
        movement_plan = []
    else:
        validation = load_json(VALIDATION_JSON)
        plan = load_json(PLAN_JSON)
        movement_plan = plan.get("movement_plan", [])

    if validation and not validation.get("passed"):
        failures.append("phase_17c9d_not_passed")

    if plan and not plan.get("passed"):
        failures.append("phase_17c9c_not_passed")

    if not movement_plan:
        failures.append("movement_plan_empty")

    if failures:
        result = {
            "phase": "17C.9E",
            "feature": "CONTROLLED_MOVEMENT_EXECUTION_GATE",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "passed": False,
            "executed": executed,
            "skipped": skipped,
            "failures": failures,
            "completion_notice": "PHASE_17C9E_BLOCKED",
            "next_phase": "17C.9E_REPAIR_OR_RETRY",
        }
    else:
        for item in movement_plan:
            source_rel = item["source"]
            destination_rel = item["destination"]

            source = ROOT / source_rel
            destination = ROOT / destination_rel

            if not item.get("safe_to_execute"):
                failures.append(f"unsafe_operation_blocked={item.get('operation_id')}")
                skipped.append(item)
                continue

            if not source.exists():
                failures.append(f"source_missing={source_rel}")
                skipped.append(item)
                continue

            if destination.exists():
                failures.append(f"destination_exists={destination_rel}")
                skipped.append(item)
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))

            executed.append({
                "operation_id": item["operation_id"],
                "source": source_rel,
                "destination": destination_rel,
                "rollback_source": destination_rel,
                "rollback_destination": source_rel,
                "semantic_owner": item.get("semantic_owner"),
                "semantic_subsystem": item.get("semantic_subsystem"),
                "semantic_role": item.get("semantic_role"),
            })

        result = {
            "phase": "17C.9E",
            "feature": "CONTROLLED_MOVEMENT_EXECUTION_GATE",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "passed": not failures and len(executed) == len(movement_plan),
            "summary": {
                "planned_count": len(movement_plan),
                "executed_count": len(executed),
                "skipped_count": len(skipped),
                "failure_count": len(failures),
            },
            "executed": executed,
            "skipped": skipped,
            "failures": failures,
            "completion_notice": (
                "PHASE_17C9E_COMPLETE_CONTROLLED_MOVEMENT_EXECUTION_FINISHED"
                if not failures and len(executed) == len(movement_plan)
                else "PHASE_17C9E_BLOCKED_PARTIAL_OR_FAILED"
            ),
            "next_phase": "17C.9F_POST_MOVEMENT_ARCHITECTURE_VALIDATION",
        }

    execution_json = OUT_DIR / "controlled_movement_execution_gate_phase_17c9e.json"
    rollback_json = OUT_DIR / "controlled_movement_rollback_manifest_phase_17c9e.json"
    report_txt = OUT_DIR / "controlled_movement_execution_gate_phase_17c9e.txt"

    rollback_manifest = [
        {
            "operation_id": item["operation_id"],
            "action": "ROLLBACK_MOVE",
            "source": item["rollback_source"],
            "destination": item["rollback_destination"],
        }
        for item in executed
    ]

    execution_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    rollback_json.write_text(json.dumps(rollback_manifest, indent=2), encoding="utf-8")

    summary = result.get("summary", {
        "planned_count": len(movement_plan),
        "executed_count": len(executed),
        "skipped_count": len(skipped),
        "failure_count": len(failures),
    })

    report_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.9E CONTROLLED MOVEMENT EXECUTION GATE",
            "=====================================================",
            f"passed={result['passed']}",
            f"planned_count={summary['planned_count']}",
            f"executed_count={summary['executed_count']}",
            f"skipped_count={summary['skipped_count']}",
            f"failure_count={summary['failure_count']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={execution_json.relative_to(ROOT)}",
            f"rollback_json={rollback_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9E_CONTROLLED_MOVEMENT_EXECUTION_GATE" if result["passed"] else "FAIL_PHASE_17C9E_CONTROLLED_MOVEMENT_EXECUTION_GATE")
    print(f"planned_count={summary['planned_count']}")
    print(f"executed_count={summary['executed_count']}")
    print(f"skipped_count={summary['skipped_count']}")
    print(f"failure_count={summary['failure_count']}")
    print(f"report={report_txt.relative_to(ROOT)}")
    print(f"json={execution_json.relative_to(ROOT)}")
    print(f"rollback_json={rollback_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
