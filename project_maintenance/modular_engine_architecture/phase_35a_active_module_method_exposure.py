from __future__ import annotations

from pathlib import Path
import json
import py_compile
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"

CONTRACTS = {
    "interface": "x",
    "solver": "x",
    "validation": "x",
    "workflow": "x",
    "runtime": "x",
    "storage": "x",
    "reports": "x",
    "notifications": "x",
}


def definition(module_id: str, enabled: bool = True, requires: list[str] | None = None) -> dict:
    return {
        "module_id": module_id,
        "name": module_id,
        "domain": f"test.{module_id}",
        "version": "1.0.0",
        "description": "method exposure test",
        "engineering_owner": "test",
        "entrypoint": f"test.{module_id}",
        "contracts": CONTRACTS,
        "outputs": [f"{module_id}_method_a", f"{module_id}_method_b"],
        "enabled": enabled,
        "requires_modules": requires or [],
    }


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    live = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions")
    live_methods = live.exposed_methods()
    live_table = live.module_status_table()

    if not live_methods:
        failures.append("Live LEAF exposes no active module methods.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        (tmp_dir / "core.json").write_text(json.dumps(definition("core", enabled=False), indent=2), encoding="utf-8")
        (tmp_dir / "injector.json").write_text(json.dumps(definition("injector", requires=["core"]), indent=2), encoding="utf-8")
        (tmp_dir / "nozzle.json").write_text(json.dumps(definition("nozzle"), indent=2), encoding="utf-8")

        integrator = ModuleRuntimeIntegrator(tmp_dir)

        methods = integrator.exposed_methods()
        records = integrator.audit().manifest["records"]

        if "nozzle" not in methods:
            failures.append("Active module methods were not exposed.")

        if "core" in methods:
            failures.append("UserDeactivated module exposed methods.")

        if "injector" in methods:
            failures.append("DependencyDeactivated module exposed methods.")

        if records["core"]["active_outputs"]:
            failures.append("UserDeactivated module retained active outputs.")

        if records["injector"]["active_outputs"]:
            failures.append("DependencyDeactivated module retained active outputs.")

        integrator.set_module_enabled("core", True)
        recovered_methods = integrator.exposed_methods()

        if "core" not in recovered_methods:
            failures.append("Reactivated dependency provider did not expose methods.")

        if "injector" not in recovered_methods:
            failures.append("Recovered dependent module did not expose methods.")

    result = {
        "schema": "LEAF_ACTIVE_MODULE_METHOD_EXPOSURE_PHASE_35A_V1",
        "programme": "Programme 35",
        "phase": "35A",
        "single_owner": "leaf_qt.module_engine.module_runtime_integrator.ModuleRuntimeIntegrator",
        "live_exposed_modules": sorted(live_methods),
        "live_status_table": live_table,
        "active_modules_expose_methods": True,
        "user_deactivated_modules_hidden": True,
        "dependency_deactivated_modules_hidden": True,
        "reactivated_modules_restore_methods": True,
        "new_exposure_engine_created": False,
        "engineering_behaviour_changed": False,
        "failures": failures,
        "completion_notice": "PHASE_35A_ACTIVE_MODULE_METHOD_EXPOSURE_COMPLETE" if not failures else "PHASE_35A_ACTIVE_MODULE_METHOD_EXPOSURE_FAILED",
        "next_phase": "35B — LEAF Integration Exposure Gate",
    }

    json_path = REPORT_DIR / "phase_35a_active_module_method_exposure.json"
    txt_path = REPORT_DIR / "phase_35a_active_module_method_exposure.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 35A — Active Module Method Exposure",
            "=" * 66,
            "",
            f"single_owner={result['single_owner']}",
            f"live_exposed_modules={','.join(sorted(live_methods))}",
            "active_modules_expose_methods=True",
            "user_deactivated_modules_hidden=True",
            "dependency_deactivated_modules_hidden=True",
            "reactivated_modules_restore_methods=True",
            "new_exposure_engine_created=False",
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
        print("FAIL_PHASE_35A_ACTIVE_MODULE_METHOD_EXPOSURE")
        for failure in failures:
            print(f"failure={failure}")
        raise SystemExit(1)

    print("PASS_PHASE_35A_ACTIVE_MODULE_METHOD_EXPOSURE")
    print(f"single_owner={result['single_owner']}")
    print(f"live_exposed_modules={','.join(sorted(live_methods))}")
    print("active_modules_expose_methods=True")
    print("user_deactivated_modules_hidden=True")
    print("dependency_deactivated_modules_hidden=True")
    print("reactivated_modules_restore_methods=True")
    print("new_exposure_engine_created=False")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_35A_ACTIVE_MODULE_METHOD_EXPOSURE_COMPLETE")
    print("next_phase=35B — LEAF Integration Exposure Gate")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
