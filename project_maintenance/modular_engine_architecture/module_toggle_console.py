from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

DEFINITION_DIR = ROOT / "leaf_qt" / "module_engine" / "definitions"


def print_modules(integrator: ModuleRuntimeIntegrator) -> list[str]:
    surface = integrator.availability_surface()
    rows = surface["status_table"]
    available = surface["available_methods"]
    ids = [row["module_id"] for row in rows]

    print("")
    print("LEAF MODULE CONTROL")
    print("=" * 72)
    print(f"active={','.join(surface['active_modules']) or '-'}")
    print(f"deactivated={','.join(surface['deactivated_modules']) or '-'}")
    print("")

    for index, row in enumerate(rows, 1):
        module_id = row["module_id"]
        requires = ",".join(row["requires_modules"]) or "-"
        method_count = len(available.get(module_id, []))
        print(
            f"{index}. {module_id:<20} [{row['activation_status']:<21}] "
            f"methods={method_count:<2} "
            f"can_activate={str(row['can_user_activate']):<5} "
            f"requires={requires}"
        )

    print("")
    print("Select a module number to toggle.")
    print("r = refresh | q = quit")
    print("")
    return ids


def yes(prompt: str) -> bool | None:
    value = input(prompt).strip().lower()
    if value in {"y", "yes"}:
        return True
    if value in {"n", "no"}:
        return False
    return None


def main() -> None:
    integrator = ModuleRuntimeIntegrator(DEFINITION_DIR)

    while True:
        ids = print_modules(integrator)
        records = integrator.availability_surface()["status_table"]
        record_map = {record["module_id"]: record for record in records}

        choice = input("Select module> ").strip().lower()

        if choice in {"q", "quit", "exit"}:
            print("closed=True")
            return

        if choice in {"r", "refresh", "status"}:
            continue

        if not choice.isdigit() or not 1 <= int(choice) <= len(ids):
            print("Invalid selection.")
            continue

        module_id = ids[int(choice) - 1]
        record = record_map[module_id]
        status = record["activation_status"]

        if status == "Active":
            answer = yes(f"{module_id} is Active. Deactivate? [y/n] ")
            if answer is True:
                result = integrator.set_module_enabled(module_id, False)
                print(f"{module_id}: [{result.get('activation_status', result['status'])}]")
            elif answer is False:
                print("cancelled=True")
            else:
                print("Invalid answer. Use y or n.")

        elif status == "UserDeactivated":
            answer = yes(f"{module_id} is UserDeactivated. Activate? [y/n] ")
            if answer is True:
                result = integrator.set_module_enabled(module_id, True)
                print(f"{module_id}: [{result.get('activation_status', result['status'])}]")
            elif answer is False:
                print("cancelled=True")
            else:
                print("Invalid answer. Use y or n.")

        elif status == "DependencyDeactivated":
            print(f"{module_id} is DependencyDeactivated.")
            print("Activate its required modules first.")

        elif status == "Blocked":
            print(f"{module_id} is Blocked.")
            print("Fix runtime or verification before toggling.")

        else:
            print(f"{module_id} has unknown status: {status}")


if __name__ == "__main__":
    main()
