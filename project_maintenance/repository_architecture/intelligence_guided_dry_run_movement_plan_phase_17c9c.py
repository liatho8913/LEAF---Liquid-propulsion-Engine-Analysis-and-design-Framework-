from __future__ import annotations

import json
import py_compile
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9c"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PLANNING_GATE = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9b" / "intelligence_guided_sorter_planning_gate_phase_17c9b.json"
APPROVED_BATCH = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9b" / "approved_intelligence_guided_sorter_batch_phase_17c9b.json"
PLANNING_SCRIPT = ROOT / "project_maintenance" / "repository_architecture" / "intelligence_guided_sorter_planning_gate_phase_17c9b.py"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    failures: list[str] = []
    warnings: list[str] = []

    try:
        py_compile.compile(str(PLANNING_SCRIPT), doraise=True)
    except Exception as exc:
        failures.append(f"planning_gate_compile_failure={exc!r}")

    if not PLANNING_GATE.exists():
        failures.append("phase_17c9b_gate_json_missing")

    if not APPROVED_BATCH.exists():
        failures.append("phase_17c9b_approved_batch_json_missing")

    if failures:
        planning_gate = {}
        approved_batch = []
    else:
        planning_gate = load_json(PLANNING_GATE)
        approved_batch = load_json(APPROVED_BATCH)

    if planning_gate and not planning_gate.get("passed"):
        failures.append("phase_17c9b_not_passed")

    movement_plan = []
    rollback_plan = []
    seen_sources = set()
    seen_destinations = set()

    for index, row in enumerate(approved_batch, start=1):
        source_rel = row["path"]
        destination_rel = row["proposed_destination"]

        source = ROOT / source_rel
        destination = ROOT / destination_rel

        operation = {
            "operation_id": f"17C9C_MOVE_{index:04d}",
            "action": "DRY_RUN_MOVE",
            "source": source_rel,
            "destination": destination_rel,
            "source_exists": source.exists(),
            "destination_exists": destination.exists(),
            "destination_parent_exists": destination.parent.exists(),
            "destination_parent": destination.parent.relative_to(ROOT).as_posix(),
            "movement_risk": row.get("movement_risk"),
            "semantic_confidence": row.get("semantic_confidence"),
            "semantic_subsystem": row.get("semantic_subsystem"),
            "semantic_role": row.get("semantic_role"),
            "semantic_owner": row.get("semantic_owner"),
            "dominant_signal": row.get("dominant_signal"),
            "classification_reason": row.get("classification_reason"),
            "would_create_parent": not destination.parent.exists(),
            "safe_to_execute": (
                source.exists()
                and not destination.exists()
                and source_rel not in seen_sources
                and destination_rel not in seen_destinations
                and row.get("movement_risk") == "LOW"
            ),
        }

        if not operation["source_exists"]:
            failures.append(f"source_missing={source_rel}")

        if operation["destination_exists"]:
            failures.append(f"destination_exists={destination_rel}")

        if source_rel in seen_sources:
            failures.append(f"duplicate_source={source_rel}")

        if destination_rel in seen_destinations:
            failures.append(f"duplicate_destination={destination_rel}")

        if row.get("movement_risk") != "LOW":
            failures.append(f"non_low_risk_move_in_plan={source_rel}")

        if operation["would_create_parent"]:
            warnings.append(f"would_create_destination_parent={operation['destination_parent']}")

        seen_sources.add(source_rel)
        seen_destinations.add(destination_rel)

        movement_plan.append(operation)

        rollback_plan.append({
            "operation_id": operation["operation_id"],
            "action": "ROLLBACK_MOVE",
            "source": destination_rel,
            "destination": source_rel,
        })

    if not movement_plan:
        failures.append("empty_movement_plan")

    if any(not item["safe_to_execute"] for item in movement_plan):
        failures.append("unsafe_operations_present")

    result = {
        "phase": "17C.9C",
        "feature": "INTELLIGENCE_GUIDED_DRY_RUN_MOVEMENT_PLAN",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "source_gate": PLANNING_GATE.relative_to(ROOT).as_posix(),
        "source_approved_batch": APPROVED_BATCH.relative_to(ROOT).as_posix(),
        "summary": {
            "approved_batch_count": len(approved_batch),
            "movement_plan_count": len(movement_plan),
            "rollback_plan_count": len(rollback_plan),
            "safe_to_execute_count": sum(1 for item in movement_plan if item["safe_to_execute"]),
            "would_create_parent_count": sum(1 for item in movement_plan if item["would_create_parent"]),
            "failure_count": len(failures),
            "warning_count": len(warnings),
        },
        "warnings": warnings,
        "failures": failures,
        "movement_plan": movement_plan,
        "rollback_plan": rollback_plan,
        "completion_notice": (
            "PHASE_17C9C_COMPLETE_INTELLIGENCE_GUIDED_DRY_RUN_MOVEMENT_PLAN_CREATED"
            if not failures
            else "PHASE_17C9C_BLOCKED"
        ),
        "next_phase": "17C.9D_DRY_RUN_VALIDATION_GATE",
    }

    plan_json = OUT_DIR / "intelligence_guided_dry_run_movement_plan_phase_17c9c.json"
    rollback_json = OUT_DIR / "intelligence_guided_dry_run_rollback_plan_phase_17c9c.json"
    report_txt = OUT_DIR / "intelligence_guided_dry_run_movement_plan_phase_17c9c.txt"

    plan_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    rollback_json.write_text(json.dumps(rollback_plan, indent=2), encoding="utf-8")

    report_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.9C INTELLIGENCE-GUIDED DRY RUN MOVEMENT PLAN",
            "=============================================================",
            f"passed={result['passed']}",
            f"approved_batch_count={result['summary']['approved_batch_count']}",
            f"movement_plan_count={result['summary']['movement_plan_count']}",
            f"rollback_plan_count={result['summary']['rollback_plan_count']}",
            f"safe_to_execute_count={result['summary']['safe_to_execute_count']}",
            f"would_create_parent_count={result['summary']['would_create_parent_count']}",
            f"failure_count={result['summary']['failure_count']}",
            f"warning_count={result['summary']['warning_count']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={plan_json.relative_to(ROOT)}",
            f"rollback_json={rollback_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9C_INTELLIGENCE_GUIDED_DRY_RUN_MOVEMENT_PLAN" if result["passed"] else "FAIL_PHASE_17C9C_INTELLIGENCE_GUIDED_DRY_RUN_MOVEMENT_PLAN")
    print(f"approved_batch_count={result['summary']['approved_batch_count']}")
    print(f"movement_plan_count={result['summary']['movement_plan_count']}")
    print(f"rollback_plan_count={result['summary']['rollback_plan_count']}")
    print(f"safe_to_execute_count={result['summary']['safe_to_execute_count']}")
    print(f"would_create_parent_count={result['summary']['would_create_parent_count']}")
    print(f"failure_count={result['summary']['failure_count']}")
    print(f"warning_count={result['summary']['warning_count']}")
    print(f"report={report_txt.relative_to(ROOT)}")
    print(f"json={plan_json.relative_to(ROOT)}")
    print(f"rollback_json={rollback_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
