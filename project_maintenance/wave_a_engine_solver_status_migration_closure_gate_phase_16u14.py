from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path


PHASE = "16U.14"
PASS_BANNER = "PASS_PHASE_16U14_WAVE_A_ENGINE_SOLVER_STATUS_MIGRATION_CLOSURE_GATE"

REQUIRED_JSON = {
    "16U.8": Path("project_maintenance/engine_solver_low_risk_status_wrapper_patch_phase_16u8.json"),
    "16U.9": Path("project_maintenance/engine_solver_low_risk_status_wrapper_regression_phase_16u9.json"),
    "16U.10": Path("project_maintenance/engine_solver_medium_risk_status_consumer_audit_phase_16u10.json"),
    "16U.11": Path("project_maintenance/engine_solver_medium_risk_status_wrapper_patch_phase_16u11.json"),
    "16U.12": Path("project_maintenance/engine_solver_medium_risk_status_wrapper_regression_phase_16u12.json"),
    "16U.13": Path("project_maintenance/engine_solver_remaining_status_consumer_review_phase_16u13.json"),
}

EXPECTED_STATUSES = {
    "16U.8": "PASS_PHASE_16U8_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_PATCH",
    "16U.9": "PASS_PHASE_16U9_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_REGRESSION",
    "16U.10": "PASS_PHASE_16U10_ENGINE_SOLVER_MEDIUM_RISK_STATUS_CONSUMER_AUDIT",
    "16U.11": "PASS_PHASE_16U11_ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_PATCH",
    "16U.12": "PASS_PHASE_16U12_ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_REGRESSION",
    "16U.13": "PASS_PHASE_16U13_ENGINE_SOLVER_REMAINING_STATUS_CONSUMER_REVIEW",
}

ENGINE = Path("leaf_qt/engine_solver.py")
GEOMETRY = Path("leaf_qt/regen_geometry_solver.py")
SOLVER_ACCESS = Path("leaf_qt/solver_status_access.py")
STRUCTURED_ACCESS = Path("leaf_qt/structured_status_access.py")

OUT_JSON = Path("project_maintenance/wave_a_engine_solver_status_migration_closure_gate_phase_16u14.json")
OUT_TXT = Path("project_maintenance/WAVE_A_ENGINE_SOLVER_STATUS_MIGRATION_CLOSURE_GATE_PHASE_16U14.txt")


REQUIRED_TOKENS = [
    "solver_pass(",
    "solver_fail(",
    "solver_highest_severity(",
    "status_solver_pass(",
]

FORBIDDEN_TOKENS = [
    'results.get("coupled_split_auto_tuned_status") != "PASS"',
    'results.get("coupled_split_auto_tuned_status") == "PASS"',
    'results.get("velocity_limited_combined_preview_status") == "FAIL"',
    'results.get("coupled_split_strategy_status") == "FAIL"',
    'results.get("vl_split_strategy_status") == "PASS"',
    'results.get("bond_coat_validation_status") != "PASS"',
    'source_data_gate != "PASS"',
    'weighted_gate != "PASS"',
    'results.get("explicit_coating_thermal_stress_status") == "FAIL"',
    'results.get("coating_stack_adhesion_risk_status") != "PASS"',
    'results.get("coating_stack_spallation_fatigue_status") != "PASS"',
    'results.get("coating_stack_source_data_gate") != "PASS"',
    'bond_status != "PASS"',
    'thermal_stress_status != "PASS"',
    'adhesion_status != "PASS"',
    'fatigue_status != "PASS"',
    'preview_status != "PASS"',
    'combined_status != "PASS"',
    'viability == "PASS"',
    'item.get("status") == "PASS"',
    'item["status"] != "FAIL"',
    'status != "FAIL"',
    'candidate_report.get("status") == "PASS"',
    'if status not in ("REQUIRED", "PASS"):',
    'if "FAIL" in statuses:',
    'elif "WARN" in statuses:',
    'solver_pass = solver_pass(',
]


