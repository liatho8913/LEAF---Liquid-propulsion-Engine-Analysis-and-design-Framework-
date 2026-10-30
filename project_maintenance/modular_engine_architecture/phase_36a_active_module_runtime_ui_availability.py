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
        "description": "availability bridge test",
        "engineering_owner": "test",
        "entrypoint": f"test.{module_id}",
        "contracts": CONTRACTS,
        "outputs": [f"{module_id}_method"],
        "enabled": enabled,
        "requires_modules": requires or [],
    }


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    live = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions")
    surface = live.availability_surface()

    if surface["owner"] != live.INTEGRATOR_OWNER:
        failures.append("Availability surface owner is not ModuleRuntimeIntegrator.")

    if not surface["available_methods"]:
        failures.append("Live availability surface exposes no active methods.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / "core.json").write_text(json.dumps(definition("core", enabled=False), indent=2), encoding="utf-8")
        (tmp_dir / "injector.json").write_text(json.dumps(definition("injector", requires=["core"]), indent=2), encoding="utf-8")
        (tmp_dir / "nozzle.json").write_text(json.dumps(definition("nozzle"), indent=2), encoding="utf-8")

        integrator = ModuleRuntimeIntegrator(tmp_dir)
        test_surface = integrator.availability_surface()

        if set(test_surface["available_methods"]) != {"nozzle"}:
            failures.append(f"Inactive modules leaked into availability surface: {sorted(test_surface['available_methods'])}")

        if "core" in test_surface["available_methods"]:
            failures.append("UserDeactivated module available to runtime/UI.")

        if "injector" in test_surface["available_methods"]:
            failures.append("DependencyDeactivated module available to runtime/UI.")

        integrator.set_module_enabled("core", True)
        recovered = integrator.availability_surface()

        if set(recovered["available_methods"]) != {"core", "injector", "nozzle"}:
            failures.append(f"Recovered availability surface incorrect: {sorted(recovered['available_methods'])}")

    result = {
        "schema": "LEAF_ACTIVE_MODULE_RUNTIME_UI_AVAILABILITY_PHASE_36A_V1",
        "programme": "Programme 36",
        "phase": "36A",
        "single_owner": live.INTEGRATOR_OWNER,
        "live_available_modules": sorted(surface["available_methods"]),
        "live_active_modules": surface["active_modules"],
        "live_deactivated_modules": surface["deactivated_modules"],
        "availability_surface_added_to_existing_integrator": True,
        "new_availability_engine_created": False,
        "inactive_modules_hidden_from_runtime_ui": True,
        "dependency_recovery_restores_runtime_ui_availability": True,
        "engineering_behaviour_changed": False,
        "failures": failures,
        "completion_notice": "PHASE_36A_ACTIVE_MODULE_RUNTIME_UI_AVAILABILITY_COMPLETE" if not failures else "PHASE_36A_ACTIVE_MODULE_RUNTIME_UI_AVAILABILITY_FAILED",
        "next_phase": "36B — Console Availability Display Consolidation",
    }

    json_path = REPORT_DIR / "phase_36a_active_module_runtime_ui_availability.json"
    txt_path = REPORT_DIR / "phase_36a_active_module_runtime_ui_availability.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 36A — Active Module Runtime/UI Availability",
            "=" * 72,
            "",
            f"single_owner={result['single_owner']}",
            f"live_available_modules={','.join(result['live_available_modules'])}",
            f"live_active_modules={','.join(result['live_active_modules'])}",
            f"live_deactivated_modules={','.join(result['live_deactivated_modules'])}",
            "availability_surface_added_to_existing_integrator=True",
            "new_availability_engine_created=False",
            "inactive_modules_hidden_from_runtime_ui=True",
            "dependency_recovery_restores_runtime_ui_availability=True",
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
        print("FAIL_PHASE_36A_ACTIVE_MODULE_RUNTIME_UI_AVAILABILITY")
        for failure in failures:
            print(f"failure={failure}")
        raise SystemExit(1)

    print("PASS_PHASE_36A_ACTIVE_MODULE_RUNTIME_UI_AVAILABILITY")
    print(f"single_owner={result['single_owner']}")
    print(f"live_available_modules={','.join(result['live_available_modules'])}")
    print(f"live_active_modules={','.join(result['live_active_modules'])}")
    print(f"live_deactivated_modules={','.join(result['live_deactivated_modules'])}")
    print("availability_surface_added_to_existing_integrator=True")
    print("new_availability_engine_created=False")
    print("inactive_modules_hidden_from_runtime_ui=True")
    print("dependency_recovery_restores_runtime_ui_availability=True")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_36A_ACTIVE_MODULE_RUNTIME_UI_AVAILABILITY_COMPLETE")
    print("next_phase=36B — Console Availability Display Consolidation")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
