from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path


PHASE = "16U.11"
PASS_BANNER = "PASS_PHASE_16U11_ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_PATCH"

AUDIT_JSON = Path("project_maintenance/engine_solver_medium_risk_status_consumer_audit_phase_16u10.json")
OUT_JSON = Path("project_maintenance/engine_solver_medium_risk_status_wrapper_patch_phase_16u11.json")
OUT_TXT = Path("project_maintenance/ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_PATCH_PHASE_16U11.txt")

ENGINE = Path("leaf_qt/engine_solver.py")


REPLACEMENTS = [
    (
        'if status not in ("REQUIRED", "PASS"):',
        'if status != "REQUIRED" and not solver_pass(status):',
    ),
    (
        'if "FAIL" in statuses:',
        'if solver_highest_severity(statuses) == "FAIL":',
    ),
    (
        'elif "WARN" in statuses:',
        'elif solver_highest_severity(statuses) == "WARN":',
    ),
]


def ensure_import(text: str) -> tuple[str, bool]:
    old = "from leaf_qt.solver_status_access import solver_fail, solver_pass"
    new = "from leaf_qt.solver_status_access import solver_fail, solver_highest_severity, solver_pass"

    if new in text:
        return text, False

    if old in text:
        return text.replace(old, new, 1), True

    lines = text.splitlines(keepends=True)
    insert_at = 0
    for idx, line in enumerate(lines):
        if line.startswith("from __future__ import"):
            insert_at = idx + 1

    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1

    lines.insert(insert_at, new + "\n")
    return "".join(lines), True


def compile_engine() -> dict:
    try:
        py_compile.compile(str(ENGINE), doraise=True)
        return {"file": str(ENGINE), "passed": True, "error": ""}
    except Exception as exc:
        return {"file": str(ENGINE), "passed": False, "error": repr(exc)}


def run_patch() -> dict:
    if not AUDIT_JSON.exists():
        raise FileNotFoundError(f"Missing {AUDIT_JSON}. Run Phase 16U.10 first.")

    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    text_original = ENGINE.read_text(encoding="utf-8", errors="replace")
    text, import_changed = ensure_import(text_original)

    applied = []
    already_applied = []
    missing = []

    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new, 1)
            applied.append({"old": old, "new": new})
        elif new in text:
            already_applied.append({"old": old, "new": new})
        else:
            missing.append({"old": old, "new": new})

    changed = text != text_original
    if changed:
        backup = ENGINE.with_suffix(ENGINE.suffix + ".phase_16u11_backup")
        if not backup.exists():
            backup.write_text(text_original, encoding="utf-8")
        ENGINE.write_text(text, encoding="utf-8")

    compile_result = compile_engine()
    final_text = ENGINE.read_text(encoding="utf-8", errors="replace")

    manual_review_tokens_still_present = [
        'elif source_data_weighted_gate in ("PARTIAL", "FAIL"):',
        'if item["status"] in ("MISSING", "PLACEHOLDER", "FAIL")',
        'verdict.endswith("PASS")',
        'if "FAIL" in text or "INVALID" in text:',
        'elif "WARN" in text or "REVIEW" in text:',
    ]

    manual_review_preserved = all(token in final_text for token in manual_review_tokens_still_present)

    passed = (
        audit.get("status") == "PASS_PHASE_16U10_ENGINE_SOLVER_MEDIUM_RISK_STATUS_CONSUMER_AUDIT"
        and audit.get("patchable_next_phase_count") == 5
        and len(applied) + len(already_applied) == len(REPLACEMENTS)
        and not missing
        and "solver_highest_severity" in final_text
        and compile_result["passed"]
        and manual_review_preserved
    )

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U11_ENGINE_SOLVER_MEDIUM_RISK_STATUS_WRAPPER_PATCH",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "audit_status": audit.get("status"),
        "import_changed": import_changed,
        "applied_count": len(applied),
        "already_applied_count": len(already_applied),
        "missing_count": len(missing),
        "applied": applied,
        "already_applied": already_applied,
        "missing": missing,
        "compile_result": compile_result,
        "manual_review_preserved": manual_review_preserved,
        "phase_16u11_engine_solver_medium_risk_status_wrapper_patch_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.11",
        "ENGINE SOLVER MEDIUM-RISK STATUS WRAPPER PATCH",
        "================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase patches only safe medium-risk Wave A solver status consumers.",
        "Manual-review medium-risk items are intentionally preserved.",
        "No solver equations are changed.",
        "No numerical calculations are changed.",
        "",
        "FILES MODIFIED",
        "--------------",
        "leaf_qt/engine_solver.py",
        "",
        "SUMMARY",
        "-------",
        f"Import changed: {import_changed}",
        f"Applied: {len(applied)}",
        f"Already applied: {len(already_applied)}",
        f"Missing: {len(missing)}",
        f"Compile: {'PASS' if compile_result['passed'] else 'FAIL'} {compile_result['error']}",
        f"Manual-review items preserved: {manual_review_preserved}",
        "",
        "PATCHES",
        "-------",
    ]

    for item in applied:
        lines.append(f"OLD: {item['old']}")
        lines.append(f"NEW: {item['new']}")
        lines.append("")

    lines.extend(
        [
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.11 COMPLETE." if passed else "PHASE 16U.11 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.12 — ENGINE SOLVER MEDIUM-RISK STATUS WRAPPER REGRESSION",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_patch()
    print(result["status"])
    print(f"applied_count={result['applied_count']}")
    print(f"already_applied_count={result['already_applied_count']}")
    print(f"missing_count={result['missing_count']}")
    print(f"manual_review_preserved={result['manual_review_preserved']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u11_engine_solver_medium_risk_status_wrapper_patch_complete"]:
        raise SystemExit(1)
