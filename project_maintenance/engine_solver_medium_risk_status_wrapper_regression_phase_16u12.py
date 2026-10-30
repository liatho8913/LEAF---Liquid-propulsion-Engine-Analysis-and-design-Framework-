from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path


PHASE = "16U.12"
PASS_BANNER = "PASS_PHASE_16U12_ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_REGRESSION"

PATCH_JSON = Path("project_maintenance/engine_solver_medium_risk_status_wrapper_patch_phase_16u11.json")
AUDIT_JSON = Path("project_maintenance/engine_solver_medium_risk_status_consumer_audit_phase_16u10.json")
OUT_JSON = Path("project_maintenance/engine_solver_medium_risk_status_wrapper_regression_phase_16u12.json")
OUT_TXT = Path("project_maintenance/ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_REGRESSION_PHASE_16U12.txt")

ENGINE = Path("leaf_qt/engine_solver.py")

REQUIRED_TOKENS = [
    'from leaf_qt.solver_status_access import solver_fail, solver_highest_severity, solver_pass',
    'if status != "REQUIRED" and not solver_pass(status):',
    'if solver_highest_severity(statuses) == "FAIL":',
    'elif solver_highest_severity(statuses) == "WARN":',
]

FORBIDDEN_PATCHED_TOKENS = [
    'if status not in ("REQUIRED", "PASS"):',
    'if "FAIL" in statuses:',
    'elif "WARN" in statuses:',
]

MANUAL_REVIEW_TOKENS = [
    'elif source_data_weighted_gate in ("PARTIAL", "FAIL"):',
    'if item["status"] in ("MISSING", "PLACEHOLDER", "FAIL")',
    'verdict.endswith("PASS")',
    'if "FAIL" in text or "INVALID" in text:',
    'elif "WARN" in text or "REVIEW" in text:',
]


def compile_engine() -> dict:
    try:
        py_compile.compile(str(ENGINE), doraise=True)
        return {"file": str(ENGINE), "passed": True, "error": ""}
    except Exception as exc:
        return {"file": str(ENGINE), "passed": False, "error": repr(exc)}


def run_regression() -> dict:
    if not PATCH_JSON.exists():
        raise FileNotFoundError(f"Missing {PATCH_JSON}. Run Phase 16U.11 first.")
    if not AUDIT_JSON.exists():
        raise FileNotFoundError(f"Missing {AUDIT_JSON}. Run Phase 16U.10 first.")

    patch = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    text = ENGINE.read_text(encoding="utf-8", errors="replace")

    missing_required = [token for token in REQUIRED_TOKENS if token not in text]
    forbidden_present = [token for token in FORBIDDEN_PATCHED_TOKENS if token in text]
    manual_review_missing = [token for token in MANUAL_REVIEW_TOKENS if token not in text]

    compile_result = compile_engine()

    checks = [
        {
            "name": "phase_16u10_audit_passed",
            "passed": audit.get("status") == "PASS_PHASE_16U10_ENGINE_SOLVER_MEDIUM_RISK_STATUS_CONSUMER_AUDIT",
            "detail": str(audit.get("status")),
        },
        {
            "name": "phase_16u11_patch_passed",
            "passed": patch.get("status") == "PASS_PHASE_16U11_ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_PATCH",
            "detail": str(patch.get("status")),
        },
        {
            "name": "required_medium_risk_wrapper_tokens_present",
            "passed": not missing_required,
            "detail": f"{len(missing_required)} missing",
        },
        {
            "name": "legacy_patched_tokens_absent",
            "passed": not forbidden_present,
            "detail": f"{len(forbidden_present)} present",
        },
        {
            "name": "manual_review_tokens_preserved",
            "passed": not manual_review_missing,
            "detail": f"{len(manual_review_missing)} missing",
        },
        {
            "name": "engine_solver_compiles",
            "passed": compile_result["passed"],
            "detail": compile_result["error"],
        },
    ]

    passed = all(check["passed"] for check in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U12_ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_REGRESSION",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "missing_required_count": len(missing_required),
        "forbidden_present_count": len(forbidden_present),
        "manual_review_missing_count": len(manual_review_missing),
        "missing_required": missing_required,
        "forbidden_present": forbidden_present,
        "manual_review_missing": manual_review_missing,
        "compile_result": compile_result,
        "checks": checks,
        "phase_16u12_engine_solver_medium_risk_status_wrapper_regression_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.12",
        "ENGINE SOLVER MEDIUM-RISK STATUS WRAPPER REGRESSION",
        "====================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase verifies the Phase 16U.11 safe medium-risk solver patch.",
        "No production files are modified.",
        "No solver equations are modified.",
        "",
        "SUMMARY",
        "-------",
        f"Missing required wrapper tokens: {result['missing_required_count']}",
        f"Forbidden patched legacy tokens present: {result['forbidden_present_count']}",
        f"Manual-review tokens missing: {result['manual_review_missing_count']}",
        "",
        "CHECKS",
        "------",
    ]

    for check in checks:
        lines.append(f"{check['name']}: {'PASS' if check['passed'] else 'FAIL'} — {check['detail']}")

    if missing_required:
        lines.extend(["", "MISSING REQUIRED TOKENS", "-----------------------"])
        lines.extend(missing_required)

    if forbidden_present:
        lines.extend(["", "FORBIDDEN TOKENS PRESENT", "------------------------"])
        lines.extend(forbidden_present)

    if manual_review_missing:
        lines.extend(["", "MANUAL REVIEW TOKENS MISSING", "----------------------------"])
        lines.extend(manual_review_missing)

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.12 COMPLETE." if passed else "PHASE 16U.12 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.13 — ENGINE SOLVER REMAINING STATUS CONSUMER REVIEW",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_regression()
    print(result["status"])
    print(f"missing_required_count={result['missing_required_count']}")
    print(f"forbidden_present_count={result['forbidden_present_count']}")
    print(f"manual_review_missing_count={result['manual_review_missing_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u12_engine_solver_medium_risk_status_wrapper_regression_complete"]:
        raise SystemExit(1)
