from __future__ import annotations

import importlib
import json
import py_compile
import re
import sys
from datetime import datetime
from pathlib import Path


PHASE = "16U.39"
PASS_BANNER = "PASS_PHASE_16U39_REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_REGRESSION"
FAIL_BANNER = "FAIL_PHASE_16U39_REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_REGRESSION"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TARGET = ROOT / "leaf_qt" / "regen_cross_section_viewer.py"
UPLOAD_COPY = ROOT / "LEAF_UPLOAD" / "leaf_qt" / "regen_cross_section_viewer.py"
PATCH_JSON = ROOT / "project_maintenance" / "regen_cross_section_viewer_presentation_layer_patch_phase_16u38.json"

OUT_TXT = ROOT / "project_maintenance" / "REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_REGRESSION_PHASE_16U39.txt"
OUT_JSON = ROOT / "project_maintenance" / "regen_cross_section_viewer_presentation_layer_regression_phase_16u39.json"

REQUIRED_TOKENS = [
    "from leaf_qt.status_presentation import",
    "LegacyCompatibilityProducer",
    "status_severity",
    "_leaf_16u38_status_severity",
    "_leaf_16u38_marker_from_bool",
    "_leaf_16u38_is_fail_like",
    "_leaf_16u38_is_pass_like",
    "_leaf_16u38_is_warn_like",
    "_leaf_16u38_is_blocked_like",
]

FORBIDDEN_REINTRODUCTION_PATTERNS = [
    r'status_text\s*=\s*["\']PASS["\']\s+if\s+.+?\s+else\s+["\']FAIL["\']',
    r'status_text\s*=\s*["\']FAIL["\']\s+if\s+.+?\s+else\s+["\']PASS["\']',
    r'if\s+"FAIL"\s+in\s+status\s+or\s+"FAIL"\s+in\s+geometry\s+or\s+"FAIL"\s+in\s+thermal\s+or\s+"FAIL"\s+in\s+coolant',
    r'status\.startswith\(\s*["\']BLOCKED["\']\s*\)\s+or\s+status\.startswith\(\s*["\']FAIL["\']\s*\)',
    r'not\s+recommended_status\.upper\(\)\.startswith\(\(["\']BLOCKED["\'],\s*["\']FAIL["\']\)\)',
    r'not\s+best_status\.upper\(\)\.startswith\(\(["\']FAIL["\'],\s*["\']BLOCKED["\']\)\)',
]


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {
        "name": name,
        "passed": bool(passed),
        "detail": detail,
    }


