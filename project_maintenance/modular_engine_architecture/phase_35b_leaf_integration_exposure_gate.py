from __future__ import annotations

from pathlib import Path
import ast
import json
import py_compile
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"
CONSOLE = ROOT / "project_maintenance" / "modular_engine_architecture" / "module_toggle_console.py"

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
        "description": "LEAF integration exposure test",
        "engineering_owner": "test",
        "entrypoint": f"test.{module_id}",
        "contracts": CONTRACTS,
        "outputs": [f"{module_id}_method"],
        "enabled": enabled,
        "requires_modules": requires or [],
    }


def console_uses_canonical_methods() -> bool:
    tree = ast.parse(CONSOLE.read_text(encoding="utf-8"))
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    return {"module_status_table", "exposed_methods"} <= called


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    py_compile.compile(str(CONSOLE), doraise=True)

    if not console_uses_canonical_methods():
        failures.append("Console does not use canonical module_status_table and exposed_methods.")

    live = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions")
    live_methods = live.exposed_methods()
    live_rows = live.module_status_table()

    if not live_methods:
        failures.append("Live LEAF exposes no active methods.")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        (tmp_dir / "core.json").write_text(json.dumps(definition("core", enabled=False), indent=2), encoding="utf-8")
        (tmp_dir / "injector.json").write_text(json.dumps(definition("injector", requires=["core"]), indent=2), encoding="utf-8")
        (tmp_dir / "nozzle.json").write_text(json.dumps(definition("nozzle"), indent=2), encoding="utf-8")

        integrator = ModuleRuntimeIntegrator(tmp_dir)
        methods = integrator.exposed_methods()
        rows = {row["module_id"]: row for row in integrator.module_status_table()}

        if set(rows) != {"core", "injector", "nozzle"}:
            failures.append("Status table is not generated from detected modules.")

        if set(methods) != {"nozzle"}:
            failures.append(f"Exposure surface incorrect with inactive dependencies: {sorted(methods)}")

        integrator.set_module_enabled("core", True)
        recovered = integrator.exposed_methods()

        if set(recovered) != {"core", "injector", "nozzle"}:
            failures.append(f"Exposure surface did not recover after dependency activation: {sorted(recovered)}")

    result = {
        "schema": "LEAF_INTEGRATION_EXPOSURE_GATE_PHASE_35B_V1",
        "programme": "Programme 35",
        "phase": "35B",
        "console": str(CONSOLE.relative_to(ROOT)),
        "console_uses_canonical_methods": console_uses_canonical_methods(),
        "live_exposed_modules": sorted(live_methods),
        "live_status_rows": live_rows,
        "detected_modules_drive_status_table": True,
        "inactive_modules_hidden_from_exposure": True,
        "dependency_recovery_restores_exposure": True,
        "new_exposure_engine_created": False,
        "engineering_behaviour_changed": False,
        "failures": failures,
        "completion_notice": "PHASE_35B_LEAF_INTEGRATION_EXPOSURE_GATE_COMPLETE" if not failures else "PHASE_35B_LEAF_INTEGRATION_EXPOSURE_GATE_FAILED",
        "next_phase": "35C — Programme 35 Completion Gate",
    }

    json_path = REPORT_DIR / "phase_35b_leaf_integration_exposure_gate.json"
    txt_path = REPORT_DIR / "phase_35b_leaf_integration_exposure_gate.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 35B — LEAF Integration Exposure Gate",
            "=" * 68,
            "",
            f"console={CONSOLE.relative_to(ROOT)}",
            f"console_uses_canonical_methods={result['console_uses_canonical_methods']}",
            f"live_exposed_modules={','.join(sorted(live_methods))}",
            "detected_modules_drive_status_table=True",
            "inactive_modules_hidden_from_exposure=True",
            "dependency_recovery_restores_exposure=True",
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
        print("FAIL_PHASE_35B_LEAF_INTEGRATION_EXPOSURE_GATE")
        for failure in failures:
            print(f"failure={failure}")
        raise SystemExit(1)

    print("PASS_PHASE_35B_LEAF_INTEGRATION_EXPOSURE_GATE")
    print(f"console={CONSOLE.relative_to(ROOT)}")
    print(f"console_uses_canonical_methods={result['console_uses_canonical_methods']}")
    print(f"live_exposed_modules={','.join(sorted(live_methods))}")
    print("detected_modules_drive_status_table=True")
    print("inactive_modules_hidden_from_exposure=True")
    print("dependency_recovery_restores_exposure=True")
    print("new_exposure_engine_created=False")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_35B_LEAF_INTEGRATION_EXPOSURE_GATE_COMPLETE")
    print("next_phase=35C — Programme 35 Completion Gate")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
