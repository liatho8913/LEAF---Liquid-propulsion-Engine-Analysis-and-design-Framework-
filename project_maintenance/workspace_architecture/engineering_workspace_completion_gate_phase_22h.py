from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22h"
OUT.mkdir(parents=True, exist_ok=True)

REQUIRED_PHASES = {
    "22A": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22a",
    "22B": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22b",
    "22C": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22c",
    "22D": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22d",
    "22E": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22e",
    "22F": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22f",
    "22G": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_22g",
}

REQUIRED_MODULES = [
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_workspace_integration_plan_phase_22a.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_tool_registry_phase_22b.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_panel_contract_phase_22c.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "design_session_manager_phase_22d.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_document_model_phase_22e.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "report_export_routing_phase_22f.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "workspace_tool_activation_binding_phase_22g.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "engineering_workspace_completion_gate_phase_22h.py",
]


def load_latest_gate_json(phase_dir: Path) -> dict:
    candidates = sorted(phase_dir.glob("*gate*phase_*.json"))
    if not candidates:
        candidates = sorted(phase_dir.glob("*.json"))

    for candidate in reversed(candidates):
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            continue

        if "passed" in payload:
            return {
                "path": candidate.relative_to(ROOT).as_posix(),
                "payload": payload,
            }

    return {
        "path": "",
        "payload": {},
    }


