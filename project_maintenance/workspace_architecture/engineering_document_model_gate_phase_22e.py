from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.engineering_document_model_phase_22e import (
    SCHEMA,
    USER_DESIGN_ROOT,
    USER_PROJECT_ROOT,
    USER_REPORT_ROOT,
    USER_EXPORT_ROOT,
    write_engineering_document_model,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22e"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "design_session_manager_phase_22d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_document_model_phase_22e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_document_model_gate_phase_22e.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    written = write_engineering_document_model(ROOT)
    model = written["model"]
    summary = model["summary"]

    if model.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    expected_roots = {
        "design": USER_DESIGN_ROOT,
        "project": USER_PROJECT_ROOT,
        "report": USER_REPORT_ROOT,
        "export": USER_EXPORT_ROOT,
    }

    if model.get("canonical_roots") != expected_roots:
        failures.append("canonical_roots_invalid")

    expected_types = {"design", "project", "report", "export"}
    actual_types = {doc.get("document_type") for doc in model.get("document_types", [])}

    if actual_types != expected_types:
        failures.append("document_type_set_invalid")

    if summary.get("document_type_count") != 4:
        failures.append("document_type_count_invalid")

    if summary.get("user_visible_document_types") != 4:
        failures.append("user_visible_document_type_count_invalid")

    if summary.get("internal_storage_document_types") != 0:
        failures.append("internal_storage_document_types_nonzero")

    if summary.get("qt_owns_document_logic_count") != 0:
        failures.append("qt_owns_document_logic_count_nonzero")

    for key in [
        "developer_user_architecture_separated",
        "ready_for_22f_report_export_routing",
    ]:
        if summary.get(key) is not True:
            failures.append(f"summary_not_true:{key}")

    for key, value in model.get("safety_boundaries", {}).items():
        if value is not False:
            failures.append(f"safety_boundary_not_false:{key}")

    for doc in model.get("document_types", []):
        doc_type = doc.get("document_type")

        if doc.get("user_visible") is not True:
            failures.append(f"document_not_user_visible:{doc_type}")

        if doc.get("internal_storage") is not False:
            failures.append(f"document_internal_storage_not_false:{doc_type}")

        if doc.get("qt_owns_document_logic") is not False:
            failures.append(f"document_qt_owns_logic_not_false:{doc_type}")

        if doc.get("filesystem_mutation_requires_user_action") is not True:
            failures.append(f"document_user_action_required_not_true:{doc_type}")

    result = {
        "phase": "22E",
        "feature": "ENGINEERING_DOCUMENT_MODEL",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": SCHEMA,
        "summary": summary,
        "document_types": sorted(actual_types),
        "canonical_roots": model.get("canonical_roots"),
        "failures": failures,
        "model_json": written["json_path"],
        "model_report": written["txt_path"],
        "completion_notice": "PHASE_22E_COMPLETE_ENGINEERING_DOCUMENT_MODEL_ESTABLISHED" if not failures else "PHASE_22E_BLOCKED",
        "next_phase": "22F_REPORT_AND_EXPORT_ROUTING",
    }

    gate_json = OUT / "engineering_document_model_gate_phase_22e.json"
    gate_txt = OUT / "engineering_document_model_gate_phase_22e.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 22E ENGINEERING DOCUMENT MODEL GATE",
        "===============================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"document_type_count={summary.get('document_type_count')}",
        f"user_visible_document_types={summary.get('user_visible_document_types')}",
        f"internal_storage_document_types={summary.get('internal_storage_document_types')}",
        f"qt_owns_document_logic_count={summary.get('qt_owns_document_logic_count')}",
        f"filesystem_mutation_requires_user_action_count={summary.get('filesystem_mutation_requires_user_action_count')}",
        f"design_root={summary.get('design_root')}",
        f"project_root={summary.get('project_root')}",
        f"report_root={summary.get('report_root')}",
        f"export_root={summary.get('export_root')}",
        f"developer_user_architecture_separated={summary.get('developer_user_architecture_separated')}",
        f"ready_for_22f_report_export_routing={summary.get('ready_for_22f_report_export_routing')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"model_json={result['model_json']}",
        f"model_report={result['model_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_22E_ENGINEERING_DOCUMENT_MODEL" if result["passed"] else "FAIL_PHASE_22E_ENGINEERING_DOCUMENT_MODEL")
    print(f"schema={result['schema']}")
    print(f"document_type_count={summary.get('document_type_count')}")
    print(f"user_visible_document_types={summary.get('user_visible_document_types')}")
    print(f"internal_storage_document_types={summary.get('internal_storage_document_types')}")
    print(f"qt_owns_document_logic_count={summary.get('qt_owns_document_logic_count')}")
    print(f"design_root={summary.get('design_root')}")
    print(f"project_root={summary.get('project_root')}")
    print(f"report_root={summary.get('report_root')}")
    print(f"export_root={summary.get('export_root')}")
    print(f"developer_user_architecture_separated={summary.get('developer_user_architecture_separated')}")
    print(f"ready_for_22f_report_export_routing={summary.get('ready_for_22f_report_export_routing')}")
    print(f"document_types={','.join(result['document_types'])}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"model_json={result['model_json']}")
    print(f"model_report={result['model_report']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
