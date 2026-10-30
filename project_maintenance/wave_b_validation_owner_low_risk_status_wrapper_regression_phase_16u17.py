from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path


PHASE = "16U.17"
PASS_BANNER = "PASS_PHASE_16U17_WAVE_B_VALIDATION_OWNER_LOW_RISK_STATUS_WRAPPER_REGRESSION"

PATCH_JSON = Path("project_maintenance/wave_b_validation_owner_low_risk_status_wrapper_patch_phase_16u16.json")
AUDIT_JSON = Path("project_maintenance/wave_b_validation_owner_status_consumer_audit_phase_16u15.json")

OUT_JSON = Path("project_maintenance/wave_b_validation_owner_low_risk_status_wrapper_regression_phase_16u17.json")
OUT_TXT = Path("project_maintenance/WAVE_B_VALIDATION_OWNER_LOW_RISK_STATUS_WRAPPER_REGRESSION_PHASE_16U17.txt")

FILES = [
    Path("leaf_qt/regen_candidate_validator.py"),
    Path("leaf_qt/regen_source_validation_gate.py"),
    Path("leaf_qt/regen_candidate_blueprint_mutation_validation.py"),
    Path("leaf_qt/regen_candidate_blueprint_population_validation_owner.py"),
    Path("leaf_qt/regen_candidate_post_resolve_validation_owner.py"),
    Path("leaf_qt/regen_geometry_constraint_validation_owner.py"),
]

REQUIRED_TOKENS = {
    "leaf_qt/regen_candidate_validator.py": [
        "from leaf_qt.structured_status_access import highest_severity as solver_highest_severity, is_pass",
        'if solver_highest_severity(severities) == "FAIL":',
    ],
    "leaf_qt/regen_source_validation_gate.py": [
        "from leaf_qt.structured_status_access import highest_severity as solver_highest_severity, is_pass",
        "if key in results and is_pass(results.get(key)):",
        'if solver_highest_severity(severities) == "FAIL":',
    ],
}

FORBIDDEN_TOKENS = {
    "leaf_qt/regen_candidate_validator.py": [
        'if "FAIL" in severities:',
    ],
    "leaf_qt/regen_source_validation_gate.py": [
        'if key in results and str(results.get(key)).upper().startswith("PASS"):',
        'if "FAIL" in severities:',
    ],
}

HELD_TOKENS = {
    "leaf_qt/regen_candidate_blueprint_mutation_validation.py": [
        'marker = "PASS" if check["passed"] else "FAIL"',
    ],
    "leaf_qt/regen_candidate_blueprint_population_validation_owner.py": [
        'marker = "PASS" if check["passed"] else "FAIL"',
    ],
    "leaf_qt/regen_candidate_post_resolve_validation_owner.py": [
        '("FAIL" not in text and "INVALID" not in text),',
        '("WARN" not in text and "REVIEW" not in text and "PLACEHOLDER" not in text),',
    ],
    "leaf_qt/regen_geometry_constraint_validation_owner.py": [
        'passed=("FAIL" not in text and "INVALID" not in text),',
        'passed=("WARN" not in text and "REVIEW" not in text and "PLACEHOLDER" not in text),',
    ],
}


def compile_file(path: Path) -> dict:
    try:
        py_compile.compile(str(path), doraise=True)
        return {"file": str(path), "passed": True, "error": ""}
    except Exception as exc:
        return {"file": str(path), "passed": False, "error": repr(exc)}


def run_regression() -> dict:
    if not PATCH_JSON.exists():
        raise FileNotFoundError(f"Missing {PATCH_JSON}. Run Phase 16U.16 first.")
    if not AUDIT_JSON.exists():
        raise FileNotFoundError(f"Missing {AUDIT_JSON}. Run Phase 16U.15 first.")

    patch = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))

    missing_required = []
    forbidden_present = []
    held_missing = []

    for file_name, tokens in REQUIRED_TOKENS.items():
        text = Path(file_name).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                missing_required.append({"file": file_name, "token": token})

    for file_name, tokens in FORBIDDEN_TOKENS.items():
        text = Path(file_name).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token in text:
                forbidden_present.append({"file": file_name, "token": token})

    for file_name, tokens in HELD_TOKENS.items():
        text = Path(file_name).read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                held_missing.append({"file": file_name, "token": token})

    compile_results = [compile_file(path) for path in FILES]

    checks = [
        {
            "name": "phase_16u15_audit_passed",
            "passed": audit.get("status") == "PASS_PHASE_16U15_WAVE_B_VALIDATION_OWNER_STATUS_CONSUMER_AUDIT",
            "detail": str(audit.get("status")),
        },
        {
            "name": "phase_16u16_patch_passed",
            "passed": patch.get("status") == "PASS_PHASE_16U16_WAVE_B_VALIDATION_OWNER_LOW_RISK_STATUS_WRAPPER_PATCH",
            "detail": str(patch.get("status")),
        },
        {
            "name": "required_wrapper_tokens_present",
            "passed": not missing_required,
            "detail": f"{len(missing_required)} missing",
        },
        {
            "name": "patched_legacy_tokens_absent",
            "passed": not forbidden_present,
            "detail": f"{len(forbidden_present)} present",
        },
        {
            "name": "held_manual_review_tokens_preserved",
            "passed": not held_missing,
            "detail": f"{len(held_missing)} missing",
        },
        {
            "name": "all_validation_files_compile",
            "passed": all(item["passed"] for item in compile_results),
            "detail": f"{sum(1 for item in compile_results if item['passed'])}/{len(compile_results)} compiled",
        },
    ]

    passed = all(check["passed"] for check in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U17_WAVE_B_VALIDATION_OWNER_LOW_RISK_STATUS_WRAPPER_REGRESSION",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "missing_required_count": len(missing_required),
        "forbidden_present_count": len(forbidden_present),
        "held_missing_count": len(held_missing),
        "missing_required": missing_required,
        "forbidden_present": forbidden_present,
        "held_missing": held_missing,
        "compile_results": compile_results,
        "checks": checks,
        "phase_16u17_wave_b_validation_owner_low_risk_status_wrapper_regression_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.17",
        "WAVE B VALIDATION OWNER LOW-RISK STATUS WRAPPER REGRESSION",
        "===========================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "SUMMARY",
        "-------",
        f"Missing required wrapper tokens: {result['missing_required_count']}",
        f"Forbidden patched legacy tokens present: {result['forbidden_present_count']}",
        f"Held/manual-review tokens missing: {result['held_missing_count']}",
        "",
        "CHECKS",
        "------",
    ]

    for check in checks:
        lines.append(f"{check['name']}: {'PASS' if check['passed'] else 'FAIL'} — {check['detail']}")

    lines.extend(["", "COMPILE RESULTS", "---------------"])
    for item in compile_results:
        lines.append(f"{item['file']}: {'PASS' if item['passed'] else 'FAIL'} {item['error']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.17 COMPLETE." if passed else "PHASE 16U.17 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.18 — WAVE B VALIDATION OWNER REMAINING CONSUMER REVIEW",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_regression()
    print(result["status"])
    print(f"missing_required_count={result['missing_required_count']}")
    print(f"forbidden_present_count={result['forbidden_present_count']}")
    print(f"held_missing_count={result['held_missing_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u17_wave_b_validation_owner_low_risk_status_wrapper_regression_complete"]:
        raise SystemExit(1)