def compile_file(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return True, ""
    except Exception as exc:
        return False, repr(exc)


def main() -> dict:
    checks = []

    checks.append(check("production_target_exists", TARGET.exists(), str(TARGET.relative_to(ROOT))))
    checks.append(check("upload_duplicate_exists_but_not_targeted", UPLOAD_COPY.exists(), str(UPLOAD_COPY.relative_to(ROOT)) if UPLOAD_COPY.exists() else "not present"))
    checks.append(check("phase_16u38_patch_json_exists", PATCH_JSON.exists(), str(PATCH_JSON.relative_to(ROOT))))

    if not TARGET.exists():
        result = {
            "phase": PHASE,
            "status": FAIL_BANNER,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "checks": checks,
            "phase_16u39_regen_cross_section_viewer_presentation_layer_regression_complete": False,
        }
        OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
        OUT_TXT.write_text("PHASE 16U.39 FAILED: target missing.\n", encoding="utf-8")
        print(result["status"])
        return result

    text = TARGET.read_text(encoding="utf-8", errors="replace")

    compiled, compile_error = compile_file(TARGET)
    checks.append(check("production_target_compiles", compiled, compile_error or "compile pass"))

    missing_tokens = [token for token in REQUIRED_TOKENS if token not in text]
    checks.append(
        check(
            "shared_presentation_tokens_present",
            not missing_tokens,
            "missing=" + ", ".join(missing_tokens) if missing_tokens else "all tokens present",
        )
    )

    forbidden_hits = []
    for pattern in FORBIDDEN_REINTRODUCTION_PATTERNS:
        if re.search(pattern, text):
            forbidden_hits.append(pattern)

    checks.append(
        check(
            "legacy_patterns_not_reintroduced",
            not forbidden_hits,
            f"{len(forbidden_hits)} forbidden pattern(s)",
        )
    )

    patch_payload = {}
    if PATCH_JSON.exists():
        try:
            patch_payload = json.loads(PATCH_JSON.read_text(encoding="utf-8"))
        except Exception as exc:
            patch_payload = {"json_error": repr(exc)}

    checks.append(
        check(
            "phase_16u38_patch_completed",
            patch_payload.get("phase_16u38_regen_cross_section_viewer_presentation_layer_patch_complete") is True,
            str(patch_payload.get("status")),
        )
    )

    try:
        status_module = importlib.import_module("leaf_qt.status_presentation")
        marker_true = status_module.LegacyCompatibilityProducer.marker_from_bool(True)
        marker_false = status_module.LegacyCompatibilityProducer.marker_from_bool(False)
        helper_api_pass = marker_true == "PASS" and marker_false == "FAIL"
        helper_api_detail = f"True->{marker_true}, False->{marker_false}"
    except Exception as exc:
        helper_api_pass = False
        helper_api_detail = repr(exc)

    checks.append(check("shared_status_compatibility_api_behaves", helper_api_pass, helper_api_detail))

    try:
        viewer_module = importlib.import_module("leaf_qt.regen_cross_section_viewer")
        viewer_import_pass = True
        viewer_import_detail = "module import pass"
    except Exception as exc:
        viewer_import_pass = False
        viewer_import_detail = repr(exc)

    checks.append(check("production_viewer_imports", viewer_import_pass, viewer_import_detail))

    helper_behaviour_pass = False
    helper_behaviour_detail = ""

    if viewer_import_pass:
        try:
            cases = [
                ("PASS", "PASS"),
                ("VALID", "PASS"),
                ("WARN", "WARN"),
                ("PARTIAL_SOURCE_MODE", "WARN"),
                ("MISSING_DATA", "FAIL"),
                ("FAIL", "FAIL"),
                ("BLOCKED_BY_GEOMETRY", "FAIL"),
                ("INVALID", "FAIL"),
                ("UNKNOWN", "UNKNOWN"),
            ]
            failures = []
            for raw, expected in cases:
                actual = viewer_module._leaf_16u38_status_severity(raw)
                if actual != expected:
                    failures.append((raw, expected, actual))

            bool_marker_pass = (
                viewer_module._leaf_16u38_marker_from_bool(True) == "PASS"
                and viewer_module._leaf_16u38_marker_from_bool(False) == "FAIL"
                and viewer_module._leaf_16u38_marker_from_bool(False, false_marker="MISSING") == "MISSING"
            )

            helper_behaviour_pass = not failures and bool_marker_pass
            helper_behaviour_detail = f"severity_failures={failures}; marker_pass={bool_marker_pass}"
        except Exception as exc:
            helper_behaviour_pass = False
            helper_behaviour_detail = repr(exc)

    checks.append(check("viewer_helper_behaviour_regression", helper_behaviour_pass, helper_behaviour_detail))

    if UPLOAD_COPY.exists():
        upload_text = UPLOAD_COPY.read_text(encoding="utf-8", errors="replace")
        upload_untouched_by_16u38 = "_leaf_16u38_status_severity" not in upload_text
        checks.append(
            check(
                "leaf_upload_duplicate_not_patched",
                upload_untouched_by_16u38,
                "duplicate contains 16u38 helpers" if not upload_untouched_by_16u38 else "duplicate untouched",
            )
        )

    passed = all(item["passed"] for item in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target": str(TARGET.relative_to(ROOT)),
        "checks": checks,
        "missing_tokens": missing_tokens,
        "forbidden_hits": forbidden_hits,
        "phase_16u39_regen_cross_section_viewer_presentation_layer_regression_complete": passed,
        "next_phase": "16U.40 — First Report Owner Presentation Layer Rollout Closure Gate",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.39",
        "REGEN CROSS SECTION VIEWER PRESENTATION LAYER REGRESSION",
        "========================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Regression verification for the first wider report-owner/UI presentation-layer rollout patch.",
        "",
        "TARGET",
        "------",
        result["target"],
        "",
        "CHECKS",
        "------",
    ]

    for item in checks:
        lines.append(f"{item['name']}: {'PASS' if item['passed'] else 'FAIL'} — {item['detail']}")

    lines.extend(
        [
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.39 COMPLETE." if passed else "PHASE 16U.39 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.40 — FIRST REPORT OWNER PRESENTATION LAYER ROLLOUT CLOSURE GATE",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    for item in result["checks"]:
        print(f"{item['name']}={'PASS' if item['passed'] else 'FAIL'}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u39_regen_cross_section_viewer_presentation_layer_regression_complete"]:
        raise SystemExit(1)
