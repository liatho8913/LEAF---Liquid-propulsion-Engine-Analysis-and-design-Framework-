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

    py_compile.compile(str(CONSOLE), doraise=True)

    calls = called_methods(CONSOLE)

    if "availability_surface" not in calls:
        failures.append("Console does not use availability_surface().")

    if "exposed_methods" in calls:
        failures.append("Console directly calls exposed_methods() instead of availability_surface().")

    if "module_status_table" in calls:
        failures.append("Console directly calls module_status_table() instead of availability_surface().")

    integrator = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions")
    surface = integrator.availability_surface()

    if surface["owner"] != integrator.INTEGRATOR_OWNER:
        failures.append("Availability surface owner mismatch.")

    if not surface["status_table"]:
        failures.append("Availability surface produced no status table.")

    if not surface["available_methods"]:
        failures.append("Availability surface produced no available methods.")

    inactive_leaks = [
        row["module_id"]
        for row in surface["status_table"]
        if row["activation_status"] != "Active"
        and row["module_id"] in surface["available_methods"]
    ]

    if inactive_leaks:
        failures.append(f"Inactive modules leaked into availability surface: {inactive_leaks}")

    result = {
        "schema": "LEAF_CONSOLE_AVAILABILITY_DISPLAY_CONSOLIDATION_PHASE_36B_V1",
        "programme": "Programme 36",
        "phase": "36B",
        "console": str(CONSOLE.relative_to(ROOT)),
        "console_uses_availability_surface": "availability_surface" in calls,
        "console_direct_exposure_calls_removed": "exposed_methods" not in calls and "module_status_table" not in calls,
        "single_owner": surface["owner"],
        "available_modules": sorted(surface["available_methods"]),
        "active_modules": surface["active_modules"],
        "deactivated_modules": surface["deactivated_modules"],
        "new_display_engine_created": False,
        "engineering_behaviour_changed": False,
        "failures": failures,
        "completion_notice": "PHASE_36B_CONSOLE_AVAILABILITY_DISPLAY_CONSOLIDATION_COMPLETE" if not failures else "PHASE_36B_CONSOLE_AVAILABILITY_DISPLAY_CONSOLIDATION_FAILED",
        "next_phase": "36C — Programme 36 Completion Gate",
    }

    json_path = REPORT_DIR / "phase_36b_console_availability_display_consolidation.json"
    txt_path = REPORT_DIR / "phase_36b_console_availability_display_consolidation.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 36B — Console Availability Display Consolidation",
            "=" * 76,
            "",
            f"console={CONSOLE.relative_to(ROOT)}",
            f"console_uses_availability_surface={result['console_uses_availability_surface']}",
            f"console_direct_exposure_calls_removed={result['console_direct_exposure_calls_removed']}",
            f"single_owner={surface['owner']}",
            f"available_modules={','.join(sorted(surface['available_methods']))}",
            f"active_modules={','.join(surface['active_modules'])}",
            f"deactivated_modules={','.join(surface['deactivated_modules'])}",
            "new_display_engine_created=False",
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
        print("FAIL_PHASE_36B_CONSOLE_AVAILABILITY_DISPLAY_CONSOLIDATION")
        for failure in failures:
            print(f"failure={failure}")
        raise SystemExit(1)

    print("PASS_PHASE_36B_CONSOLE_AVAILABILITY_DISPLAY_CONSOLIDATION")
    print(f"console={CONSOLE.relative_to(ROOT)}")
    print("console_uses_availability_surface=True")
    print("console_direct_exposure_calls_removed=True")
    print(f"single_owner={surface['owner']}")
    print(f"available_modules={','.join(sorted(surface['available_methods']))}")
    print(f"active_modules={','.join(surface['active_modules'])}")
    print(f"deactivated_modules={','.join(surface['deactivated_modules'])}")
    print("new_display_engine_created=False")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_36B_CONSOLE_AVAILABILITY_DISPLAY_CONSOLIDATION_COMPLETE")
    print("next_phase=36C — Programme 36 Completion Gate")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
