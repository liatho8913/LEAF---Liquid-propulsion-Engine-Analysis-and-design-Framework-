from __future__ import annotations

import json
import py_compile
from datetime import datetime
from pathlib import Path


PHASE = "16U.16"
PASS_BANNER = "PASS_PHASE_16U16_WAVE_B_VALIDATION_OWNER_LOW_RISK_STATUS_WRAPPER_PATCH"

AUDIT_JSON = Path("project_maintenance/wave_b_validation_owner_status_consumer_audit_phase_16u15.json")
OUT_JSON = Path("project_maintenance/wave_b_validation_owner_low_risk_status_wrapper_patch_phase_16u16.json")
OUT_TXT = Path("project_maintenance/WAVE_B_VALIDATION_OWNER_LOW_RISK_STATUS_WRAPPER_PATCH_PHASE_16U16.txt")

CANDIDATE_VALIDATOR = Path("leaf_qt/regen_candidate_validator.py")
SOURCE_VALIDATION_GATE = Path("leaf_qt/regen_source_validation_gate.py")

IMPORT_LINE = "from leaf_qt.structured_status_access import highest_severity as solver_highest_severity, is_pass\n"


REPLACEMENTS = {
    CANDIDATE_VALIDATOR: [
        (
            'if "FAIL" in severities:',
            'if solver_highest_severity(severities) == "FAIL":',
        ),
    ],
    SOURCE_VALIDATION_GATE: [
        (
            'if key in results and str(results.get(key)).upper().startswith("PASS"):',
            'if key in results and is_pass(results.get(key)):',
        ),
        (
            'if "FAIL" in severities:',
            'if solver_highest_severity(severities) == "FAIL":',
        ),
    ],
}


HELD_TOKENS = {
    Path("leaf_qt/regen_candidate_blueprint_mutation_validation.py"): [
        'marker = "PASS" if check["passed"] else "FAIL"',
    ],
    Path("leaf_qt/regen_candidate_blueprint_population_validation_owner.py"): [
        'marker = "PASS" if check["passed"] else "FAIL"',
    ],
    Path("leaf_qt/regen_candidate_post_resolve_validation_owner.py"): [
        '("FAIL" not in text and "INVALID" not in text),',
        '("WARN" not in text and "REVIEW" not in text and "PLACEHOLDER" not in text),',
    ],
    Path("leaf_qt/regen_geometry_constraint_validation_owner.py"): [
        'passed=("FAIL" not in text and "INVALID" not in text),',
        'passed=("WARN" not in text and "REVIEW" not in text and "PLACEHOLDER" not in text),',
    ],
}


def ensure_import(path: Path, text: str) -> tuple[str, bool]:
    if IMPORT_LINE.strip() in text:
        return text, False

    lines = text.splitlines(keepends=True)

    insert_at = 0
    if lines and lines[0].startswith("#!"):
        insert_at = 1

    for idx, line in enumerate(lines):
        if line.startswith("from __future__ import"):
            insert_at = idx + 1

    while insert_at < len(lines) and lines[insert_at].strip() == "":
        insert_at += 1

    lines.insert(insert_at, IMPORT_LINE)
    return "".join(lines), True


def apply_file_patch(path: Path, replacements: list[tuple[str, str]]) -> dict:
    original = path.read_text(encoding="utf-8", errors="replace")
    text, import_added = ensure_import(path, original)

    applied = []
    already_applied = []
    missing = []

    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            applied.append({"old": old, "new": new})
        elif new in text:
            already_applied.append({"old": old, "new": new})
        else:
            missing.append({"old": old, "new": new})

    changed = text != original

    if changed:
        backup = path.with_suffix(path.suffix + ".phase_16u16_backup")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
        path.write_text(text, encoding="utf-8")

    return {
        "file": str(path),
        "import_added": import_added,
        "applied_count": len(applied),
        "already_applied_count": len(already_applied),
        "missing_count": len(missing),
        "applied": applied,
        "already_applied": already_applied,
        "missing": missing,
        "changed": changed,
    }


def compile_file(path: Path) -> dict:
    try:
        py_compile.compile(str(path), doraise=True)
        return {"file": str(path), "passed": True, "error": ""}
    except Exception as exc:
        return {"file": str(path), "passed": False, "error": repr(exc)}


def held_tokens_preserved() -> dict:
    missing = []

    for path, tokens in HELD_TOKENS.items():
        if not path.exists():
            missing.append({"file": str(path), "token": "__FILE_MISSING__"})
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            if token not in text:
                missing.append({"file": str(path), "token": token})

    return {
        "passed": not missing,
        "missing": missing,
    }


