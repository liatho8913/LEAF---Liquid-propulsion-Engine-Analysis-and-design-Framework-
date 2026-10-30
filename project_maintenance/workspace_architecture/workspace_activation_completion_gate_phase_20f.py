from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.workspace_activation_completion_phase_20f import (
    SCHEMA,
    build_workspace_activation_completion_certificate,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_20f"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_activation_completion_phase_20f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_activation_completion_gate_phase_20f.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    certificate = build_workspace_activation_completion_certificate(ROOT)
    failures.extend(certificate.get("failures", []))

    summary = certificate.get("summary", {})
    activation = certificate.get("activation_status", {})
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

    if activation.get("ready_for_qt_workspace_binding") is not True:
        failures.append("not_ready_for_qt_workspace_binding")

    for key in [
        "qt_widgets_created",
        "gui_execution_active",
        "automatic_import_active",
    ]:
        if activation.get(key) is not False:
            failures.append(f"activation_not_false={key}")

    for key, value in locks.items():
        if value is not False:
            failures.append(f"safety_lock_not_false={key}")

    cert_path = OUT / "workspace_activation_completion_certificate_phase_20f.json"
    gate_json = OUT / "workspace_activation_completion_gate_phase_20f.json"
    gate_txt = OUT / "workspace_activation_completion_gate_phase_20f.txt"

    certificate["passed"] = not failures
    certificate["failures"] = failures
    certificate["completion_notice"] = (
        "PHASE_20F_COMPLETE_WORKSPACE_ACTIVATION_SIGNED_OFF"
        if not failures else
        "PHASE_20F_BLOCKED"
    )

    cert_path.write_text(json.dumps(certificate, indent=2), encoding="utf-8")

    result = {
        "phase": "20F",
        "feature": "WORKSPACE_ACTIVATION_COMPLETION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": certificate.get("schema"),
        "summary": summary,
        "activation_status": activation,
        "failures": failures,
        "completion_notice": certificate["completion_notice"],
        "certificate_json": cert_path.relative_to(ROOT).as_posix(),
        "next_phase": "21A_QT_WORKSPACE_SIDEBAR_SHELL",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 20F WORKSPACE ACTIVATION COMPLETION",
        "================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"programme_completed={summary.get('programme_completed')}",
        f"artifacts_required={summary.get('artifacts_required')}",
        f"artifacts_present={summary.get('artifacts_present')}",
        f"schemas_valid={summary.get('schemas_valid')}",
        f"sidebar_items={summary.get('sidebar_items')}",
        f"panel_providers={summary.get('panel_providers')}",
        f"actions={summary.get('actions')}",
        f"review_rows={summary.get('review_rows')}",
        f"dashboard_cards={summary.get('dashboard_cards')}",
        f"unsafe_enabled_actions={summary.get('unsafe_enabled_actions')}",
        f"unsafe_dashboard_flags={summary.get('unsafe_dashboard_flags')}",
        f"ready_for_qt_workspace_binding={activation.get('ready_for_qt_workspace_binding')}",
        f"qt_widgets_created={activation.get('qt_widgets_created')}",
        f"gui_execution_active={activation.get('gui_execution_active')}",
        f"automatic_import_active={activation.get('automatic_import_active')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"certificate_json={result['certificate_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_20F_WORKSPACE_ACTIVATION_COMPLETION" if result["passed"] else "FAIL_PHASE_20F_WORKSPACE_ACTIVATION_COMPLETION")
    print(f"schema={result['schema']}")
    print(f"programme_completed={summary.get('programme_completed')}")
    print(f"artifacts_required={summary.get('artifacts_required')}")
    print(f"artifacts_present={summary.get('artifacts_present')}")
    print(f"schemas_valid={summary.get('schemas_valid')}")
    print(f"sidebar_items={summary.get('sidebar_items')}")
    print(f"panel_providers={summary.get('panel_providers')}")
    print(f"actions={summary.get('actions')}")
    print(f"review_rows={summary.get('review_rows')}")
    print(f"dashboard_cards={summary.get('dashboard_cards')}")
    print(f"ready_for_qt_workspace_binding={activation.get('ready_for_qt_workspace_binding')}")
    print(f"qt_widgets_created={activation.get('qt_widgets_created')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"certificate_json={result['certificate_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
