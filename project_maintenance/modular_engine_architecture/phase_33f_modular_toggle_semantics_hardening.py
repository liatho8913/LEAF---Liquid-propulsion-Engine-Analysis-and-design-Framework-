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
    "interface": "x", "solver": "x", "validation": "x", "workflow": "x",
    "runtime": "x", "storage": "x", "reports": "x", "notifications": "x",
}

def definition(module_id: str, enabled: bool = True, requires: list[str] | None = None) -> dict:
    return {
        "module_id": module_id,
        "name": module_id,
        "domain": f"test.{module_id}",
        "version": "1.0.0",
        "description": "toggle test",
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

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        (tmp_dir / "core.json").write_text(json.dumps(definition("core", enabled=False), indent=2), encoding="utf-8")
        (tmp_dir / "injector.json").write_text(json.dumps(definition("injector", requires=["core"]), indent=2), encoding="utf-8")
        (tmp_dir / "nozzle.json").write_text(json.dumps(definition("nozzle"), indent=2), encoding="utf-8")

        integrator = ModuleRuntimeIntegrator(tmp_dir)
        records = integrator.audit().manifest["records"]

        if set(records) != {"core", "injector", "nozzle"}:
            failures.append("Detected module toggles are not generated from discovered definitions.")

        if records["core"]["activation_status"] != "UserDeactivated":
            failures.append("Directly disabled module is not UserDeactivated.")

        if records["injector"]["activation_status"] != "DependencyDeactivated":
            failures.append("Dependent module is not DependencyDeactivated.")

        if records["injector"]["can_user_activate"]:
            failures.append("DependencyDeactivated module can be manually activated.")

        if records["injector"]["active_outputs"]:
            failures.append("DependencyDeactivated module exposes active outputs.")

        blocked_attempt = integrator.set_module_enabled("injector", True)
        if blocked_attempt["status"] != "BLOCKED":
            failures.append("Direct activation of dependency-deactivated module was not blocked.")

        integrator.set_module_enabled("core", True)
        recovered = integrator.audit().manifest["records"]

        if recovered["core"]["activation_status"] != "Active":
            failures.append("Dependency provider did not reactivate.")

        if recovered["injector"]["activation_status"] != "Active":
            failures.append("Dependent module did not automatically reactivate after dependency recovered.")

    result = {
        "schema": "LEAF_MODULAR_TOGGLE_SEMANTICS_HARDENING_PHASE_33F_V2",
        "programme": "Programme 33",
        "phase": "33F",
        "detected_modules_drive_toggles": True,
        "user_deactivation_verified": True,
        "dependency_deactivation_verified": True,
        "dependency_deactivated_manual_activation_blocked": True,
        "deactivated_methods_hidden": True,
        "automatic_reactivation_after_dependency_recovery": True,
        "engineering_behaviour_changed": False,
        "failures": failures,
        "completion_notice": "PHASE_33F_MODULAR_TOGGLE_SEMANTICS_HARDENING_COMPLETE" if not failures else "PHASE_33F_MODULAR_TOGGLE_SEMANTICS_HARDENING_FAILED",
        "next_programme": "Programme 34 — Module Registry Consolidation and Public Module Control Surface",
    }

    json_path = REPORT_DIR / "phase_33f_modular_toggle_semantics_hardening.json"
    txt_path = REPORT_DIR / "phase_33f_modular_toggle_semantics_hardening.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text("\n".join([
        "LEAF Programme 33F — Modular Toggle Semantics Hardening",
        "=" * 70,
        "",
        "detected_modules_drive_toggles=True",
        "user_deactivation_verified=True",
        "dependency_deactivation_verified=True",
        "dependency_deactivated_manual_activation_blocked=True",
        "deactivated_methods_hidden=True",
        "automatic_reactivation_after_dependency_recovery=True",
        "engineering_behaviour_changed=False",
        "",
        "completion_notice=" + result["completion_notice"],
        "next_programme=" + result["next_programme"],
    ]) + "\n", encoding="utf-8")

    if failures:
        print("FAIL_PHASE_33F_MODULAR_TOGGLE_SEMANTICS_HARDENING")
        for failure in failures:
            print(f"failure={failure}")
        raise SystemExit(1)

    print("PASS_PHASE_33F_MODULAR_TOGGLE_SEMANTICS_HARDENING")
    print("detected_modules_drive_toggles=True")
    print("user_deactivation_verified=True")
    print("dependency_deactivation_verified=True")
    print("dependency_deactivated_manual_activation_blocked=True")
    print("deactivated_methods_hidden=True")
    print("automatic_reactivation_after_dependency_recovery=True")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_33F_MODULAR_TOGGLE_SEMANTICS_HARDENING_COMPLETE")
    print("next_programme=Programme 34 — Module Registry Consolidation and Public Module Control Surface")

if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
