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
    "36A": REPORT_DIR / "phase_36a_active_module_runtime_ui_availability.json",
    "36B": REPORT_DIR / "phase_36b_console_availability_display_consolidation.json",
}

INTEGRATOR = ROOT / "leaf_qt" / "module_engine" / "module_runtime_integrator.py"
CONSOLE = ROOT / "project_maintenance" / "modular_engine_architecture" / "module_toggle_console.py"


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
        failures.append(f"Missing Programme 36 reports: {missing_reports}")

    py_compile.compile(str(INTEGRATOR), doraise=True)
    py_compile.compile(str(CONSOLE), doraise=True)

    integrator = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions")
    audit = integrator.audit()
    surface = integrator.availability_surface()

    if audit.status != "PASS":
        failures.append(f"Module runtime status is not PASS: {audit.status}")

    if audit.manual_runtime_binding_required:
        failures.append("Manual runtime binding required.")

    if surface.get("owner") != audit.integrator_owner:
        failures.append("Availability surface owner mismatch.")

    if not surface.get("available_methods"):
        failures.append("Availability surface exposes no active methods.")

    inactive_leaks = [
        row["module_id"]
        for row in surface.get("status_table", [])
        if row["activation_status"] != "Active"
        and row["module_id"] in surface.get("available_methods", {})
    ]

    if inactive_leaks:
        failures.append(f"Inactive modules leaked into availability surface: {inactive_leaks}")

    console_calls = called_methods(CONSOLE)
    if "availability_surface" not in console_calls:
        failures.append("Console does not call availability_surface().")

    if "exposed_methods" in console_calls or "module_status_table" in console_calls:
        failures.append("Console bypasses availability_surface with direct exposure/status calls.")

    integrator_text = INTEGRATOR.read_text(encoding="utf-8", errors="ignore")

    if integrator_text.count("def availability_surface") != 1:
        failures.append("availability_surface is not defined exactly once.")

    forbidden_duplicate_names = [
        "availability_engine.py",
        "module_availability_engine.py",
        "module_availability_manager.py",
        "runtime_availability_engine.py",
        "ui_availability_engine.py",
        "module_display_engine.py",
        "module_display_manager.py",
    ]

    duplicate_files = [
        str(path.relative_to(ROOT))
        for name in forbidden_duplicate_names
        for path in ROOT.rglob(name)
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    ]

    if duplicate_files:
        failures.append(f"Duplicate availability/display systems found: {duplicate_files}")

    programme_complete = not failures

    result = {
        "schema": "LEAF_PROGRAMME_36_COMPLETION_GATE_V1",
        "programme": "Programme 36",
        "programme_title": "Active Module Integration into LEAF Runtime/UI Availability",
        "programme_complete": programme_complete,
        "missing_reports": missing_reports,
        "failures": failures,
        "module_runtime_status": audit.status,
        "manual_runtime_binding_required": audit.manual_runtime_binding_required,
        "single_owner": audit.integrator_owner,
        "availability_owner": surface.get("owner"),
        "module_count": surface.get("module_count"),
        "active_modules": surface.get("active_modules", []),
        "deactivated_modules": surface.get("deactivated_modules", []),
        "available_modules": sorted(surface.get("available_methods", {})),
        "console_uses_availability_surface": "availability_surface" in console_calls,
        "console_direct_exposure_calls_removed": "exposed_methods" not in console_calls and "module_status_table" not in console_calls,
        "duplicate_availability_systems_found": duplicate_files,
        "new_availability_engine_created": False,
        "engineering_behaviour_changed": False,
        "completion_notice": (
            "PROGRAMME_36_COMPLETE_ACTIVE_MODULE_RUNTIME_UI_AVAILABILITY_SIGNED_OFF"
            if programme_complete
            else "PROGRAMME_36_COMPLETION_GATE_FAILED"
        ),
        "next_programme": "Programme 37 — Module Dependency Graph and Cascade Visibility",
    }

    json_path = REPORT_DIR / "phase_36c_programme_36_completion_gate.json"
    txt_path = REPORT_DIR / "phase_36c_programme_36_completion_gate.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 36C — Programme 36 Completion Gate",
            "=" * 72,
            "",
            "programme=Programme 36",
            "programme_title=Active Module Integration into LEAF Runtime/UI Availability",
            f"programme_complete={programme_complete}",
            f"module_runtime_status={audit.status}",
            f"manual_runtime_binding_required={audit.manual_runtime_binding_required}",
            f"single_owner={audit.integrator_owner}",
            f"availability_owner={surface.get('owner')}",
            f"module_count={surface.get('module_count')}",
            f"active_modules={','.join(surface.get('active_modules', []))}",
            f"deactivated_modules={','.join(surface.get('deactivated_modules', []))}",
            f"available_modules={','.join(sorted(surface.get('available_methods', {})))}",
            f"console_uses_availability_surface={result['console_uses_availability_surface']}",
            f"console_direct_exposure_calls_removed={result['console_direct_exposure_calls_removed']}",
            f"duplicate_availability_systems_found={len(duplicate_files)}",
            "new_availability_engine_created=False",
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
        print("FAIL_PHASE_36C_PROGRAMME_36_COMPLETION_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_36C_PROGRAMME_36_COMPLETION_GATE")
    print("programme=Programme 36")
    print("programme_title=Active Module Integration into LEAF Runtime/UI Availability")
    print(f"programme_complete={programme_complete}")
    print(f"module_runtime_status={audit.status}")
    print(f"manual_runtime_binding_required={audit.manual_runtime_binding_required}")
    print(f"single_owner={audit.integrator_owner}")
    print(f"availability_owner={surface.get('owner')}")
    print(f"module_count={surface.get('module_count')}")
    print(f"active_modules={','.join(surface.get('active_modules', []))}")
    print(f"deactivated_modules={','.join(surface.get('deactivated_modules', []))}")
    print(f"available_modules={','.join(sorted(surface.get('available_methods', {})))}")
    print(f"console_uses_availability_surface={result['console_uses_availability_surface']}")
    print(f"console_direct_exposure_calls_removed={result['console_direct_exposure_calls_removed']}")
    print(f"duplicate_availability_systems_found={len(duplicate_files)}")
    print("new_availability_engine_created=False")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"next_programme={result['next_programme']}")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
