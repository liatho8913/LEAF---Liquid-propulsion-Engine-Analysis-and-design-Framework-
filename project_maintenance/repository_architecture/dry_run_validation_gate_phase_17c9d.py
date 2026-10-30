from __future__ import annotations

import json
import py_compile
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9d"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PLAN_SCRIPT = ROOT / "project_maintenance" / "repository_architecture" / "intelligence_guided_dry_run_movement_plan_phase_17c9c.py"
PLAN_JSON = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9c" / "intelligence_guided_dry_run_movement_plan_phase_17c9c.json"
ROLLBACK_JSON = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9c" / "intelligence_guided_dry_run_rollback_plan_phase_17c9c.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    warnings: list[str] = []

    try:
        py_compile.compile(str(PLAN_SCRIPT), doraise=True)
    except Exception as exc:
        failures.append(f"dry_run_plan_script_compile_failure={exc!r}")

    if not PLAN_JSON.exists():
        failures.append("phase_17c9c_plan_json_missing")

    if not ROLLBACK_JSON.exists():
        failures.append("phase_17c9c_rollback_json_missing")

    if failures:
        plan = {}
        movement_plan = []
        rollback_plan = []
    else:
        plan = load_json(PLAN_JSON)
        movement_plan = plan.get("movement_plan", [])
        rollback_plan = load_json(ROLLBACK_JSON)

    if plan and not plan.get("passed"):
        failures.append("phase_17c9c_not_passed")

    if not movement_plan:
        failures.append("movement_plan_empty")

    if not rollback_plan:
        failures.append("rollback_plan_empty")

    if len(movement_plan) != len(rollback_plan):
        failures.append("movement_and_rollback_plan_count_mismatch")

    sources = [item.get("source") for item in movement_plan]
    destinations = [item.get("destination") for item in movement_plan]

    if len(sources) != len(set(sources)):
        failures.append("duplicate_sources_detected")

    if len(destinations) != len(set(destinations)):
        failures.append("duplicate_destinations_detected")

    rollback_by_id = {
        item.get("operation_id"): item
        for item in rollback_plan
    }

    safe_count = 0
    parent_create_count = 0

    for item in movement_plan:
        operation_id = item.get("operation_id")
        source_rel = item.get("source")
        destination_rel = item.get("destination")

        source = ROOT / source_rel
        destination = ROOT / destination_rel

        if item.get("action") != "DRY_RUN_MOVE":
            failures.append(f"invalid_action={operation_id}")

        if item.get("movement_risk") != "LOW":
            failures.append(f"non_low_risk_operation={operation_id}")

        if not source.exists():
            failures.append(f"source_missing={source_rel}")

        if destination.exists():
            failures.append(f"destination_already_exists={destination_rel}")

        if item.get("safe_to_execute"):
            safe_count += 1
        else:
            failures.append(f"operation_not_safe_to_execute={operation_id}")

        if item.get("would_create_parent"):
            parent_create_count += 1

        rollback = rollback_by_id.get(operation_id)
        if rollback is None:
            failures.append(f"rollback_missing={operation_id}")
            continue

        if rollback.get("source") != destination_rel:
            failures.append(f"rollback_source_mismatch={operation_id}")

        if rollback.get("destination") != source_rel:
            failures.append(f"rollback_destination_mismatch={operation_id}")

    if parent_create_count:
        warnings.append(f"destination_parents_to_create={parent_create_count}")

    result = {
        "phase": "17C.9D",
        "feature": "DRY_RUN_VALIDATION_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "summary": {
            "movement_plan_count": len(movement_plan),
            "rollback_plan_count": len(rollback_plan),
            "safe_to_execute_count": safe_count,
            "would_create_parent_count": parent_create_count,
            "failure_count": len(failures),
            "warning_count": len(warnings),
        },
        "warnings": warnings,
        "failures": failures,
        "validated_plan": PLAN_JSON.relative_to(ROOT).as_posix() if PLAN_JSON.exists() else None,
        "validated_rollback": ROLLBACK_JSON.relative_to(ROOT).as_posix() if ROLLBACK_JSON.exists() else None,
        "completion_notice": (
            "PHASE_17C9D_COMPLETE_DRY_RUN_VALIDATION_GATE_PASSED"
            if not failures
            else "PHASE_17C9D_BLOCKED"
        ),
        "next_phase": "17C.9E_CONTROLLED_MOVEMENT_EXECUTION_GATE",
    }

    gate_json = OUT_DIR / "dry_run_validation_gate_phase_17c9d.json"
    gate_txt = OUT_DIR / "dry_run_validation_gate_phase_17c9d.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.9D DRY RUN VALIDATION GATE",
            "==========================================",
            f"passed={result['passed']}",
            f"movement_plan_count={result['summary']['movement_plan_count']}",
            f"rollback_plan_count={result['summary']['rollback_plan_count']}",
            f"safe_to_execute_count={result['summary']['safe_to_execute_count']}",
            f"would_create_parent_count={result['summary']['would_create_parent_count']}",
            f"failure_count={result['summary']['failure_count']}",
            f"warning_count={result['summary']['warning_count']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9D_DRY_RUN_VALIDATION_GATE" if result["passed"] else "FAIL_PHASE_17C9D_DRY_RUN_VALIDATION_GATE")
    print(f"movement_plan_count={result['summary']['movement_plan_count']}")
    print(f"rollback_plan_count={result['summary']['rollback_plan_count']}")
    print(f"safe_to_execute_count={result['summary']['safe_to_execute_count']}")
    print(f"would_create_parent_count={result['summary']['would_create_parent_count']}")
    print(f"failure_count={result['summary']['failure_count']}")
    print(f"warning_count={result['summary']['warning_count']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
