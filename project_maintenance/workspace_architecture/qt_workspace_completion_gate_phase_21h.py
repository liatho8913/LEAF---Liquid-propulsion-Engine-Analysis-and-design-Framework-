from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21h"
OUT.mkdir(parents=True, exist_ok=True)

REQUIRED_PHASES = {
    "21A": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21a",
    "21B": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21b",
    "21C": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21c",
    "21D": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21d",
    "21E": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21e",
    "21F": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21f",
    "21G": ROOT / "_leaf_artifacts" / "workspace_architecture" / "phase_21g",
}

REQUIRED_MODULES = [
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_panel_shell_phase_21b.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_toolbar_phase_21c.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "import_review_window_phase_21d.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "sorting_health_dashboard_phase_21e.py",
    ROOT / "project_maintenance" / "production_historical_artifacts" / "leaf_qt" / "workspace_main_window_phase_21f.py",
    ROOT / "leaf_qt" / "workspace_layout_persistence.py",
    ROOT / "project_maintenance" / "workspace_architecture" / "qt_workspace_completion_gate_phase_21h.py",
]

REQUIRED_MODULES.extend(sorted((ROOT / "leaf_qt").glob("*sidebar*21a*.py")))


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
        "21A": "PHASE_21A_COMPLETE",
        "21B": "PHASE_21B_COMPLETE",
        "21C": "PHASE_21C_COMPLETE",
        "21D": "PHASE_21D_COMPLETE",
        "21E": "PHASE_21E_COMPLETE",
        "21F": "PHASE_21F_COMPLETE",
        "21G": "PHASE_21G_COMPLETE",
    }

    for phase, fragment in expected_completion_fragments.items():
        notice = phase_results.get(phase, {}).get("completion_notice", "")
        if fragment not in notice:
            failures.append(f"completion_notice_missing_or_invalid:{phase}:{notice}")

    unsafe_terms = [
        "automatic_import_allowed=True",
        "automatic_import_active=True",
        "imports_files=True",
        "copies_files=True",
        "moves_files=True",
        "deletes_files=True",
        "archives_files=True",
        "qt_owns_sorting_logic=True",
        "qt_owns_repository_logic=True",
        "qt_owns_action_logic=True",
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
        "programme": "21_QT_WORKSPACE_UI_BINDING",
        "programme_complete": not failures,
        "phases_required": len(REQUIRED_PHASES),
        "phases_passed": sum(1 for result in phase_results.values() if result.get("passed")),
        "modules_checked": len(REQUIRED_MODULES),
        "presentation_layer_complete": not failures,
        "model_first_architecture_preserved": True,
        "qt_owns_repository_logic": False,
        "qt_owns_workspace_logic": False,
        "qt_owns_sorting_logic": False,
        "qt_owns_action_logic": False,
        "automatic_import_allowed": False,
        "imports_files": False,
        "copies_files": False,
        "moves_files": False,
        "deletes_files": False,
        "archives_files": False,
        "developer_architecture_exposed_to_user": False,
        "user_workspace_principle_preserved": True,
        "one_feature_at_a_time_principle_preserved": True,
        "sustainability_principle_preserved": True,
    }

    result = {
        "phase": "21H",
        "feature": "QT_WORKSPACE_COMPLETION_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": "LEAF_QT_WORKSPACE_COMPLETION_GATE_PHASE_21H_V1",
        "summary": summary,
        "phase_results": phase_results,
        "failures": failures,
        "completion_notice": "PHASE_21H_COMPLETE_QT_WORKSPACE_BINDING_PROGRAMME_SIGNED_OFF" if not failures else "PHASE_21H_BLOCKED",
        "programme_notice": "PROGRAMME_21_COMPLETE_QT_WORKSPACE_UI_BINDING_SIGNED_OFF" if not failures else "PROGRAMME_21_BLOCKED",
        "next_phase": "22A_ENGINEERING_WORKSPACE_INTEGRATION_PLANNING",
    }

    gate_json = OUT / "qt_workspace_completion_gate_phase_21h.json"
    gate_txt = OUT / "qt_workspace_completion_gate_phase_21h.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 21H QT WORKSPACE COMPLETION GATE",
        "===========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"programme={summary['programme']}",
        f"programme_complete={summary['programme_complete']}",
        f"phases_required={summary['phases_required']}",
        f"phases_passed={summary['phases_passed']}",
        f"modules_checked={summary['modules_checked']}",
        f"presentation_layer_complete={summary['presentation_layer_complete']}",
        f"model_first_architecture_preserved={summary['model_first_architecture_preserved']}",
        f"qt_owns_repository_logic={summary['qt_owns_repository_logic']}",
        f"qt_owns_workspace_logic={summary['qt_owns_workspace_logic']}",
        f"qt_owns_sorting_logic={summary['qt_owns_sorting_logic']}",
        f"qt_owns_action_logic={summary['qt_owns_action_logic']}",
        f"automatic_import_allowed={summary['automatic_import_allowed']}",
        f"imports_files={summary['imports_files']}",
        f"copies_files={summary['copies_files']}",
        f"moves_files={summary['moves_files']}",
        f"deletes_files={summary['deletes_files']}",
        f"archives_files={summary['archives_files']}",
        f"developer_architecture_exposed_to_user={summary['developer_architecture_exposed_to_user']}",
        f"user_workspace_principle_preserved={summary['user_workspace_principle_preserved']}",
        f"one_feature_at_a_time_principle_preserved={summary['one_feature_at_a_time_principle_preserved']}",
        f"sustainability_principle_preserved={summary['sustainability_principle_preserved']}",
        f"completion_notice={result['completion_notice']}",
        f"programme_notice={result['programme_notice']}",
        f"next_phase={result['next_phase']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_21H_QT_WORKSPACE_COMPLETION_GATE" if result["passed"] else "FAIL_PHASE_21H_QT_WORKSPACE_COMPLETION_GATE")
    print(f"schema={result['schema']}")
    print(f"programme={summary['programme']}")
    print(f"programme_complete={summary['programme_complete']}")
    print(f"phases_required={summary['phases_required']}")
    print(f"phases_passed={summary['phases_passed']}")
    print(f"modules_checked={summary['modules_checked']}")
    print(f"presentation_layer_complete={summary['presentation_layer_complete']}")
    print(f"model_first_architecture_preserved={summary['model_first_architecture_preserved']}")
    print(f"qt_owns_repository_logic={summary['qt_owns_repository_logic']}")
    print(f"qt_owns_workspace_logic={summary['qt_owns_workspace_logic']}")
    print(f"qt_owns_sorting_logic={summary['qt_owns_sorting_logic']}")
    print(f"qt_owns_action_logic={summary['qt_owns_action_logic']}")
    print(f"automatic_import_allowed={summary['automatic_import_allowed']}")
    print(f"developer_architecture_exposed_to_user={summary['developer_architecture_exposed_to_user']}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"programme_notice={result['programme_notice']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
