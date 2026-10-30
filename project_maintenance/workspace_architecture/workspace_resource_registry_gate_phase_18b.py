from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.workspace_runtime_core import CANONICAL_USER_ROOTS
from leaf_qt.workspace_runtime_core import (
    RESOURCE_REGISTRY_SCHEMA as SCHEMA,
    build_workspace_resource_registry,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_18b"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_resource_registry_gate_phase_18b.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    registry = build_workspace_resource_registry(ROOT)
    summary = registry["summary"]
    policy = registry["execution_policy"]

    if registry.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if summary["canonical_roots"] != len(CANONICAL_USER_ROOTS):
        failures.append("canonical_root_count_invalid")

    for folder in CANONICAL_USER_ROOTS:
        root_record = registry["canonical_roots"].get(folder)
        if not root_record:
            failures.append(f"canonical_root_missing_from_registry={folder}")
        elif not root_record["exists"] or not root_record["is_dir"]:
            failures.append(f"canonical_root_not_ready={folder}")

    if policy.get("registry_is_read_only") is not True:
        failures.append("registry_not_read_only")
    if policy.get("moves_existing_files") is not False:
        failures.append("move_policy_not_false")
    if policy.get("deletes_files") is not False:
        failures.append("delete_policy_not_false")
    if policy.get("archives_files") is not False:
        failures.append("archive_policy_not_false")
    if policy.get("rewrites_existing_user_assets") is not False:
        failures.append("rewrite_policy_not_false")

    if summary.get("developer_files_registered") != 0:
        failures.append("developer_files_registered_as_user_assets")

    if summary.get("internal_folders_registered_as_user_assets") != 0:
        failures.append("internal_folders_registered_as_user_assets")

    registry_path = OUT / "workspace_resource_registry_phase_18b.json"
    gate_json = OUT / "workspace_resource_registry_gate_phase_18b.json"
    gate_txt = OUT / "workspace_resource_registry_gate_phase_18b.txt"

    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    result = {
        "phase": "18B",
        "feature": "WORKSPACE_RESOURCE_REGISTRY",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": registry.get("schema"),
        "summary": summary,
        "failures": failures,
        "registry_json": registry_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_18B_COMPLETE_WORKSPACE_RESOURCE_REGISTRY_ESTABLISHED" if not failures else "PHASE_18B_BLOCKED",
        "next_phase": "18C_PROJECT_DESIGN_REPORT_EXPORT_OWNERSHIP_LAYER",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 18B WORKSPACE RESOURCE REGISTRY",
        "===========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"canonical_roots={summary.get('canonical_roots')}",
        f"registered_resources={summary.get('registered_resources')}",
        f"resource_types={summary.get('resource_types')}",
        f"suffix_groups={summary.get('suffix_groups')}",
        f"developer_files_registered={summary.get('developer_files_registered')}",
        f"internal_folders_registered_as_user_assets={summary.get('internal_folders_registered_as_user_assets')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"registry_json={result['registry_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_18B_WORKSPACE_RESOURCE_REGISTRY" if result["passed"] else "FAIL_PHASE_18B_WORKSPACE_RESOURCE_REGISTRY")
    print(f"schema={result['schema']}")
    print(f"canonical_roots={summary.get('canonical_roots')}")
    print(f"registered_resources={summary.get('registered_resources')}")
    print(f"resource_types={summary.get('resource_types')}")
    print(f"suffix_groups={summary.get('suffix_groups')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"registry_json={result['registry_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
