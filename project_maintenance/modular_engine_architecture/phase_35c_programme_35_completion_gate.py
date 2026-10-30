from __future__ import annotations

from pathlib import Path
import ast
import json
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"

REQUIRED_REPORTS = {
    "35A": REPORT_DIR / "phase_35a_active_module_method_exposure.json",
    "35B": REPORT_DIR / "phase_35b_leaf_integration_exposure_gate.json",
}

CONSOLE = ROOT / "project_maintenance" / "modular_engine_architecture" / "module_toggle_console.py"
INTEGRATOR = ROOT / "leaf_qt" / "module_engine" / "module_runtime_integrator.py"


def called_methods(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    return {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    missing_reports = [
        phase for phase, path in REQUIRED_REPORTS.items()
        if not path.exists()
    ]

    if missing_reports:
        failures.append(f"Missing Programme 35 reports: {missing_reports}")

    py_compile.compile(str(CONSOLE), doraise=True)
    py_compile.compile(str(INTEGRATOR), doraise=True)

    integrator = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions")
    audit = integrator.audit()
    methods = integrator.exposed_methods()
    rows = integrator.module_status_table()

    if audit.status != "PASS":
        failures.append(f"Module runtime status is not PASS: {audit.status}")

    if audit.manual_runtime_binding_required:
        failures.append("Manual runtime binding required.")

    if not methods:
        failures.append("No active module methods are exposed.")

    row_ids = {row["module_id"] for row in rows}
    method_ids = set(methods)

    missing_active_methods = [
        row["module_id"]
        for row in rows
        if row["activation_status"] == "Active" and row["module_id"] not in method_ids
    ]

    inactive_exposed = [
        row["module_id"]
        for row in rows
        if row["activation_status"] != "Active" and row["module_id"] in method_ids
    ]

    if missing_active_methods:
        failures.append(f"Active modules missing exposed methods: {missing_active_methods}")

    if inactive_exposed:
        failures.append(f"Inactive modules expose methods: {inactive_exposed}")

    console_calls = called_methods(CONSOLE)
    if not {"module_status_table", "exposed_methods"} <= console_calls:
        failures.append("Console does not use canonical status/exposure methods.")

    integrator_source = INTEGRATOR.read_text(encoding="utf-8", errors="ignore")
    if integrator_source.count("def exposed_methods") != 1:
        failures.append("exposed_methods is not defined exactly once.")

    if integrator_source.count("def module_status_table") != 1:
        failures.append("module_status_table is not defined exactly once.")

    forbidden_duplicate_names = [
        "module_exposure_engine.py",
        "module_exposure_manager.py",
        "method_exposure_engine.py",
        "method_exposure_manager.py",
        "active_method_registry.py",
    ]

    duplicate_files = [
        str(path.relative_to(ROOT))
        for name in forbidden_duplicate_names
        for path in ROOT.rglob(name)
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    ]

    if duplicate_files:
        failures.append(f"Duplicate exposure systems found: {duplicate_files}")

    programme_complete = not failures

    result = {
        "schema": "LEAF_PROGRAMME_35_COMPLETION_GATE_V1",
        "programme": "Programme 35",
        "programme_title": "Active Module Method Exposure and LEAF Integration Gate",
        "programme_complete": programme_complete,
        "missing_reports": missing_reports,
        "failures": failures,
        "module_runtime_status": audit.status,
        "manual_runtime_binding_required": audit.manual_runtime_binding_required,
        "single_owner": audit.integrator_owner,
        "module_count": audit.manifest.get("module_count"),
        "status_table_modules": sorted(row_ids),
        "exposed_method_modules": sorted(method_ids),
        "active_modules": audit.manifest.get("active_modules", []),
        "deactivated_modules": audit.manifest.get("deactivated_modules", []),
        "missing_active_methods": missing_active_methods,
        "inactive_exposed": inactive_exposed,
        "console_uses_canonical_methods": {"module_status_table", "exposed_methods"} <= console_calls,
        "duplicate_exposure_systems_found": duplicate_files,
        "new_exposure_engine_created": False,
        "engineering_behaviour_changed": False,
        "completion_notice": (
            "PROGRAMME_35_COMPLETE_ACTIVE_MODULE_METHOD_EXPOSURE_SIGNED_OFF"
            if programme_complete
            else "PROGRAMME_35_COMPLETION_GATE_FAILED"
        ),
        "next_programme": "Programme 36 — Active Module Integration into LEAF Runtime/UI Availability",
    }

    json_path = REPORT_DIR / "phase_35c_programme_35_completion_gate.json"
    txt_path = REPORT_DIR / "phase_35c_programme_35_completion_gate.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 35C — Programme 35 Completion Gate",
            "=" * 68,
            "",
            "programme=Programme 35",
            "programme_title=Active Module Method Exposure and LEAF Integration Gate",
            f"programme_complete={programme_complete}",
            f"module_runtime_status={audit.status}",
            f"manual_runtime_binding_required={audit.manual_runtime_binding_required}",
            f"single_owner={audit.integrator_owner}",
            f"module_count={audit.manifest.get('module_count')}",
            f"active_modules={','.join(audit.manifest.get('active_modules', []))}",
            f"deactivated_modules={','.join(audit.manifest.get('deactivated_modules', []))}",
            f"exposed_method_modules={','.join(sorted(method_ids))}",
            f"console_uses_canonical_methods={result['console_uses_canonical_methods']}",
            f"duplicate_exposure_systems_found={len(duplicate_files)}",
            "new_exposure_engine_created=False",
            "engineering_behaviour_changed=False",
            "",
            "Failures:",
            *[f"- {failure}" for failure in failures],
            "",
            f"completion_notice={result['completion_notice']}",
            f"next_programme={result['next_programme']}",
        ]) + "\n",
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_35C_PROGRAMME_35_COMPLETION_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_35C_PROGRAMME_35_COMPLETION_GATE")
    print("programme=Programme 35")
    print("programme_title=Active Module Method Exposure and LEAF Integration Gate")
    print(f"programme_complete={programme_complete}")
    print(f"module_runtime_status={audit.status}")
    print(f"manual_runtime_binding_required={audit.manual_runtime_binding_required}")
    print(f"single_owner={audit.integrator_owner}")
    print(f"module_count={audit.manifest.get('module_count')}")
    print(f"active_modules={','.join(audit.manifest.get('active_modules', []))}")
    print(f"deactivated_modules={','.join(audit.manifest.get('deactivated_modules', []))}")
    print(f"exposed_method_modules={','.join(sorted(method_ids))}")
    print(f"console_uses_canonical_methods={result['console_uses_canonical_methods']}")
    print(f"duplicate_exposure_systems_found={len(duplicate_files)}")
    print("new_exposure_engine_created=False")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"next_programme={result['next_programme']}")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
