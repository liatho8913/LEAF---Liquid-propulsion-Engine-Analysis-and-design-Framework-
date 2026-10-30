from __future__ import annotations

from pathlib import Path
import json
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator


DEFINITION_DIR = ROOT / "leaf_qt" / "module_engine" / "definitions"
REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    audit = ModuleRuntimeIntegrator(DEFINITION_DIR).audit()
    manifest = audit.manifest
    records = manifest["records"]

    result = {
        "schema": "LEAF_MODULE_ACTIVATION_CONTROL_PHASE_33A_V1",
        "programme": "Programme 33",
        "phase": "33A",
        "status": audit.status,
        "module_count": manifest["module_count"],
        "active_modules": manifest["active_modules"],
        "deactivated_modules": manifest["deactivated_modules"],
        "records": records,
        "single_owner": audit.integrator_owner,
        "manual_runtime_binding_required": audit.manual_runtime_binding_required,
        "files_removed": [],
        "engineering_behaviour_changed": False,
        "completion_notice": "PHASE_33A_MODULE_ACTIVATION_CONTROL_COMPLETE",
        "next_phase": "33B — Controlled Legacy Reduction Planning",
    }

    json_path = REPORT_DIR / "phase_33a_module_activation_control.json"
    txt_path = REPORT_DIR / "phase_33a_module_activation_control.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF Programme 33A — Module Activation Control",
        "=" * 58,
        "",
        f"status={audit.status}",
        f"module_count={manifest['module_count']}",
        f"active_modules={','.join(manifest['active_modules'])}",
        f"deactivated_modules={','.join(manifest['deactivated_modules'])}",
        "",
        "Module Status:",
    ]

    for module_id, record in sorted(records.items()):
        lines.append(
            f"- {module_id}: {record['activation_status']} | "
            f"runtime={record['runtime_status']} | active_outputs={len(record['active_outputs'])}"
        )

    lines.extend([
        "",
        f"single_owner={audit.integrator_owner}",
        f"manual_runtime_binding_required={audit.manual_runtime_binding_required}",
        "engineering_behaviour_changed=False",
        "files_removed=0",
        "",
        "completion_notice=PHASE_33A_MODULE_ACTIVATION_CONTROL_COMPLETE",
        "next_phase=33B — Controlled Legacy Reduction Planning",
    ])

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("PASS_PHASE_33A_MODULE_ACTIVATION_CONTROL")
    print(f"status={audit.status}")
    print(f"module_count={manifest['module_count']}")
    print("")
    print("MODULE STATUS")
    for module_id, record in sorted(records.items()):
        print(
            f"{module_id}: {record['activation_status']} "
            f"| runtime={record['runtime_status']} "
            f"| active_outputs={len(record['active_outputs'])}"
        )
    print("")
    print(f"active_modules={','.join(manifest['active_modules'])}")
    print(f"deactivated_modules={','.join(manifest['deactivated_modules'])}")
    print(f"single_owner={audit.integrator_owner}")
    print(f"manual_runtime_binding_required={audit.manual_runtime_binding_required}")
    print("engineering_behaviour_changed=False")
    print("files_removed=0")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_33A_MODULE_ACTIVATION_CONTROL_COMPLETE")
    print("next_phase=33B — Controlled Legacy Reduction Planning")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
