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
    RESOURCE_OWNERSHIP_SCHEMA as SCHEMA,
    RESOURCE_OWNERS,
    build_workspace_resource_ownership_layer,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_18c"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_resource_ownership_layer_gate_phase_18c.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    layer = build_workspace_resource_ownership_layer(ROOT)
    summary = layer["summary"]
    policy = layer["execution_policy"]

    if layer.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if layer.get("source_registry_schema") != "LEAF_WORKSPACE_RESOURCE_REGISTRY_PHASE_18B_V1":
        failures.append("source_registry_schema_invalid")

    if summary.get("registered_resources") != summary.get("owned_resources"):
        failures.append("not_all_registered_resources_owned")

    if summary.get("ownership_failures") != 0:
        failures.extend(layer.get("failures", []))

    for resource_type in ["design", "project", "report", "export"]:
        if resource_type not in RESOURCE_OWNERS:
            failures.append(f"resource_owner_missing={resource_type}")

    if policy.get("registry_source_only") is not True:
        failures.append("registry_source_only_not_true")
    if policy.get("rescans_internal_folders") is not False:
        failures.append("rescans_internal_folders_not_false")
    if policy.get("ownership_layer_is_read_only") is not True:
        failures.append("ownership_layer_not_read_only")

    for key in [
        "moves_existing_files",
        "deletes_files",
        "archives_files",
        "rewrites_existing_user_assets",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    if summary.get("developer_assets_owned_as_user_resources") != 0:
        failures.append("developer_assets_owned_as_user_resources")

    if summary.get("internal_assets_owned_as_user_resources") != 0:
        failures.append("internal_assets_owned_as_user_resources")

    ownership_path = OUT / "workspace_resource_ownership_layer_phase_18c.json"
    gate_json = OUT / "workspace_resource_ownership_layer_gate_phase_18c.json"
    gate_txt = OUT / "workspace_resource_ownership_layer_gate_phase_18c.txt"

    ownership_path.write_text(json.dumps(layer, indent=2), encoding="utf-8")

    result = {
        "phase": "18C",
        "feature": "PROJECT_DESIGN_REPORT_EXPORT_OWNERSHIP_LAYER",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": layer.get("schema"),
        "source_registry_schema": layer.get("source_registry_schema"),
        "summary": summary,
        "failures": failures,
        "ownership_json": ownership_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_18C_COMPLETE_PROJECT_DESIGN_REPORT_EXPORT_OWNERSHIP_LAYER_ESTABLISHED" if not failures else "PHASE_18C_BLOCKED",
        "next_phase": "18D_WORKSPACE_NAVIGATION_MODEL",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 18C PROJECT DESIGN REPORT EXPORT OWNERSHIP LAYER",
        "=============================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_registry_schema={result['source_registry_schema']}",
        f"registered_resources={summary.get('registered_resources')}",
        f"owned_resources={summary.get('owned_resources')}",
        f"workspace_owners={summary.get('workspace_owners')}",
        f"workspace_domains={summary.get('workspace_domains')}",
        f"workspace_lifecycles={summary.get('workspace_lifecycles')}",
        f"authority_states={summary.get('authority_states')}",
        f"ownership_failures={summary.get('ownership_failures')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"ownership_json={result['ownership_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_18C_PROJECT_DESIGN_REPORT_EXPORT_OWNERSHIP_LAYER" if result["passed"] else "FAIL_PHASE_18C_PROJECT_DESIGN_REPORT_EXPORT_OWNERSHIP_LAYER")
    print(f"schema={result['schema']}")
    print(f"source_registry_schema={result['source_registry_schema']}")
    print(f"registered_resources={summary.get('registered_resources')}")
    print(f"owned_resources={summary.get('owned_resources')}")
    print(f"workspace_owners={summary.get('workspace_owners')}")
    print(f"workspace_domains={summary.get('workspace_domains')}")
    print(f"workspace_lifecycles={summary.get('workspace_lifecycles')}")
    print(f"authority_states={summary.get('authority_states')}")
    print(f"ownership_failures={summary.get('ownership_failures')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"ownership_json={result['ownership_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
