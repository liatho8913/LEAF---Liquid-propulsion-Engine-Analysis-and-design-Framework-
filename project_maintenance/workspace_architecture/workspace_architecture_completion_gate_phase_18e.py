from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.workspace_architecture_completion_phase_18e import (
    SCHEMA,
    build_workspace_architecture_completion_certificate,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_18e"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_architecture_completion_phase_18e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_architecture_completion_gate_phase_18e.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    certificate = build_workspace_architecture_completion_certificate(ROOT)
    failures.extend(certificate.get("failures", []))

    summary = certificate.get("summary", {})
    sorting = certificate.get("sorting_intelligence_status", {})
    locks = certificate.get("safety_locks", {})

    if certificate.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if certificate.get("programme_completed") is not True:
        failures.append("programme_not_completed")

    if summary.get("artifacts_present") != summary.get("artifacts_required"):
        failures.append("required_artifacts_missing")

    if summary.get("schemas_valid") != summary.get("artifacts_required"):
        failures.append("required_artifact_schemas_invalid")

    if summary.get("ready_for_next_programme") is not True:
        failures.append("not_ready_for_next_programme")

    if sorting.get("whole_sorting_intelligence_engine_complete") is not True:
        failures.append("whole_sorting_intelligence_not_complete")

    for key in [
        "move_allowed",
        "archive_allowed",
        "delete_allowed",
        "automatic_delete_allowed",
        "automatic_relocation_allowed",
        "automatic_import_allowed",
        "completion_gate_execution_allowed",
        "deletion_started",
    ]:
        if locks.get(key) is not False:
            failures.append(f"safety_lock_not_false={key}")

    cert_path = OUT / "workspace_architecture_completion_certificate_phase_18e.json"
    gate_json = OUT / "workspace_architecture_completion_gate_phase_18e.json"
    gate_txt = OUT / "workspace_architecture_completion_gate_phase_18e.txt"

    certificate["passed"] = not failures
    certificate["failures"] = failures
    certificate["completion_notice"] = (
        "PHASE_18E_COMPLETE_WORKSPACE_ARCHITECTURE_SIGNED_OFF"
        if not failures else
        "PHASE_18E_BLOCKED"
    )

    cert_path.write_text(json.dumps(certificate, indent=2), encoding="utf-8")

    result = {
        "phase": "18E",
        "feature": "WORKSPACE_ARCHITECTURE_COMPLETION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": certificate.get("schema"),
        "summary": summary,
        "sorting_intelligence_status": sorting,
        "failures": failures,
        "completion_notice": certificate["completion_notice"],
        "certificate_json": cert_path.relative_to(ROOT).as_posix(),
        "next_phase": "19A_WORKSPACE_IMPORT_CANDIDATE_DETECTOR",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 18E WORKSPACE ARCHITECTURE COMPLETION",
        "==================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"programme_completed={summary.get('programme_completed')}",
        f"artifacts_required={summary.get('artifacts_required')}",
        f"artifacts_present={summary.get('artifacts_present')}",
        f"schemas_valid={summary.get('schemas_valid')}",
        f"canonical_roots_present={summary.get('canonical_roots_present')}",
        f"registered_resources={summary.get('registered_resources')}",
        f"owned_resources={summary.get('owned_resources')}",
        f"navigation_sections={summary.get('navigation_sections')}",
        f"navigation_items={summary.get('navigation_items')}",
        f"developer_sections_exposed={summary.get('developer_sections_exposed')}",
        f"internal_paths_required_for_user_navigation={summary.get('internal_paths_required_for_user_navigation')}",
        f"whole_sorting_intelligence_engine_complete={sorting.get('whole_sorting_intelligence_engine_complete')}",
        f"ready_for_next_programme={summary.get('ready_for_next_programme')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"certificate_json={result['certificate_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_18E_WORKSPACE_ARCHITECTURE_COMPLETION" if result["passed"] else "FAIL_PHASE_18E_WORKSPACE_ARCHITECTURE_COMPLETION")
    print(f"schema={result['schema']}")
    print(f"programme_completed={summary.get('programme_completed')}")
    print(f"artifacts_required={summary.get('artifacts_required')}")
    print(f"artifacts_present={summary.get('artifacts_present')}")
    print(f"schemas_valid={summary.get('schemas_valid')}")
    print(f"canonical_roots_present={summary.get('canonical_roots_present')}")
    print(f"registered_resources={summary.get('registered_resources')}")
    print(f"owned_resources={summary.get('owned_resources')}")
    print(f"navigation_sections={summary.get('navigation_sections')}")
    print(f"navigation_items={summary.get('navigation_items')}")
    print(f"whole_sorting_intelligence_engine_complete={sorting.get('whole_sorting_intelligence_engine_complete')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"certificate_json={result['certificate_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
