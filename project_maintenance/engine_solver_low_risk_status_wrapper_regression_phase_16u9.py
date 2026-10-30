from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path


PHASE = "16U.9"
PASS_BANNER = "PASS_PHASE_16U9_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_REGRESSION"

PATCH_JSON = Path("project_maintenance/engine_solver_low_risk_status_wrapper_patch_phase_16u8.json")
PLAN_JSON = Path("project_maintenance/engine_solver_status_patch_planner_phase_16u7.json")
OUT_JSON = Path("project_maintenance/engine_solver_low_risk_status_wrapper_regression_phase_16u9.json")
OUT_TXT = Path("project_maintenance/ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_REGRESSION_PHASE_16U9.txt")

ENGINE = Path("leaf_qt/engine_solver.py")
GEOMETRY = Path("leaf_qt/regen_geometry_solver.py")

ENGINE_IMPORT = "from leaf_qt.solver_status_access import solver_fail, solver_pass"
GEOMETRY_IMPORT = "from leaf_qt.solver_status_access import solver_pass as status_solver_pass"


REQUIRED_TOKENS = [
    'not solver_pass(results.get("coupled_split_auto_tuned_status"))',
    'solver_pass(results.get("coupled_split_auto_tuned_status"))',
    'solver_fail(results.get("velocity_limited_combined_preview_status"))',
    'solver_fail(results.get("coupled_split_strategy_status"))',
    'solver_pass(results.get("vl_split_strategy_status"))',
    'not solver_pass(results.get("bond_coat_validation_status"))',
    'not solver_pass(source_data_gate)',
    'not solver_pass(weighted_gate)',
    'solver_fail(results.get("explicit_coating_thermal_stress_status"))',
    'not solver_pass(results.get("coating_stack_adhesion_risk_status"))',
    'not solver_pass(results.get("coating_stack_spallation_fatigue_status"))',
    'not solver_pass(results.get("coating_stack_source_data_gate"))',
    'not solver_pass(source_gate)',
    'not solver_pass(bond_status)',
    'not solver_pass(thermal_stress_status)',
    'not solver_pass(adhesion_status)',
    'not solver_pass(fatigue_status)',
    'not solver_pass(preview_status)',
    'not solver_pass(combined_status)',
    'solver_pass(viability)',
    'solver_pass(item.get("status"))',
    'not solver_fail(item.get("status"))',
    'not solver_fail(status)',
    'status_solver_pass(candidate_report.get("status"))',
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
    'solver_pass = solver_pass(',
]


def compile_file(path: Path) -> dict:
    try:
        py_compile.compile(str(path), doraise=True)
        return {"file": str(path), "passed": True, "error": ""}
    except Exception as exc:
        return {"file": str(path), "passed": False, "error": repr(exc)}


def run_regression() -> dict:
    if not PATCH_JSON.exists():
        raise FileNotFoundError(f"Missing {PATCH_JSON}. Run Phase 16U.8 first.")
    if not PLAN_JSON.exists():
        raise FileNotFoundError(f"Missing {PLAN_JSON}. Run Phase 16U.7 first.")

    patch = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
    plan = json.loads(PLAN_JSON.read_text(encoding="utf-8"))

    engine_text = ENGINE.read_text(encoding="utf-8", errors="replace")
    geometry_text = GEOMETRY.read_text(encoding="utf-8", errors="replace")
    combined_text = engine_text + "\n" + geometry_text

    missing_required_tokens = [
        token for token in REQUIRED_TOKENS
        if token not in combined_text
    ]

    forbidden_tokens_present = [
        token for token in FORBIDDEN_TOKENS
        if token in combined_text
    ]

    checks = [
        {
            "name": "phase_16u8_patch_passed",
            "passed": patch.get("status") == "PASS_PHASE_16U8_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_PATCH",
            "detail": str(patch.get("status")),
        },
        {
            "name": "phase_16u7_plan_available",
            "passed": plan.get("status") == "PASS_PHASE_16U7_ENGINE_SOLVER_STATUS_PATCH_PLANNER",
            "detail": str(plan.get("status")),
        },
        {
            "name": "engine_import_present",
            "passed": ENGINE_IMPORT in engine_text,
            "detail": ENGINE_IMPORT,
        },
        {
            "name": "geometry_alias_import_present",
            "passed": GEOMETRY_IMPORT in geometry_text,
            "detail": GEOMETRY_IMPORT,
        },
        {
            "name": "required_wrapper_tokens_present",
            "passed": not missing_required_tokens,
            "detail": f"{len(missing_required_tokens)} missing",
        },
        {
            "name": "forbidden_legacy_tokens_absent",
            "passed": not forbidden_tokens_present,
            "detail": f"{len(forbidden_tokens_present)} present",
        },
    ]

    compile_results = [compile_file(ENGINE), compile_file(GEOMETRY)]
    for item in compile_results:
        checks.append(
            {
                "name": f"compile_{Path(item['file']).name}",
                "passed": item["passed"],
                "detail": item["error"],
            }
        )

    passed = all(check["passed"] for check in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U9_ENGINE_SOLVER_LOW_RISK_STATUS_WRAPPER_REGRESSION",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "missing_required_token_count": len(missing_required_tokens),
        "forbidden_token_present_count": len(forbidden_tokens_present),
        "missing_required_tokens": missing_required_tokens,
        "forbidden_tokens_present": forbidden_tokens_present,
        "compile_results": compile_results,
        "checks": checks,
        "phase_16u9_engine_solver_low_risk_status_wrapper_regression_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.9",
        "ENGINE SOLVER LOW-RISK STATUS WRAPPER REGRESSION",
        "=================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase verifies the Phase 16U.8 low-risk solver wrapper patch.",
        "No production files are modified.",
        "No solver equations are modified.",
        "",
        "SUMMARY",
        "-------",
        f"Missing required wrapper tokens: {result['missing_required_token_count']}",
        f"Forbidden legacy tokens present: {result['forbidden_token_present_count']}",
        "",
        "CHECKS",
        "------",
    ]

    for check in checks:
        lines.append(f"{check['name']}: {'PASS' if check['passed'] else 'FAIL'} — {check['detail']}")

    if missing_required_tokens:
        lines.extend(["", "MISSING REQUIRED TOKENS", "-----------------------"])
        lines.extend(missing_required_tokens)

    if forbidden_tokens_present:
        lines.extend(["", "FORBIDDEN TOKENS PRESENT", "------------------------"])
        lines.extend(forbidden_tokens_present)

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.9 COMPLETE." if passed else "PHASE 16U.9 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.10 — ENGINE SOLVER MEDIUM-RISK STATUS CONSUMER AUDIT",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_regression()
    print(result["status"])
    print(f"missing_required_token_count={result['missing_required_token_count']}")
    print(f"forbidden_token_present_count={result['forbidden_token_present_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u9_engine_solver_low_risk_status_wrapper_regression_complete"]:
        raise SystemExit(1)
