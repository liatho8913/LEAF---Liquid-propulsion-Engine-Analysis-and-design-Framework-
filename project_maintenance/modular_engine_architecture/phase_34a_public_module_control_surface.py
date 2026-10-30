from __future__ import annotations

from pathlib import Path
import json
import py_compile
import shutil
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"
ARCHIVE_ROOT = ROOT / "_leaf_legacy_reduction_archive"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    console = ROOT / "project_maintenance" / "modular_engine_architecture" / "module_toggle_console.py"
    old_gate = ROOT / "project_maintenance" / "modular_engine_architecture" / "phase_33g_terminal_module_toggle_console.py"

    py_compile.compile(str(console), doraise=True)

    archived_deleted: list[str] = []
    if old_gate.exists():
        archive = ARCHIVE_ROOT / f"phase_34a_{datetime.now().strftime('%Y%m%d_%H%M%S')}" / old_gate.relative_to(ROOT)
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(old_gate, archive)
        old_gate.unlink()
        archived_deleted.append(str(old_gate.relative_to(ROOT)))

    audit = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions").audit()
    manifest = audit.manifest
    records = manifest["records"]

    if audit.status != "PASS":
        failures.append(f"Module runtime status is not PASS: {audit.status}")

    if audit.manual_runtime_binding_required:
        failures.append("Manual runtime binding required.")

    if not records:
        failures.append("No modules detected.")

    for module_id, record in records.items():
        if record["activation_status"] != "Active" and record["active_outputs"]:
            failures.append(f"{module_id} exposes active outputs while deactivated.")

    result = {
        "schema": "LEAF_PUBLIC_MODULE_CONTROL_SURFACE_PHASE_34A_V1",
        "programme": "Programme 34",
        "phase": "34A",
        "public_control_surface": str(console.relative_to(ROOT)),
        "module_count": manifest["module_count"],
        "active_modules": manifest["active_modules"],
        "deactivated_modules": manifest["deactivated_modules"],
        "single_owner": audit.integrator_owner,
        "manual_runtime_binding_required": audit.manual_runtime_binding_required,
        "archived_deleted_files": archived_deleted,
        "new_toggle_engine_created": False,
        "engineering_behaviour_changed": False,
        "failures": failures,
        "completion_notice": "PHASE_34A_PUBLIC_MODULE_CONTROL_SURFACE_COMPLETE" if not failures else "PHASE_34A_PUBLIC_MODULE_CONTROL_SURFACE_FAILED",
        "next_phase": "34B — Registry Persistence and Launch Shortcut",
    }

    json_path = REPORT_DIR / "phase_34a_public_module_control_surface.json"
    txt_path = REPORT_DIR / "phase_34a_public_module_control_surface.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 34A — Public Module Control Surface",
            "=" * 66,
            "",
            f"public_control_surface={console.relative_to(ROOT)}",
            f"module_count={manifest['module_count']}",
            f"active_modules={','.join(manifest['active_modules'])}",
            f"deactivated_modules={','.join(manifest['deactivated_modules'])}",
            f"single_owner={audit.integrator_owner}",
            f"manual_runtime_binding_required={audit.manual_runtime_binding_required}",
            f"archived_deleted_files={len(archived_deleted)}",
            "new_toggle_engine_created=False",
            "engineering_behaviour_changed=False",
            "",
            "Failures:",
            *[f"- {failure}" for failure in failures],
            "",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
        ]) + "\n",
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_34A_PUBLIC_MODULE_CONTROL_SURFACE")
        for failure in failures:
            print(f"failure={failure}")
        raise SystemExit(1)

    print("PASS_PHASE_34A_PUBLIC_MODULE_CONTROL_SURFACE")
    print(f"public_control_surface={console.relative_to(ROOT)}")
    print(f"module_count={manifest['module_count']}")
    print(f"active_modules={','.join(manifest['active_modules'])}")
    print(f"deactivated_modules={','.join(manifest['deactivated_modules'])}")
    print(f"single_owner={audit.integrator_owner}")
    print(f"manual_runtime_binding_required={audit.manual_runtime_binding_required}")
    print(f"archived_deleted_files={len(archived_deleted)}")
    print("new_toggle_engine_created=False")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_34A_PUBLIC_MODULE_CONTROL_SURFACE_COMPLETE")
    print("next_phase=34B — Registry Persistence and Launch Shortcut")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
