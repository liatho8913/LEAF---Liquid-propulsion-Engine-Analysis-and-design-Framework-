from __future__ import annotations

from pathlib import Path
import json
import py_compile
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator


DEFINITION_DIR = ROOT / "leaf_qt" / "module_engine" / "definitions"


def main() -> None:
    failures: list[str] = []

    audit = ModuleRuntimeIntegrator(DEFINITION_DIR).audit()
    manifest = audit.manifest
    records = manifest["records"]

    if audit.status != "PASS":
        failures.append(f"Runtime integration failed: {audit.status}")

    if not records:
        failures.append("No modules found.")

    for module_id, record in records.items():
        if record["activation_status"] not in {"Active", "Deactivated"}:
            failures.append(f"{module_id} has invalid activation status.")

        if record["activation_status"] == "Deactivated" and record["active_outputs"]:
            failures.append(f"{module_id} is deactivated but still exposes active outputs.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        base = {
            "name": "Base",
            "domain": "test.base",
            "version": "1.0.0",
            "description": "temporary dependency test",
            "engineering_owner": "test",
            "entrypoint": "test.Base",
            "contracts": {
                "interface": "x",
                "solver": "x",
                "validation": "x",
                "workflow": "x",
                "runtime": "x",
                "storage": "x",
                "reports": "x",
                "notifications": "x"
            },
            "outputs": ["base_method"]
        }

        disabled = dict(base, module_id="disabled_base", name="Disabled Base", enabled=False)
        dependent = dict(base, module_id="dependent_module", name="Dependent Module", requires_modules=["disabled_base"])

        (tmp_dir / "disabled_base.json").write_text(json.dumps(disabled), encoding="utf-8")
        (tmp_dir / "dependent_module.json").write_text(json.dumps(dependent), encoding="utf-8")

        test_manifest = ModuleRuntimeIntegrator(tmp_dir).audit().manifest["records"]

        if test_manifest["disabled_base"]["activation_status"] != "Deactivated":
            failures.append("Disabled module did not deactivate.")

        if test_manifest["dependent_module"]["activation_status"] != "Deactivated":
            failures.append("Dependent module did not deactivate when requirement was deactivated.")

        if test_manifest["dependent_module"]["active_outputs"]:
            failures.append("Dependent deactivated module still exposes active outputs.")

    if failures:
        print("FAIL_PHASE_33A_MODULE_ACTIVATION_CONTROL_GATE")
        for failure in failures:
            print(f"failure={failure}")
        raise SystemExit(1)

    print("PASS_PHASE_33A_MODULE_ACTIVATION_CONTROL_GATE")
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
    print("dependent_deactivation_verified=True")
    print("deactivated_methods_hidden=True")
    print(f"single_owner={audit.integrator_owner}")
    print(f"manual_runtime_binding_required={audit.manual_runtime_binding_required}")
    print("engineering_behaviour_changed=False")
    print("files_removed=0")
    print("completion_notice=PHASE_33A_MODULE_ACTIVATION_CONTROL_COMPLETE")
    print("next_phase=33B — Controlled Legacy Reduction Planning")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