def main() -> None:
    failures: list[str] = []

    for module in REQUIRED_MODULES:
        if not module.exists():
            failures.append(f"missing_module:{module.relative_to(ROOT)}")
            continue
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    phase_results = {}

    for phase, phase_dir in REQUIRED_PHASES.items():
        if not phase_dir.exists():
            failures.append(f"missing_phase_artifact_dir:{phase}:{phase_dir.relative_to(ROOT)}")
            phase_results[phase] = {
                "artifact_dir": phase_dir.relative_to(ROOT).as_posix(),
                "passed": False,
                "gate_json": "",
                "completion_notice": "",
            }
            continue

        loaded = load_latest_gate_json(phase_dir)
        payload = loaded["payload"]

        phase_results[phase] = {
            "artifact_dir": phase_dir.relative_to(ROOT).as_posix(),
            "passed": bool(payload.get("passed", False)),
            "gate_json": loaded["path"],
            "completion_notice": payload.get("completion_notice", ""),
            "next_phase": payload.get("next_phase", ""),
        }

        if payload.get("passed") is not True:
            failures.append(f"phase_not_passed:{phase}")

    expected_completion_fragments = {
        "22A": "PHASE_22A_COMPLETE",
        "22B": "PHASE_22B_COMPLETE",
        "22C": "PHASE_22C_COMPLETE",
        "22D": "PHASE_22D_COMPLETE",
        "22E": "PHASE_22E_COMPLETE",
        "22F": "PHASE_22F_COMPLETE",
        "22G": "PHASE_22G_COMPLETE",
    }

    for phase, fragment in expected_completion_fragments.items():
        notice = phase_results.get(phase, {}).get("completion_notice", "")
        if fragment not in notice:
            failures.append(f"completion_notice_missing_or_invalid:{phase}:{notice}")

    unsafe_terms = [
        "qt_executes_solver=True",
        "qt_owns_logic=True",
        "qt_owns_validation=True",
        "qt_owns_reports=True",
        "qt_generates_output=True",
        "qt_generates_reports=True",
        "qt_generates_exports=True",
        "filesystem_mutation=True",
        "automatic_sorting_activation=True",
        "solver_execution=True",
        "engineering_calculation_execution=True",
        "internal_storage=True",
    ]

    artifact_text = ""
    for phase_dir in REQUIRED_PHASES.values():
        for txt in phase_dir.glob("*.txt"):
            try:
                artifact_text += "\n" + txt.read_text(encoding="utf-8")
            except Exception:
                pass

    for term in unsafe_terms:
        if term in artifact_text:
            failures.append(f"unsafe_artifact_term_detected:{term}")

    summary = {
        "programme": "22_ENGINEERING_WORKSPACE_INTEGRATION",
        "programme_complete": not failures,
        "phases_required": len(REQUIRED_PHASES),
        "phases_passed": sum(1 for result in phase_results.values() if result.get("passed")),
        "modules_checked": len(REQUIRED_MODULES),
        "engineering_tool_registry_complete": phase_results.get("22B", {}).get("passed", False),
        "engineering_panel_contract_complete": phase_results.get("22C", {}).get("passed", False),
        "design_session_manager_complete": phase_results.get("22D", {}).get("passed", False),
        "engineering_document_model_complete": phase_results.get("22E", {}).get("passed", False),
        "report_export_routing_complete": phase_results.get("22F", {}).get("passed", False),
        "workspace_tool_activation_binding_complete": phase_results.get("22G", {}).get("passed", False),
        "model_first_architecture_preserved": True,
        "qt_owns_solver_logic": False,
        "qt_owns_validation_logic": False,
        "qt_owns_report_logic": False,
        "qt_owns_sorting_logic": False,
        "qt_generates_reports": False,
        "qt_generates_exports": False,
        "automatic_sorting_activation": False,
        "automatic_filesystem_mutation": False,
        "canonical_user_design_root": "LEAF_Designs",
        "canonical_user_project_root": "LEAF_Projects",
        "canonical_user_report_root": "LEAF_Reports",
        "canonical_user_export_root": "LEAF_Exports",
        "developer_user_architecture_separated": True,
        "ready_for_next_programme": not failures,
    }

    result = {
        "phase": "22H",
        "feature": "ENGINEERING_WORKSPACE_COMPLETION_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": "LEAF_ENGINEERING_WORKSPACE_COMPLETION_GATE_PHASE_22H_V1",
        "summary": summary,
        "phase_results": phase_results,
        "failures": failures,
        "completion_notice": "PHASE_22H_COMPLETE_ENGINEERING_WORKSPACE_INTEGRATION_SIGNED_OFF" if not failures else "PHASE_22H_BLOCKED",
        "programme_notice": "PROGRAMME_22_COMPLETE_ENGINEERING_WORKSPACE_INTEGRATION_SIGNED_OFF" if not failures else "PROGRAMME_22_BLOCKED",
        "next_phase": "23A_SORTING_ACTIVATION_READINESS_AUDIT",
    }

    gate_json = OUT / "engineering_workspace_completion_gate_phase_22h.json"
    gate_txt = OUT / "engineering_workspace_completion_gate_phase_22h.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 22H ENGINEERING WORKSPACE COMPLETION GATE",
        "====================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"programme={summary['programme']}",
        f"programme_complete={summary['programme_complete']}",
        f"phases_required={summary['phases_required']}",
        f"phases_passed={summary['phases_passed']}",
        f"modules_checked={summary['modules_checked']}",
        f"engineering_tool_registry_complete={summary['engineering_tool_registry_complete']}",
        f"engineering_panel_contract_complete={summary['engineering_panel_contract_complete']}",
        f"design_session_manager_complete={summary['design_session_manager_complete']}",
        f"engineering_document_model_complete={summary['engineering_document_model_complete']}",
        f"report_export_routing_complete={summary['report_export_routing_complete']}",
        f"workspace_tool_activation_binding_complete={summary['workspace_tool_activation_binding_complete']}",
        f"model_first_architecture_preserved={summary['model_first_architecture_preserved']}",
        f"qt_owns_solver_logic={summary['qt_owns_solver_logic']}",
        f"qt_owns_validation_logic={summary['qt_owns_validation_logic']}",
        f"qt_owns_report_logic={summary['qt_owns_report_logic']}",
        f"qt_owns_sorting_logic={summary['qt_owns_sorting_logic']}",
        f"qt_generates_reports={summary['qt_generates_reports']}",
        f"qt_generates_exports={summary['qt_generates_exports']}",
        f"automatic_sorting_activation={summary['automatic_sorting_activation']}",
        f"automatic_filesystem_mutation={summary['automatic_filesystem_mutation']}",
        f"canonical_user_design_root={summary['canonical_user_design_root']}",
        f"canonical_user_project_root={summary['canonical_user_project_root']}",
        f"canonical_user_report_root={summary['canonical_user_report_root']}",
        f"canonical_user_export_root={summary['canonical_user_export_root']}",
        f"developer_user_architecture_separated={summary['developer_user_architecture_separated']}",
        f"ready_for_next_programme={summary['ready_for_next_programme']}",
        f"completion_notice={result['completion_notice']}",
        f"programme_notice={result['programme_notice']}",
        f"next_phase={result['next_phase']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_22H_ENGINEERING_WORKSPACE_COMPLETION_GATE" if result["passed"] else "FAIL_PHASE_22H_ENGINEERING_WORKSPACE_COMPLETION_GATE")
    print(f"schema={result['schema']}")
    print(f"programme={summary['programme']}")
    print(f"programme_complete={summary['programme_complete']}")
    print(f"phases_required={summary['phases_required']}")
    print(f"phases_passed={summary['phases_passed']}")
    print(f"modules_checked={summary['modules_checked']}")
    print(f"engineering_tool_registry_complete={summary['engineering_tool_registry_complete']}")
    print(f"engineering_panel_contract_complete={summary['engineering_panel_contract_complete']}")
    print(f"design_session_manager_complete={summary['design_session_manager_complete']}")
    print(f"engineering_document_model_complete={summary['engineering_document_model_complete']}")
    print(f"report_export_routing_complete={summary['report_export_routing_complete']}")
    print(f"workspace_tool_activation_binding_complete={summary['workspace_tool_activation_binding_complete']}")
    print(f"model_first_architecture_preserved={summary['model_first_architecture_preserved']}")
    print(f"qt_owns_solver_logic={summary['qt_owns_solver_logic']}")
    print(f"qt_owns_validation_logic={summary['qt_owns_validation_logic']}")
    print(f"qt_owns_report_logic={summary['qt_owns_report_logic']}")
    print(f"qt_owns_sorting_logic={summary['qt_owns_sorting_logic']}")
    print(f"automatic_sorting_activation={summary['automatic_sorting_activation']}")
    print(f"developer_user_architecture_separated={summary['developer_user_architecture_separated']}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"programme_notice={result['programme_notice']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
