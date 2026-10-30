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
    NAVIGATION_SCHEMA as SCHEMA,
    NAVIGATION_SECTIONS,
    build_workspace_navigation_model,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_18d"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_navigation_model_gate_phase_18d.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    model = build_workspace_navigation_model(ROOT)
    summary = model["summary"]
    policy = model["execution_policy"]

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if model.get("source_ownership_schema") != "LEAF_WORKSPACE_RESOURCE_OWNERSHIP_LAYER_PHASE_18C_V1":
        failures.append("source_ownership_schema_invalid")

    if summary.get("navigation_sections") != len(NAVIGATION_SECTIONS):
        failures.append("navigation_section_count_invalid")

    for section in NAVIGATION_SECTIONS:
        if section not in model.get("sections", {}):
            failures.append(f"navigation_section_missing={section}")

    if summary.get("developer_sections_exposed") != 0:
        failures.append("developer_sections_exposed_to_user_navigation")

    if summary.get("internal_paths_required_for_user_navigation") != 0:
        failures.append("internal_paths_required_for_user_navigation")

    if summary.get("user_visible_navigation_ready") is not True:
        failures.append("user_visible_navigation_not_ready")

    if policy.get("navigation_model_is_read_only") is not True:
        failures.append("navigation_model_not_read_only")

    if policy.get("uses_18c_ownership_layer") is not True:
        failures.append("does_not_use_18c_ownership_layer")

    if policy.get("rescans_internal_folders") is not False:
        failures.append("rescans_internal_folders_not_false")

    for key in [
        "moves_existing_files",
        "deletes_files",
        "archives_files",
        "rewrites_existing_user_assets",
    ]:
        if policy.get(key) is not False:
            failures.append(f"unsafe_policy_not_false={key}")

    model_path = OUT / "workspace_navigation_model_phase_18d.json"
    gate_json = OUT / "workspace_navigation_model_gate_phase_18d.json"
    gate_txt = OUT / "workspace_navigation_model_gate_phase_18d.txt"

    model_path.write_text(json.dumps(model, indent=2), encoding="utf-8")

    result = {
        "phase": "18D",
        "feature": "WORKSPACE_NAVIGATION_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": model.get("schema"),
        "source_ownership_schema": model.get("source_ownership_schema"),
        "summary": summary,
        "failures": failures,
        "navigation_json": model_path.relative_to(ROOT).as_posix(),
        "completion_notice": "PHASE_18D_COMPLETE_WORKSPACE_NAVIGATION_MODEL_ESTABLISHED" if not failures else "PHASE_18D_BLOCKED",
        "next_phase": "18E_WORKSPACE_ARCHITECTURE_COMPLETION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 18D WORKSPACE NAVIGATION MODEL",
        "==========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_ownership_schema={result['source_ownership_schema']}",
        f"navigation_sections={summary.get('navigation_sections')}",
        f"navigation_items={summary.get('navigation_items')}",
        f"quick_access_items={summary.get('quick_access_items')}",
        f"developer_sections_exposed={summary.get('developer_sections_exposed')}",
        f"internal_paths_required_for_user_navigation={summary.get('internal_paths_required_for_user_navigation')}",
        f"user_visible_navigation_ready={summary.get('user_visible_navigation_ready')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"navigation_json={result['navigation_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_18D_WORKSPACE_NAVIGATION_MODEL" if result["passed"] else "FAIL_PHASE_18D_WORKSPACE_NAVIGATION_MODEL")
    print(f"schema={result['schema']}")
    print(f"source_ownership_schema={result['source_ownership_schema']}")
    print(f"navigation_sections={summary.get('navigation_sections')}")
    print(f"navigation_items={summary.get('navigation_items')}")
    print(f"quick_access_items={summary.get('quick_access_items')}")
    print(f"developer_sections_exposed={summary.get('developer_sections_exposed')}")
    print(f"internal_paths_required_for_user_navigation={summary.get('internal_paths_required_for_user_navigation')}")
    print(f"user_visible_navigation_ready={summary.get('user_visible_navigation_ready')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"navigation_json={result['navigation_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
