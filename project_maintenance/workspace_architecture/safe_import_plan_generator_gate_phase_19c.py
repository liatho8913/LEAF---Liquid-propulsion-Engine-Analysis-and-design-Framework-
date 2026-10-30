from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.workspace_runtime_core import (
    SAFE_IMPORT_PLAN_SCHEMA as SCHEMA,
    build_safe_import_plan,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_19c"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "safe_import_plan_generator_gate_phase_19c.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    plan = build_safe_import_plan(ROOT)
    summary = plan["summary"]
    policy = plan["execution_policy"]

    if plan.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if plan.get("source_review_registry_schema") != "LEAF_IMPORT_REVIEW_REGISTRY_PHASE_19B_V1":
        failures.append("source_review_registry_schema_invalid")

    if summary.get("review_records") != summary.get("plans_ready", 0) + summary.get("plans_blocked", 0):
        failures.append("plan_count_mismatch")

    for key in [
        "plan_generator_is_read_only",
        "creates_plans_only",
        "requires_manual_approval",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_not_true={key}")

    for key in [
        "imports_files",
        "copies_files",
        "moves_existing_files",
        "deletes_files",
        "archives_files",
        "overwrites_files",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    for key in [
        "automatic_actions_created",
        "execution_allowed_plans",
        "copy_operations_created",
        "move_operations_created",
        "delete_operations_created",
        "archive_operations_created",
    ]:
        if summary.get(key) != 0:
            failures.append(f"unsafe_summary_nonzero={key}")

    for collection_name in ["ready_plans", "blocked_plans"]:
        for review_id, item in plan.get(collection_name, {}).items():
            if item.get("execution_allowed") is not False:
                failures.append(f"plan_execution_allowed={review_id}")
            if item.get("manual_approval_required") is not True:
                failures.append(f"manual_approval_missing={review_id}")
            for key in [
                "overwrite_allowed",
                "delete_source_allowed",
                "archive_source_allowed",
                "move_source_allowed",
            ]:
                if item.get(key) is not False:
                    failures.append(f"unsafe_plan_flag_not_false={review_id}:{key}")
            if item.get("copy_not_move") is not True:
                failures.append(f"copy_not_move_not_true={review_id}")
            if item.get("preserve_source") is not True:
                failures.append(f"preserve_source_not_true={review_id}")

    plan_path = OUT / "safe_import_plan_phase_19c.json"
    gate_json = OUT / "safe_import_plan_generator_gate_phase_19c.json"
    gate_txt = OUT / "safe_import_plan_generator_gate_phase_19c.txt"

    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    result = {
        "phase": "19C",
        "feature": "SAFE_IMPORT_PLAN_GENERATOR",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": plan.get("schema"),
        "source_review_registry_schema": plan.get("source_review_registry_schema"),
        "summary": summary,
        "failures": failures,
        "plan_json": plan_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_19C_COMPLETE_SAFE_IMPORT_PLAN_GENERATOR_ESTABLISHED" if not failures else "PHASE_19C_BLOCKED",
        "next_phase": "19D_MANUAL_APPROVAL_GATE",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 19C SAFE IMPORT PLAN GENERATOR",
        "==========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_review_registry_schema={result['source_review_registry_schema']}",
        f"review_records={summary.get('review_records')}",
        f"plans_ready={summary.get('plans_ready')}",
        f"plans_blocked={summary.get('plans_blocked')}",
        f"blocked_destination_conflict={summary.get('blocked_destination_conflict')}",
        f"blocked_duplicate_review={summary.get('blocked_duplicate_review')}",
        f"blocked_low_confidence={summary.get('blocked_low_confidence')}",
        f"blocked_invalid_json={summary.get('blocked_invalid_json')}",
        f"automatic_actions_created={summary.get('automatic_actions_created')}",
        f"execution_allowed_plans={summary.get('execution_allowed_plans')}",
        f"copy_operations_created={summary.get('copy_operations_created')}",
        f"move_operations_created={summary.get('move_operations_created')}",
        f"delete_operations_created={summary.get('delete_operations_created')}",
        f"archive_operations_created={summary.get('archive_operations_created')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"plan_json={result['plan_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_19C_SAFE_IMPORT_PLAN_GENERATOR" if result["passed"] else "FAIL_PHASE_19C_SAFE_IMPORT_PLAN_GENERATOR")
    print(f"schema={result['schema']}")
    print(f"source_review_registry_schema={result['source_review_registry_schema']}")
    print(f"review_records={summary.get('review_records')}")
    print(f"plans_ready={summary.get('plans_ready')}")
    print(f"plans_blocked={summary.get('plans_blocked')}")
    print(f"blocked_destination_conflict={summary.get('blocked_destination_conflict')}")
    print(f"blocked_duplicate_review={summary.get('blocked_duplicate_review')}")
    print(f"blocked_low_confidence={summary.get('blocked_low_confidence')}")
    print(f"automatic_actions_created={summary.get('automatic_actions_created')}")
    print(f"execution_allowed_plans={summary.get('execution_allowed_plans')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"plan_json={result['plan_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
