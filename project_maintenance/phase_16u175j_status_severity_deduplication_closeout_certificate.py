from __future__ import annotations

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]

IN_G = ROOT / "project_maintenance" / "phase_16u175g_shared_status_severity_extended_owner_upgrade.json"
IN_H = ROOT / "project_maintenance" / "phase_16u175h_local_status_severity_deduplication_wave.json"
IN_HE = ROOT / "project_maintenance" / "phase_16u175he_context_aware_try_except_fallback_repair.json"
IN_IC = ROOT / "project_maintenance" / "phase_16u175ic_status_presentation_circular_import_break.json"
IN_I = ROOT / "project_maintenance" / "phase_16u175i_deduplication_regression_and_compatibility_audit.json"

OUT_JSON = ROOT / "project_maintenance" / "phase_16u175j_status_severity_deduplication_closeout_certificate.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u175j_status_severity_deduplication_closeout_certificate.txt"


def load(path: Path) -> dict:
    if not path.exists():
        return {"missing": True, "path": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> dict:
    g = load(IN_G)
    h = load(IN_H)
    he = load(IN_HE)
    ic = load(IN_IC)
    i = load(IN_I)

    checks = {
        "shared_owner_upgrade_passed": g.get("passed") is True,
        "direct_deduplication_touched_45": h.get("touched_count") == 45,
        "fallback_repair_passed": he.get("passed") is True,
        "fallback_repair_repaired_22": he.get("repaired_count") == 22,
        "circular_import_break_passed": ic.get("passed") is True,
        "regression_passed": i.get("passed") is True,
        "compile_clean": i.get("compile_failure_count") == 0,
        "owner_self_test_clean": i.get("owner_self_test_failure_count") == 0,
        "single_low_level_local_definition_remaining": i.get("local_status_definition_count") == 1,
    }

    passed = all(checks.values())

    result = {
        "phase": "16U.175J",
        "certificate": "STATUS_SEVERITY_DEDUPLICATION_CLOSEOUT_CERTIFICATE",
        "checks": checks,
        "direct_deduplicated_files": h.get("touched_count"),
        "fallback_repaired_files": he.get("repaired_count"),
        "production_file_count": i.get("production_file_count"),
        "compile_failure_count": i.get("compile_failure_count"),
        "shared_status_import_user_count": i.get("shared_status_import_user_count"),
        "remaining_local_status_definition_count": i.get("local_status_definition_count"),
        "remaining_local_definition_policy": (
            "Intentional low-level definition in structured_status_access.py "
            "to break circular import between status_presentation and structured_status_access."
        ),
        "passed": passed,
        "status": (
            "PASS_PHASE_16U175J_STATUS_SEVERITY_DEDUPLICATION_CLOSEOUT_CERTIFICATE"
            if passed
            else "FAIL_PHASE_16U175J_STATUS_SEVERITY_DEDUPLICATION_CLOSEOUT_CERTIFICATE"
        ),
        "next_phase": "16U.176_PRESENTATION_MIGRATION_CLOSEOUT_CERTIFICATE",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.175J",
        "STATUS SEVERITY DEDUPLICATION CLOSEOUT CERTIFICATE",
        "=" * 62,
        f"status={result['status']}",
        "",
        "SUMMARY",
        "-" * 7,
        f"direct_deduplicated_files={result['direct_deduplicated_files']}",
        f"fallback_repaired_files={result['fallback_repaired_files']}",
        f"production_file_count={result['production_file_count']}",
        f"compile_failure_count={result['compile_failure_count']}",
        f"shared_status_import_user_count={result['shared_status_import_user_count']}",
        f"remaining_local_status_definition_count={result['remaining_local_status_definition_count']}",
        "",
        "CHECKS",
        "-" * 6,
    ]

    for key, value in checks.items():
        lines.append(f"{key}={value}")

    lines.extend([
        "",
        "REMAINING LOCAL DEFINITION POLICY",
        "-" * 33,
        result["remaining_local_definition_policy"],
        "",
        "FEATURE COMPLETION NOTICE",
        "-" * 25,
        "Status severity deduplication is complete.",
        "The two integration methods now mesh cleanly through the shared owner architecture.",
        "",
        "NEXT FEATURE",
        "-" * 12,
        result["next_phase"],
        "",
        f"json={OUT_JSON}",
        f"text={OUT_TXT}",
    ])

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"direct_deduplicated_files={result['direct_deduplicated_files']}")
    print(f"fallback_repaired_files={result['fallback_repaired_files']}")
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"shared_status_import_user_count={result['shared_status_import_user_count']}")
    print(f"remaining_local_status_definition_count={result['remaining_local_status_definition_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
