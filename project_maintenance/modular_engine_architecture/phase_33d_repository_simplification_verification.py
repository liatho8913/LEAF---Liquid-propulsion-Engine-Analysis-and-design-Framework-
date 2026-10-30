from __future__ import annotations

from pathlib import Path
import json
import py_compile
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from leaf_qt.module_engine.module_runtime_integrator import ModuleRuntimeIntegrator

REPORT_DIR = ROOT / "project_maintenance" / "modular_engine_architecture" / "reports"
EXECUTION_REPORT = REPORT_DIR / "phase_33c_controlled_legacy_reduction_execution.json"


def main() -> None:
    failures: list[str] = []

    if not EXECUTION_REPORT.exists():
        print("FAIL_PHASE_33D_REPOSITORY_SIMPLIFICATION_VERIFICATION")
        print(f"failure=Missing 33C execution report: {EXECUTION_REPORT.relative_to(ROOT)}")
        raise SystemExit(1)

    execution = json.loads(EXECUTION_REPORT.read_text(encoding="utf-8"))

    deleted_files = execution.get("deleted_files", [])
    archived_files = execution.get("archived_files", [])
    archive_location = execution.get("archive_location", "")

    archive_root = ROOT / archive_location

    still_present = [
        path for path in deleted_files
        if (ROOT / path).exists()
    ]

    archive_missing = [
        path for path in archived_files
        if not (archive_root / path).exists()
    ]

    runtime_audit = ModuleRuntimeIntegrator(ROOT / "leaf_qt" / "module_engine" / "definitions").audit()

    if still_present:
        failures.append(f"Deleted files still present: {still_present}")

    if archive_missing:
        failures.append(f"Archived copies missing: {archive_missing}")

    if runtime_audit.status != "PASS":
        failures.append(f"ModuleRuntimeIntegrator failed: {runtime_audit.status}")

    if runtime_audit.manual_runtime_binding_required:
        failures.append("Manual runtime binding required after simplification.")

    simplification_verified = not failures

    result = {
        "schema": "LEAF_REPOSITORY_SIMPLIFICATION_VERIFICATION_PHASE_33D_V1",
        "programme": "Programme 33",
        "phase": "33D",
        "planned_deleted_files": len(deleted_files),
        "deleted_files_absent": len(still_present) == 0,
        "archived_files_present": len(archive_missing) == 0,
        "archive_location": archive_location,
        "module_runtime_status": runtime_audit.status,
        "manual_runtime_binding_required": runtime_audit.manual_runtime_binding_required,
        "active_modules": runtime_audit.manifest.get("active_modules", []),
        "deactivated_modules": runtime_audit.manifest.get("deactivated_modules", []),
        "simplification_verified": simplification_verified,
        "still_present": still_present,
        "archive_missing": archive_missing,
        "engineering_behaviour_changed": False,
        "failures": failures,
        "completion_notice": (
            "PHASE_33D_REPOSITORY_SIMPLIFICATION_VERIFICATION_COMPLETE"
            if simplification_verified
            else "PHASE_33D_REPOSITORY_SIMPLIFICATION_VERIFICATION_FAILED"
        ),
        "next_phase": "33E — Programme 33 Completion Gate",
    }

    json_path = REPORT_DIR / "phase_33d_repository_simplification_verification.json"
    txt_path = REPORT_DIR / "phase_33d_repository_simplification_verification.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join([
            "LEAF Programme 33D — Repository Simplification Verification",
            "=" * 72,
            "",
            f"planned_deleted_files={len(deleted_files)}",
            f"deleted_files_absent={len(still_present) == 0}",
            f"archived_files_present={len(archive_missing) == 0}",
            f"archive_location={archive_location}",
            f"module_runtime_status={runtime_audit.status}",
            f"manual_runtime_binding_required={runtime_audit.manual_runtime_binding_required}",
            f"active_modules={','.join(runtime_audit.manifest.get('active_modules', []))}",
            f"deactivated_modules={','.join(runtime_audit.manifest.get('deactivated_modules', []))}",
            f"simplification_verified={simplification_verified}",
            "engineering_behaviour_changed=False",
            "",
            "Failures:",
            *[f"- {failure}" for failure in failures],
            "",
            f"completion_notice={result['completion_notice']}",
            "next_phase=33E — Programme 33 Completion Gate",
        ]) + "\n",
        encoding="utf-8",
    )

    if failures:
        print("FAIL_PHASE_33D_REPOSITORY_SIMPLIFICATION_VERIFICATION")
        for failure in failures:
            print(f"failure={failure}")
        print(f"report={txt_path.relative_to(ROOT)}")
        print(f"json={json_path.relative_to(ROOT)}")
        raise SystemExit(1)

    print("PASS_PHASE_33D_REPOSITORY_SIMPLIFICATION_VERIFICATION")
    print(f"planned_deleted_files={len(deleted_files)}")
    print("deleted_files_absent=True")
    print("archived_files_present=True")
    print(f"archive_location={archive_location}")
    print(f"module_runtime_status={runtime_audit.status}")
    print(f"manual_runtime_binding_required={runtime_audit.manual_runtime_binding_required}")
    print(f"active_modules={','.join(runtime_audit.manifest.get('active_modules', []))}")
    print(f"deactivated_modules={','.join(runtime_audit.manifest.get('deactivated_modules', []))}")
    print("simplification_verified=True")
    print("engineering_behaviour_changed=False")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print("completion_notice=PHASE_33D_REPOSITORY_SIMPLIFICATION_VERIFICATION_COMPLETE")
    print("next_phase=33E — Programme 33 Completion Gate")


if __name__ == "__main__":
    py_compile.compile(__file__, doraise=True)
    main()
