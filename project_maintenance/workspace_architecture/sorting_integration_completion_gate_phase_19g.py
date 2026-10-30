from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.workspace_architecture.sorting_integration_completion_phase_19g import (
    SCHEMA,
    build_sorting_integration_completion_certificate,
)

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_19g"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "leaf_qt" / "workspace_runtime_core.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "manual_import_approval_gate_phase_19d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "controlled_import_execution_phase_19e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "import_verification_rollback_snapshot_phase_19f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_integration_completion_phase_19g.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "sorting_integration_completion_gate_phase_19g.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    certificate = build_sorting_integration_completion_certificate(ROOT)
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

    if activation.get("ready_for_gui_activation") is not True:
        failures.append("not_ready_for_gui_activation")

    if activation.get("automatic_import_active") is not False:
        failures.append("automatic_import_active_must_be_false")

    if activation.get("gui_activation_active") is not False:
        failures.append("gui_activation_active_must_be_false")

    for key in [
        "move_allowed",
        "archive_allowed",
        "delete_allowed",
        "automatic_delete_allowed",
        "automatic_relocation_allowed",
        "automatic_import_allowed",
        "gui_execution_allowed",
        "completion_gate_execution_allowed",
        "deletion_started",
    ]:
        if locks.get(key) is not False:
            failures.append(f"safety_lock_not_false={key}")

    cert_path = OUT / "sorting_integration_completion_certificate_phase_19g.json"
    gate_json = OUT / "sorting_integration_completion_gate_phase_19g.json"
    gate_txt = OUT / "sorting_integration_completion_gate_phase_19g.txt"

    certificate["passed"] = not failures
    certificate["failures"] = failures
    certificate["completion_notice"] = (
        "PHASE_19G_COMPLETE_SORTING_INTEGRATION_SIGNED_OFF"
        if not failures else
        "PHASE_19G_BLOCKED"
    )

    cert_path.write_text(json.dumps(certificate, indent=2), encoding="utf-8")

    result = {
        "phase": "19G",
        "feature": "SORTING_INTEGRATION_COMPLETION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": certificate.get("schema"),
        "summary": summary,
        "activation_status": activation,
        "failures": failures,
        "completion_notice": certificate["completion_notice"],
        "certificate_json": cert_path.relative_to(ROOT).as_posix(),
        "next_phase": "20A_WORKSPACE_SIDEBAR_MODEL",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 19G SORTING INTEGRATION COMPLETION",
        "================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"programme_completed={summary.get('programme_completed')}",
        f"artifacts_required={summary.get('artifacts_required')}",
        f"artifacts_present={summary.get('artifacts_present')}",
        f"schemas_valid={summary.get('schemas_valid')}",
        f"import_candidates={summary.get('import_candidates')}",
        f"review_records={summary.get('review_records')}",
        f"plans_ready={summary.get('plans_ready')}",
        f"plans_blocked={summary.get('plans_blocked')}",
        f"approval_records={summary.get('approval_records')}",
        f"approved_records={summary.get('approved_records')}",
        f"executed_records={summary.get('executed_records')}",
        f"safe_no_op_state={summary.get('safe_no_op_state')}",
        f"ready_for_gui_activation={activation.get('ready_for_gui_activation')}",
        f"automatic_import_active={activation.get('automatic_import_active')}",
        f"gui_activation_active={activation.get('gui_activation_active')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"certificate_json={result['certificate_json']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_19G_SORTING_INTEGRATION_COMPLETION" if result["passed"] else "FAIL_PHASE_19G_SORTING_INTEGRATION_COMPLETION")
    print(f"schema={result['schema']}")
    print(f"programme_completed={summary.get('programme_completed')}")
    print(f"artifacts_required={summary.get('artifacts_required')}")
    print(f"artifacts_present={summary.get('artifacts_present')}")
    print(f"schemas_valid={summary.get('schemas_valid')}")
    print(f"import_candidates={summary.get('import_candidates')}")
    print(f"review_records={summary.get('review_records')}")
    print(f"plans_ready={summary.get('plans_ready')}")
    print(f"plans_blocked={summary.get('plans_blocked')}")
    print(f"approval_records={summary.get('approval_records')}")
    print(f"approved_records={summary.get('approved_records')}")
    print(f"executed_records={summary.get('executed_records')}")
    print(f"safe_no_op_state={summary.get('safe_no_op_state')}")
    print(f"ready_for_gui_activation={activation.get('ready_for_gui_activation')}")
    print(f"automatic_import_active={activation.get('automatic_import_active')}")
    print(f"gui_activation_active={activation.get('gui_activation_active')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"certificate_json={result['certificate_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