def compile_file(path: Path) -> dict:
    try:
        py_compile.compile(str(path), doraise=True)
        return {"file": str(path), "passed": True, "error": ""}
    except Exception as exc:
        return {"file": str(path), "passed": False, "error": repr(exc)}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_gate() -> dict:
    missing_files = [str(path) for path in [ENGINE, GEOMETRY, SOLVER_ACCESS, STRUCTURED_ACCESS] if not path.exists()]
    missing_json = [str(path) for path in REQUIRED_JSON.values() if not path.exists()]

    phase_status_checks = []
    loaded = {}

    if not missing_json:
        for phase, path in REQUIRED_JSON.items():
            payload = read_json(path)
            loaded[phase] = payload
            expected = EXPECTED_STATUSES[phase]
            phase_status_checks.append(
                {
                    "phase": phase,
                    "expected": expected,
                    "actual": payload.get("status"),
                    "passed": payload.get("status") == expected,
                }
            )

    engine_text = ENGINE.read_text(encoding="utf-8", errors="replace") if ENGINE.exists() else ""
    geometry_text = GEOMETRY.read_text(encoding="utf-8", errors="replace") if GEOMETRY.exists() else ""
    combined_text = engine_text + "\n" + geometry_text

    missing_required_tokens = [token for token in REQUIRED_TOKENS if token not in combined_text]
    forbidden_tokens_present = [token for token in FORBIDDEN_TOKENS if token in combined_text]

    compile_results = [compile_file(path) for path in [ENGINE, GEOMETRY, SOLVER_ACCESS, STRUCTURED_ACCESS] if path.exists()]

    phase_16u13 = loaded.get("16U.13", {})
    remaining_count = int(phase_16u13.get("remaining_candidate_count", -1))
    blocker_count = int(phase_16u13.get("wave_closure_blocker_count", -1))

    checks = [
        {
            "name": "required_source_files_present",
            "passed": not missing_files,
            "detail": f"{len(missing_files)} missing",
        },
        {
            "name": "required_phase_json_present",
            "passed": not missing_json,
            "detail": f"{len(missing_json)} missing",
        },
        {
            "name": "all_required_phase_statuses_passed",
            "passed": bool(phase_status_checks) and all(item["passed"] for item in phase_status_checks),
            "detail": f"{sum(1 for item in phase_status_checks if item['passed'])}/{len(phase_status_checks)} passed",
        },
        {
            "name": "required_wrapper_tokens_present",
            "passed": not missing_required_tokens,
            "detail": f"{len(missing_required_tokens)} missing",
        },
        {
            "name": "patched_legacy_tokens_absent",
            "passed": not forbidden_tokens_present,
            "detail": f"{len(forbidden_tokens_present)} present",
        },
        {
            "name": "remaining_consumers_recorded",
            "passed": remaining_count >= 0,
            "detail": str(remaining_count),
        },
        {
            "name": "wave_closure_blockers_absent",
            "passed": blocker_count == 0,
            "detail": str(blocker_count),
        },
        {
            "name": "all_closure_files_compile",
            "passed": bool(compile_results) and all(item["passed"] for item in compile_results),
            "detail": f"{sum(1 for item in compile_results if item['passed'])}/{len(compile_results)} compiled",
        },
    ]

    passed = all(check["passed"] for check in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U14_WAVE_A_ENGINE_SOLVER_STATUS_MIGRATION_CLOSURE_GATE",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "missing_files": missing_files,
        "missing_json": missing_json,
        "phase_status_checks": phase_status_checks,
        "missing_required_tokens": missing_required_tokens,
        "forbidden_tokens_present": forbidden_tokens_present,
        "remaining_candidate_count": remaining_count,
        "wave_closure_blocker_count": blocker_count,
        "compile_results": compile_results,
        "checks": checks,
        "wave_a_engine_solver_status_migration_closed": passed,
        "phase_16u14_wave_a_engine_solver_status_migration_closure_gate_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.14",
        "WAVE A ENGINE SOLVER STATUS MIGRATION CLOSURE GATE",
        "===================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase closes Wave A solver status migration.",
        "No production files are modified.",
        "No solver equations are modified.",
        "",
        "SUMMARY",
        "-------",
        f"Remaining consumers recorded: {remaining_count}",
        f"Wave closure blockers: {blocker_count}",
        f"Missing required tokens: {len(missing_required_tokens)}",
        f"Forbidden patched legacy tokens present: {len(forbidden_tokens_present)}",
        "",
        "CHECKS",
        "------",
    ]

    for check in checks:
        lines.append(f"{check['name']}: {'PASS' if check['passed'] else 'FAIL'} — {check['detail']}")

    lines.extend(["", "PHASE STATUS CHECKS", "-------------------"])
    for item in phase_status_checks:
        lines.append(
            f"{item['phase']}: {'PASS' if item['passed'] else 'FAIL'} "
            f"expected={item['expected']} actual={item['actual']}"
        )

    lines.extend(["", "COMPILE RESULTS", "---------------"])
    for item in compile_results:
        lines.append(f"{item['file']}: {'PASS' if item['passed'] else 'FAIL'} {item['error']}")

    if forbidden_tokens_present:
        lines.extend(["", "FORBIDDEN TOKENS PRESENT", "------------------------"])
        lines.extend(forbidden_tokens_present)

    if missing_required_tokens:
        lines.extend(["", "MISSING REQUIRED TOKENS", "-----------------------"])
        lines.extend(missing_required_tokens)

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.14 COMPLETE." if passed else "PHASE 16U.14 FAILED.",
            "WAVE A ENGINE SOLVER STATUS MIGRATION CLOSED." if passed else "WAVE A ENGINE SOLVER STATUS MIGRATION NOT CLOSED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.15 — WAVE B VALIDATION OWNER STATUS CONSUMER MIGRATION AUDIT",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_gate()
    print(result["status"])
    print(f"remaining_candidate_count={result['remaining_candidate_count']}")
    print(f"wave_closure_blocker_count={result['wave_closure_blocker_count']}")
    print(f"wave_a_engine_solver_status_migration_closed={result['wave_a_engine_solver_status_migration_closed']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u14_wave_a_engine_solver_status_migration_closure_gate_complete"]:
        raise SystemExit(1)
