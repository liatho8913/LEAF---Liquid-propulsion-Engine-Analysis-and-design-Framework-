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

REQUIRED = {
    "34A": REPORT_DIR / "phase_34a_public_module_control_surface.json",
    "34B": REPORT_DIR / "phase_34b_registry_persistence_and_launch_shortcut.json",
}

LAUNCHER = ROOT / "leaf_modules.py"
CONSOLE = ROOT / "project_maintenance" / "modular_engine_architecture" / "module_toggle_console.py"
SNAPSHOT = ROOT / "project_maintenance" / "modular_engine_architecture" / "module_registry_snapshot.json"


def imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return set()

    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    missing_reports = [phase for phase, path in REQUIRED.items() if not path.exists()]
    if missing_reports:
        failures.append(f"Missing Programme 34 reports: {missing_reports}")

    for path in [LAUNCHER, CONSOLE]:
        if not path.exists():
            failures.append(f"Missing required file: {path.relative_to(ROOT)}")
        else:
            py_compile.compile(str(path), doraise=True)

    if not SNAPSHOT.exists():
        failures.append(f"Missing registry snapshot: {SNAPSHOT.relative_to(ROOT)}")

    audit = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions").audit()
    manifest = audit.manifest

    if audit.status != "PASS":
        failures.append(f"Module runtime status is not PASS: {audit.status}")

    if audit.manual_runtime_binding_required:
        failures.append("Manual runtime binding required.")

    if audit.integrator_owner != "leaf_qt.module_engine.module_runtime_integrator.ModuleRuntimeIntegrator":
        failures.append("ModuleRuntimeIntegrator is not the single owner.")

    if SNAPSHOT.exists():
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        if snapshot.get("owner") != audit.integrator_owner:
            failures.append("Registry snapshot owner does not match ModuleRuntimeIntegrator.")
        if snapshot.get("module_count") != manifest.get("module_count"):
            failures.append("Registry snapshot module count does not match live manifest.")

    forbidden_duplicate_names = [
        "module_toggle_engine.py",
        "module_toggle_manager.py",
        "module_activation_engine.py",
        "module_activation_manager.py",
        "module_control_engine.py",
        "module_control_manager.py",
    ]

    duplicate_files = [
        str(path.relative_to(ROOT))
        for name in forbidden_duplicate_names
        for path in ROOT.rglob(name)
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    ]

    if duplicate_files:
        failures.append(f"Duplicate module control systems found: {duplicate_files}")

    launcher_imports = imports(LAUNCHER) if LAUNCHER.exists() else set()
    if "project_maintenance.modular_engine_architecture.module_toggle_console" not in launcher_imports:
        failures.append("leaf_modules.py does not launch the canonical module toggle console.")

    programme_complete = not failures

    result = {
        "schema": "LEAF_PROGRAMME_34_COMPLETION_GATE_V1",
        "programme": "Programme 34",
        "programme_title": "Module Registry Consolidation and Public Module Control Surface",
        "programme_complete": programme_complete,
        "missing_reports": missing_reports,
        "failures": failures,
        "launcher": str(LAUNCHER.relative_to(ROOT)),
        "console": str(CONSOLE.relative_to(ROOT)),
        "registry_snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "module_runtime_status": audit.status,
        "manual_runtime_binding_required": audit.manual_runtime_binding_required,
        "single_owner": audit.integrator_owner,
        "module_count": manifest.get("module_count"),
        "active_modules": manifest.get("active_modules", []),
        "deactivated_modules": manifest.get("deactivated_modules", []),
        "duplicate_control_systems_found": duplicate_files,
        "engineering_behaviour_changed": False,
        "completion_notice": (
            "PROGRAMME_34_COMPLETE_MODULE_CONTROL_SURFACE_SIGNED_OFF"
            if programme_complete
            else "PROGRAMME_34_COMPLETION_GATE_FAILED"
        ),
        "next_programme": "Programme 35 — Active Module Method Exposure and LEAF Integration Gate",
    }

    json_path = REPORT_DIR / "phase_34c_programme_34_completion_gate.json"
    txt_path = REPORT_DIR / "phase_34c_programme_34_completion_gate.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    txt_path.write_text(
        "\n".join([
            "LEAF Programme 34C — Programme 34 Completion Gate",
            "=" * 68,
            "",
            "programme=Programme 34",
            "programme_title=Module Registry Consolidation and Public Module Control Surface",
            f"programme_complete={programme_complete}",
            f"launcher={LAUNCHER.relative_to(ROOT)}",
            f"console={CONSOLE.relative_to(ROOT)}",
            f"registry_snapshot={SNAPSHOT.relative_to(ROOT)}",
            f"module_runtime_status={audit.status}",
            f"manual_runtime_binding_required={audit.manual_runtime_binding_required}",
            f"single_owner={audit.integrator_owner}",
            f"module_count={manifest.get('module_count')}",
            f"active_modules={','.join(manifest.get('active_modules', []))}",
            f"deactivated_modules={','.join(manifest.get('deactivated_modules', []))}",
            f"duplicate_control_systems_found={len(duplicate_files)}",
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
        print("FAIL_PHASE_34C_PROGRAMME_34_COMPLETION_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_34C_PROGRAMME_34_COMPLETION_GATE")
    print("programme=Programme 34")
    print("programme_title=Module Registry Consolidation and Public Module Control Surface")
    print(f"programme_complete={programme_complete}")
    print(f"launcher={LAUNCHER.relative_to(ROOT)}")
    print(f"console={CONSOLE.relative_to(ROOT)}")
    print(f"registry_snapshot={SNAPSHOT.relative_to(ROOT)}")
    print(f"module_runtime_status={audit.status}")
    print(f"manual_runtime_binding_required={audit.manual_runtime_binding_required}")
    print(f"single_owner={audit.integrator_owner}")
    print(f"module_count={manifest.get('module_count')}")
    print(f"active_modules={','.join(manifest.get('active_modules', []))}")
    print(f"deactivated_modules={','.join(manifest.get('deactivated_modules', []))}")
    print(f"duplicate_control_systems_found={len(duplicate_files)}")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"next_programme={result['next_programme']}")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
