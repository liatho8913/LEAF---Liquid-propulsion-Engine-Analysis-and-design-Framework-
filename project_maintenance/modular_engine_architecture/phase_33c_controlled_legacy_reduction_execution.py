from __future__ import annotations

from pathlib import Path
import json
import shutil
import py_compile
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"
PLAN_PATH = REPORT_DIR / "phase_33b_controlled_legacy_reduction_planning.json"
ARCHIVE_ROOT = ROOT / "_leaf_legacy_reduction_archive"


def main() -> None:
    failures: list[str] = []

    if not PLAN_PATH.exists():
        print("FAIL_PHASE_33C_CONTROLLED_LEGACY_REDUCTION_EXECUTION")
        print(f"failure=Missing plan: {PLAN_PATH.relative_to(ROOT)}")
        raise SystemExit(1)

    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    candidates = [
        item for item in plan.get("candidates", [])
        if item.get("recommended_action") == "DELETE_AFTER_ARCHIVE"
    ]

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = ARCHIVE_ROOT / f"phase_33c_{stamp}"

    archived: list[str] = []
    deleted: list[str] = []
    missing: list[str] = []

    for item in candidates:
        rel = item["path"]
        src = ROOT / rel

        if not src.exists():
            missing.append(rel)
            continue

        dst = archive_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        archived.append(rel)

    for rel in archived:
        src = ROOT / rel
        if src.exists():
            src.unlink()
            deleted.append(rel)

    runtime_audit = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions").audit()

    if runtime_audit.status != "PASS":
        failures.append(f"ModuleRuntimeIntegrator failed after deletion: {runtime_audit.status}")

    if runtime_audit.manual_runtime_binding_required:
        failures.append("Manual runtime binding required after deletion.")

    if len(deleted) != len(candidates):
        failures.append(f"Deleted count mismatch. planned={len(candidates)} deleted={len(deleted)} missing={len(missing)}")

    result = {
        "schema": "LEAF_CONTROLLED_LEGACY_REDUCTION_EXECUTION_PHASE_33C_V1",
        "programme": "Programme 33",
        "phase": "33C",
        "planned_delete_count": len(candidates),
        "archived_count": len(archived),
        "deleted_count": len(deleted),
        "missing_count": len(missing),
        "archive_location": str(archive_dir.relative_to(ROOT)),
        "archived_files": archived,
        "deleted_files": deleted,
        "missing_files": missing,
        "module_runtime_status_after_deletion": runtime_audit.status,
        "manual_runtime_binding_required": runtime_audit.manual_runtime_binding_required,
        "active_modules": runtime_audit.manifest.get("active_modules", []),
        "deactivated_modules": runtime_audit.manifest.get("deactivated_modules", []),
        "engineering_behaviour_changed": False,
        "failures": failures,
        "completion_notice": "PHASE_33C_CONTROLLED_LEGACY_REDUCTION_EXECUTION_COMPLETE" if not failures else "PHASE_33C_CONTROLLED_LEGACY_REDUCTION_EXECUTION_FAILED",
        "next_phase": "33D — Repository Simplification Verification",
    }

    json_path = REPORT_DIR / "phase_33c_controlled_legacy_reduction_execution.json"
    txt_path = REPORT_DIR / "phase_33c_controlled_legacy_reduction_execution.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF Programme 33C — Controlled Legacy Reduction Execution",
        "=" * 70,
        "",
        f"planned_delete_count={len(candidates)}",
        f"archived_count={len(archived)}",
        f"deleted_count={len(deleted)}",
        f"missing_count={len(missing)}",
        f"archive_location={archive_dir.relative_to(ROOT)}",
        f"module_runtime_status_after_deletion={runtime_audit.status}",
        f"manual_runtime_binding_required={runtime_audit.manual_runtime_binding_required}",
        f"active_modules={','.join(runtime_audit.manifest.get('active_modules', []))}",
        f"deactivated_modules={','.join(runtime_audit.manifest.get('deactivated_modules', []))}",
        "engineering_behaviour_changed=False",
        "",
        "Deleted files:",
        *[f"- {path}" for path in deleted],
        "",
        "Failures:",
        *[f"- {failure}" for failure in failures],
        "",
        f"completion_notice={result['completion_notice']}",
        "next_phase=33D — Repository Simplification Verification",
    ]

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if failures:
        print("FAIL_PHASE_33C_CONTROLLED_LEGACY_REDUCTION_EXECUTION")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_33C_CONTROLLED_LEGACY_REDUCTION_EXECUTION")
    print(f"planned_delete_count={len(candidates)}")
    print(f"archived_count={len(archived)}")
    print(f"deleted_count={len(deleted)}")
    print(f"missing_count={len(missing)}")
    print(f"archive_location={archive_dir.relative_to(ROOT)}")
    print(f"module_runtime_status_after_deletion={runtime_audit.status}")
    print(f"manual_runtime_binding_required={runtime_audit.manual_runtime_binding_required}")
    print(f"active_modules={','.join(runtime_audit.manifest.get('active_modules', []))}")
    print(f"deactivated_modules={','.join(runtime_audit.manifest.get('deactivated_modules', []))}")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_33C_CONTROLLED_LEGACY_REDUCTION_EXECUTION_COMPLETE")
    print("next_phase=33D — Repository Simplification Verification")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