def run_patch() -> dict:
    if not AUDIT_JSON.exists():
        raise FileNotFoundError(f"Missing {AUDIT_JSON}. Run Phase 16U.15 first.")

    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))

    patch_results = [
        apply_file_patch(path, replacements)
        for path, replacements in REPLACEMENTS.items()
    ]

    compile_targets = sorted(set(REPLACEMENTS.keys()) | set(HELD_TOKENS.keys()), key=str)
    compile_results = [compile_file(path) for path in compile_targets if path.exists()]

    held_result = held_tokens_preserved()

    total_applied = sum(item["applied_count"] for item in patch_results)
    total_already = sum(item["already_applied_count"] for item in patch_results)
    total_missing = sum(item["missing_count"] for item in patch_results)

    final_candidate_text = CANDIDATE_VALIDATOR.read_text(encoding="utf-8", errors="replace")
    final_source_gate_text = SOURCE_VALIDATION_GATE.read_text(encoding="utf-8", errors="replace")

    required_tokens = [
        'if solver_highest_severity(severities) == "FAIL":',
        'if key in results and is_pass(results.get(key)):',
        IMPORT_LINE.strip(),
    ]

    required_present = (
        all(token in final_candidate_text or token in final_source_gate_text for token in required_tokens)
    )

    forbidden_tokens = [
        'if key in results and str(results.get(key)).upper().startswith("PASS"):',
    ]

    forbidden_present = [
        token for token in forbidden_tokens
        if token in final_candidate_text or token in final_source_gate_text
    ]

    passed = (
        audit.get("status") == "PASS_PHASE_16U15_WAVE_B_VALIDATION_OWNER_STATUS_CONSUMER_AUDIT"
        and audit.get("patchable_next_phase_count") == 7
        and total_missing == 0
        and total_applied + total_already == 3
        and required_present
        and not forbidden_present
        and held_result["passed"]
        and all(item["passed"] for item in compile_results)
    )

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else "FAIL_PHASE_16U16_WAVE_B_VALIDATION_OWNER_LOW_RISK_STATUS_WRAPPER_PATCH",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "audit_status": audit.get("status"),
        "audit_patchable_next_phase_count": audit.get("patchable_next_phase_count"),
        "deduplicated_patch_count": 3,
        "total_applied_count": total_applied,
        "total_already_applied_count": total_already,
        "total_missing_count": total_missing,
        "patch_results": patch_results,
        "held_tokens_preserved": held_result,
        "forbidden_tokens_present": forbidden_present,
        "compile_results": compile_results,
        "phase_16u16_wave_b_validation_owner_low_risk_status_wrapper_patch_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.16",
        "WAVE B VALIDATION OWNER LOW-RISK STATUS WRAPPER PATCH",
        "======================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "SCOPE",
        "-----",
        "This phase patches only deduplicated low-risk Wave B validation-owner consumers.",
        "Held/manual-review validation items are intentionally preserved.",
        "No solver equations are changed.",
        "No validation equations are changed.",
        "",
        "FILES MODIFIED",
        "--------------",
        "leaf_qt/regen_candidate_validator.py",
        "leaf_qt/regen_source_validation_gate.py",
        "",
        "SUMMARY",
        "-------",
        f"Audit patchable rows: {audit.get('patchable_next_phase_count')}",
        "Deduplicated patch items: 3",
        f"Applied: {total_applied}",
        f"Already applied: {total_already}",
        f"Missing: {total_missing}",
        f"Held/manual-review tokens preserved: {held_result['passed']}",
        f"Forbidden tokens present: {len(forbidden_present)}",
        "",
        "PATCH RESULTS",
        "-------------",
    ]

    for patch_result in patch_results:
        lines.append(f"{patch_result['file']}")
        lines.append(f"  import_added: {patch_result['import_added']}")
        lines.append(f"  applied: {patch_result['applied_count']}")
        lines.append(f"  already_applied: {patch_result['already_applied_count']}")
        lines.append(f"  missing: {patch_result['missing_count']}")
        for item in patch_result["applied"]:
            lines.append(f"  OLD: {item['old']}")
            lines.append(f"  NEW: {item['new']}")
        lines.append("")

    lines.extend(["COMPILE RESULTS", "---------------"])
    for item in compile_results:
        lines.append(f"{item['file']}: {'PASS' if item['passed'] else 'FAIL'} {item['error']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.16 COMPLETE." if passed else "PHASE 16U.16 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.17 — WAVE B VALIDATION OWNER LOW-RISK STATUS WRAPPER REGRESSION",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_patch()
    print(result["status"])
    print(f"total_applied_count={result['total_applied_count']}")
    print(f"total_already_applied_count={result['total_already_applied_count']}")
    print(f"total_missing_count={result['total_missing_count']}")
    print(f"held_tokens_preserved={result['held_tokens_preserved']['passed']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
    if not result["phase_16u16_wave_b_validation_owner_low_risk_status_wrapper_patch_complete"]:
        raise SystemExit(1)
