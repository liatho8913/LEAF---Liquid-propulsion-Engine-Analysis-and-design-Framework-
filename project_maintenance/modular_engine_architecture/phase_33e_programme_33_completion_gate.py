from __future__ import annotations

from pathlib import Path
import json
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"

REQUIRED_REPORTS = {
    "33A": "phase_33a_module_activation_control.json",
    "33B": "phase_33b_controlled_legacy_reduction_planning.json",
    "33C": "phase_33c_controlled_legacy_reduction_execution.json",
    "33D": "phase_33d_repository_simplification_verification.json",
}


def read_report(filename: str) -> dict:
    path = REPORT_DIR / filename
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    failures: list[str] = []

    missing_reports = [
        phase for phase, filename in REQUIRED_REPORTS.items()
        if not (REPORT_DIR / filename).exists()
    ]

    if missing_reports:
        failures.append(f"Missing reports: {missing_reports}")

    phase_33a = read_report(REQUIRED_REPORTS["33A"])
    phase_33b = read_report(REQUIRED_REPORTS["33B"])
    phase_33c = read_report(REQUIRED_REPORTS["33C"])
    phase_33d = read_report(REQUIRED_REPORTS["33D"])

    runtime = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions").audit()
    manifest = runtime.manifest

    if runtime.status != "PASS":
        failures.append(f"Module runtime status is not PASS: {runtime.status}")

    if runtime.manual_runtime_binding_required:
        failures.append("Manual runtime binding required.")

    if not manifest.get("records"):
        failures.append("No module runtime records found.")

    for module_id, record in manifest.get("records", {}).items():
        if record.get("activation_status") not in {"Active", "Deactivated"}:
            failures.append(f"{module_id} has invalid activation status.")

        if record.get("activation_status") == "Deactivated" and record.get("active_outputs"):
            failures.append(f"{module_id} is deactivated but still exposes active outputs.")

    if phase_33c.get("deleted_count", 0) <= 0:
        failures.append("33C did not delete any files.")

    if phase_33c.get("deleted_count") != phase_33c.get("archived_count"):
        failures.append("33C deleted count does not match archived count.")

    if phase_33d.get("simplification_verified") is not True:
        failures.append("33D simplification verification did not pass.")

    if phase_33d.get("deleted_files_absent") is not True:
        failures.append("Deleted files are still present.")

    if phase_33d.get("archived_files_present") is not True:
        failures.append("Archived files are missing.")

    for phase, report in {
        "33A": phase_33a,
        "33B": phase_33b,
        "33C": phase_33c,
        "33D": phase_33d,
    }.items():
        if report.get("engineering_behaviour_changed"):
            failures.append(f"{phase} reported engineering behaviour changed.")

    programme_complete = not failures

    result = {
        "schema": "LEAF_PROGRAMME_33_COMPLETION_GATE_V1",
        "programme": "Programme 33",
        "programme_title": "Controlled Modular Simplification and Legacy Reduction",
        "programme_complete": programme_complete,
        "missing_reports": missing_reports,
        "failures": failures,
        "module_runtime_status": runtime.status,
        "manual_runtime_binding_required": runtime.manual_runtime_binding_required,
        "module_count": manifest.get("module_count"),
        "active_modules": manifest.get("active_modules", []),
        "deactivated_modules": manifest.get("deactivated_modules", []),
        "deleted_files": phase_33c.get("deleted_count", 0),
        "archived_files": phase_33c.get("archived_count", 0),
        "simplification_verified": phase_33d.get("simplification_verified"),
        "engineering_behaviour_changed": False,
        "completion_notice": (
            "PROGRAMME_33_COMPLETE_CONTROLLED_MODULAR_SIMPLIFICATION_SIGNED_OFF"
            if programme_complete
            else "PROGRAMME_33_COMPLETION_GATE_FAILED"
        ),
        "next_programme": "Programme 34 — Module Registry Consolidation and Public Module Control Surface",
    }

    json_path = REPORT_DIR / "phase_33e_programme_33_completion_gate.json"
    txt_path = REPORT_DIR / "phase_33e_programme_33_completion_gate.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join([
            "LEAF Programme 33E — Programme 33 Completion Gate",
            "=" * 66,
            "",
            "programme=Programme 33",
            "programme_title=Controlled Modular Simplification and Legacy Reduction",
            f"programme_complete={programme_complete}",
            f"missing_reports={missing_reports}",
            f"module_runtime_status={runtime.status}",
            f"manual_runtime_binding_required={runtime.manual_runtime_binding_required}",
            f"module_count={manifest.get('module_count')}",
            f"active_modules={','.join(manifest.get('active_modules', []))}",
            f"deactivated_modules={','.join(manifest.get('deactivated_modules', []))}",
            f"deleted_files={phase_33c.get('deleted_count', 0)}",
            f"archived_files={phase_33c.get('archived_count', 0)}",
            f"simplification_verified={phase_33d.get('simplification_verified')}",
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
        print("FAIL_PHASE_33E_PROGRAMME_33_COMPLETION_GATE")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_33E_PROGRAMME_33_COMPLETION_GATE")
    print("programme=Programme 33")
    print("programme_title=Controlled Modular Simplification and Legacy Reduction")
    print(f"programme_complete={programme_complete}")
    print(f"module_runtime_status={runtime.status}")
    print(f"manual_runtime_binding_required={runtime.manual_runtime_binding_required}")
    print(f"module_count={manifest.get('module_count')}")
    print(f"active_modules={','.join(manifest.get('active_modules', []))}")
    print(f"deactivated_modules={','.join(manifest.get('deactivated_modules', []))}")
    print(f"deleted_files={phase_33c.get('deleted_count', 0)}")
    print(f"archived_files={phase_33c.get('archived_count', 0)}")
    print(f"simplification_verified={phase_33d.get('simplification_verified')}")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"next_programme={result['next_programme']}")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
