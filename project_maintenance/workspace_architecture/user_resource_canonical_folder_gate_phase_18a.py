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
    USER_RESOURCE_SCHEMA as SCHEMA,
    CANONICAL_USER_ROOTS,
    ensure_user_resource_folders,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_18a"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "__init__.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "user_resource_canonical_folder_gate_phase_18a.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    plan = ensure_user_resource_folders(ROOT)
    summary = plan["summary"]

    if plan.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    for folder in CANONICAL_USER_ROOTS:
        path = ROOT / folder
        if not path.exists():
            failures.append(f"canonical_folder_missing={folder}")
        elif not path.is_dir():
            failures.append(f"canonical_folder_not_directory={folder}")

    if summary["canonical_roots_present"] != summary["canonical_roots_required"]:
        failures.append("not_all_canonical_roots_present")

    policy = plan.get("execution_policy", {})
    if policy.get("moves_existing_files") is not False:
        failures.append("move_policy_not_false")
    if policy.get("deletes_files") is not False:
        failures.append("delete_policy_not_false")
    if policy.get("archives_files") is not False:
        failures.append("archive_policy_not_false")
    if policy.get("rewrites_existing_user_assets") is not False:
        failures.append("rewrite_policy_not_false")

    plan_path = OUT / "user_resource_canonical_folder_plan_phase_18a.json"
    gate_json = OUT / "user_resource_canonical_folder_gate_phase_18a.json"
    gate_txt = OUT / "user_resource_canonical_folder_gate_phase_18a.txt"

    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    result = {
        "phase": "18A",
        "feature": "USER_RESOURCE_CANONICAL_FOLDER_SYSTEM",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": plan.get("schema"),
        "summary": summary,
        "canonical_user_roots": list(CANONICAL_USER_ROOTS),
        "failures": failures,
        "plan_json": plan_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_18A_COMPLETE_USER_RESOURCE_CANONICAL_FOLDER_SYSTEM_ESTABLISHED" if not failures else "PHASE_18A_BLOCKED",
        "next_phase": "18B_WORKSPACE_RESOURCE_REGISTRY",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 18A USER RESOURCE CANONICAL FOLDER SYSTEM",
        "======================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"canonical_roots_required={summary.get('canonical_roots_required')}",
        f"canonical_roots_present={summary.get('canonical_roots_present')}",
        f"missing_roots={summary.get('missing_roots')}",
        f"canonical_user_roots={result['canonical_user_roots']}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"plan_json={result['plan_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_18A_USER_RESOURCE_CANONICAL_FOLDER_SYSTEM" if result["passed"] else "FAIL_PHASE_18A_USER_RESOURCE_CANONICAL_FOLDER_SYSTEM")
    print(f"schema={result['schema']}")
    print(f"canonical_roots_required={summary.get('canonical_roots_required')}")
    print(f"canonical_roots_present={summary.get('canonical_roots_present')}")
    print(f"missing_roots={summary.get('missing_roots')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"plan_json={result['plan_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
