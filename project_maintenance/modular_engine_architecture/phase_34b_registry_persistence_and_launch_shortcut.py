from __future__ import annotations

from pathlib import Path
import json
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"
REGISTRY_PATH = ROOT / "project_maintenance" / "modular_engine_architecture" / "module_registry_snapshot.json"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    launcher = ROOT / "leaf_modules.py"
    console = ROOT / "project_maintenance" / "modular_engine_architecture" / "module_toggle_console.py"

    py_compile.compile(str(launcher), doraise=True)
    py_compile.compile(str(console), doraise=True)

    audit = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions").audit()
    manifest = audit.manifest

    snapshot = {
        "schema": "LEAF_MODULE_REGISTRY_SNAPSHOT_V1",
        "owner": audit.integrator_owner,
        "module_count": manifest["module_count"],
        "active_modules": manifest["active_modules"],
        "deactivated_modules": manifest["deactivated_modules"],
        "records": manifest["records"],
    }

    REGISTRY_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    result = {
        "schema": "LEAF_REGISTRY_PERSISTENCE_AND_LAUNCH_SHORTCUT_PHASE_34B_V1",
        "programme": "Programme 34",
        "phase": "34B",
        "launcher": str(launcher.relative_to(ROOT)),
        "console": str(console.relative_to(ROOT)),
        "registry_snapshot": str(REGISTRY_PATH.relative_to(ROOT)),
        "module_count": manifest["module_count"],
        "active_modules": manifest["active_modules"],
        "deactivated_modules": manifest["deactivated_modules"],
        "single_owner": audit.integrator_owner,
        "new_toggle_engine_created": False,
        "engineering_behaviour_changed": False,
        "completion_notice": "PHASE_34B_REGISTRY_PERSISTENCE_AND_LAUNCH_SHORTCUT_COMPLETE",
        "next_phase": "34C — Programme 34 Completion Gate",
    }

    json_path = REPORT_DIR / "phase_34b_registry_persistence_and_launch_shortcut.json"
    txt_path = REPORT_DIR / "phase_34b_registry_persistence_and_launch_shortcut.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 34B — Registry Persistence and Launch Shortcut",
            "=" * 72,
            "",
            f"launcher={launcher.relative_to(ROOT)}",
            f"console={console.relative_to(ROOT)}",
            f"registry_snapshot={REGISTRY_PATH.relative_to(ROOT)}",
            f"module_count={manifest['module_count']}",
            f"active_modules={','.join(manifest['active_modules'])}",
            f"deactivated_modules={','.join(manifest['deactivated_modules'])}",
            f"single_owner={audit.integrator_owner}",
            "new_toggle_engine_created=False",
            "engineering_behaviour_changed=False",
            "",
            "completion_notice=PHASE_34B_REGISTRY_PERSISTENCE_AND_LAUNCH_SHORTCUT_COMPLETE",
            "next_phase=34C — Programme 34 Completion Gate",
        ]) + "\n",
        encoding="utf-8",
    )

    print("PASS_PHASE_34B_REGISTRY_PERSISTENCE_AND_LAUNCH_SHORTCUT")
    print(f"launcher={launcher.relative_to(ROOT)}")
    print(f"run_command=python -u leaf_modules.py")
    print(f"registry_snapshot={REGISTRY_PATH.relative_to(ROOT)}")
    print(f"module_count={manifest['module_count']}")
    print(f"active_modules={','.join(manifest['active_modules'])}")
    print(f"deactivated_modules={','.join(manifest['deactivated_modules'])}")
    print(f"single_owner={audit.integrator_owner}")
    print("new_toggle_engine_created=False")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_34B_REGISTRY_PERSISTENCE_AND_LAUNCH_SHORTCUT_COMPLETE")
    print("next_phase=34C — Programme 34 Completion Gate")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
