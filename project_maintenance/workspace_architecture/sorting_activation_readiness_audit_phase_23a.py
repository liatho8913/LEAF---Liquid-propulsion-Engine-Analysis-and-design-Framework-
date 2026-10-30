from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "LEAF_SORTING_ACTIVATION_READINESS_AUDIT_PHASE_23A_V1"


def _load_gate(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "passed": False, "path": str(path)}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"exists": True, "passed": False, "path": str(path), "error": repr(exc)}

    return {
        "exists": True,
        "passed": bool(payload.get("passed", False)),
        "path": str(path),
        "completion_notice": payload.get("completion_notice", ""),
        "programme_notice": payload.get("programme_notice", ""),
        "next_phase": payload.get("next_phase", ""),
    }


def build_sorting_activation_readiness_audit(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)

    required_gates = {
        "programme_21_workspace_binding": root / "_leaf_artifacts/workspace_architecture/phase_21h/qt_workspace_completion_gate_phase_21h.json",
        "programme_22_engineering_workspace": root / "_leaf_artifacts/workspace_architecture/phase_22h/engineering_workspace_completion_gate_phase_22h.json",
        "sorting_integration_completion_19g": root / "_leaf_artifacts/workspace_architecture/phase_19g/sorting_integration_completion_gate_phase_19g.json",
        "workspace_activation_completion_20f": root / "_leaf_artifacts/workspace_architecture/phase_20f/workspace_activation_completion_gate_phase_20f.json",
    }

    gate_results = {
        name: _load_gate(path)
        for name, path in required_gates.items()
    }

    required_artifact_roots = {
        "user_design_root": root / "LEAF_Designs",
        "user_project_root": root / "LEAF_Projects",
        "user_report_root": root / "LEAF_Reports",
        "user_export_root": root / "LEAF_Exports",
        "workspace_artifacts": root / "_leaf_artifacts/workspace_architecture",
    }

    artifact_root_results = {
        name: {
            "path": path.relative_to(root).as_posix(),
            "exists": path.exists(),
            "is_dir": path.is_dir(),
        }
        for name, path in required_artifact_roots.items()
    }

    safety_requirements = {
        "dry_run_required_before_execution": True,
        "manual_approval_required_before_execution": True,
        "rollback_snapshot_required": True,
        "small_batch_required_before_bulk": True,
        "automatic_sorting_must_remain_disabled": True,
        "continuous_watcher_must_remain_disabled": True,
        "delete_operations_forbidden": True,
        "archive_operations_forbidden_until_verified": True,
        "execution_must_be_user_initiated": True,
    }

    blockers = []

    for name, result in gate_results.items():
        if not result.get("exists"):
            blockers.append(f"missing_gate:{name}")
        elif result.get("passed") is not True:
            blockers.append(f"gate_not_passed:{name}")

    for name, result in artifact_root_results.items():
        if name == "workspace_artifacts":
            if result.get("exists") is not True or result.get("is_dir") is not True:
                blockers.append(f"missing_workspace_artifact_root:{name}")
        else:
            # User roots may be created lazily later, but the document model must remain canonical.
            pass

    execution_readiness = {
        "ready_for_direct_execution": False,
        "ready_for_automatic_sorting": False,
        "ready_for_continuous_watcher": False,
        "ready_for_next_phase_user_approval_rules": len(blockers) == 0,
        "reason": "23A is an audit only. Controlled execution cannot begin until approval rules, sandboxing, rollback and small-batch execution are separately proven.",
    }

    return {
        "schema": SCHEMA,
        "phase": "23A",
        "feature": "SORTING_ACTIVATION_READINESS_AUDIT",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "audit_rule": "This phase audits readiness only. It must not execute sorting, approve imports, move files, copy files, delete files, archive files, or activate watchers.",
        "required_gates": gate_results,
        "artifact_roots": artifact_root_results,
        "safety_requirements": safety_requirements,
        "execution_readiness": execution_readiness,
        "blockers": blockers,
        "summary": {
            "required_gates_checked": len(required_gates),
            "required_gates_passed": sum(1 for result in gate_results.values() if result.get("passed")),
            "blocker_count": len(blockers),
            "audit_only": True,
            "manual_approval_required_before_execution": True,
            "rollback_required_before_execution": True,
            "small_batch_required_before_bulk": True,
            "ready_for_direct_execution": False,
            "ready_for_automatic_sorting": False,
            "ready_for_continuous_watcher": False,
            "ready_for_23b_user_approval_rules": len(blockers) == 0,
            "imports_files": False,
            "copies_files": False,
            "moves_files": False,
            "deletes_files": False,
            "archives_files": False,
            "automatic_sorting_activation": False,
        },
    }


def write_sorting_activation_readiness_audit(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    out_dir = root / "_leaf_artifacts" / "workspace_architecture" / "phase_23a"
    out_dir.mkdir(parents=True, exist_ok=True)

    audit = build_sorting_activation_readiness_audit(root)

    json_path = out_dir / "sorting_activation_readiness_audit_phase_23a.json"
    txt_path = out_dir / "sorting_activation_readiness_audit_phase_23a.txt"

    json_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    txt_path.write_text("\n".join([
        "LEAF PHASE 23A SORTING ACTIVATION READINESS AUDIT",
        "=================================================",
        f"schema={audit['schema']}",
        f"phase={audit['phase']}",
        f"feature={audit['feature']}",
        f"required_gates_checked={audit['summary']['required_gates_checked']}",
        f"required_gates_passed={audit['summary']['required_gates_passed']}",
        f"blocker_count={audit['summary']['blocker_count']}",
        f"audit_only={audit['summary']['audit_only']}",
        f"manual_approval_required_before_execution={audit['summary']['manual_approval_required_before_execution']}",
        f"rollback_required_before_execution={audit['summary']['rollback_required_before_execution']}",
        f"small_batch_required_before_bulk={audit['summary']['small_batch_required_before_bulk']}",
        f"ready_for_direct_execution={audit['summary']['ready_for_direct_execution']}",
        f"ready_for_automatic_sorting={audit['summary']['ready_for_automatic_sorting']}",
        f"ready_for_continuous_watcher={audit['summary']['ready_for_continuous_watcher']}",
        f"ready_for_23b_user_approval_rules={audit['summary']['ready_for_23b_user_approval_rules']}",
        f"imports_files={audit['summary']['imports_files']}",
        f"copies_files={audit['summary']['copies_files']}",
        f"moves_files={audit['summary']['moves_files']}",
        f"deletes_files={audit['summary']['deletes_files']}",
        f"archives_files={audit['summary']['archives_files']}",
        f"automatic_sorting_activation={audit['summary']['automatic_sorting_activation']}",
        "",
        "Gate Results:",
        *[
            f"{name}: exists={result.get('exists')} passed={result.get('passed')}"
            for name, result in audit["required_gates"].items()
        ],
        "",
        "Blockers:",
        *(audit["blockers"] if audit["blockers"] else ["none"]),
    ]), encoding="utf-8")

    return {
        "audit": audit,
        "json_path": json_path.relative_to(root).as_posix(),
        "txt_path": txt_path.relative_to(root).as_posix(),
    }


if __name__ == "__main__":
    result = write_sorting_activation_readiness_audit(Path.cwd())
    print("PASS_PHASE_23A_SORTING_ACTIVATION_READINESS_AUDIT_WRITTEN")
    print(f"schema={result['audit']['schema']}")
    print(f"required_gates_checked={result['audit']['summary']['required_gates_checked']}")
    print(f"blocker_count={result['audit']['summary']['blocker_count']}")
    print(f"json={result['json_path']}")
    print(f"report={result['txt_path']}")
