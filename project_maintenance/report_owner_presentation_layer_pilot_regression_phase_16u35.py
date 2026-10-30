from __future__ import annotations

import importlib
import json
import py_compile
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PHASE = "16U.35"
PASS_BANNER = "PASS_PHASE_16U35_REPORT_OWNER_PRESENTATION_LAYER_PILOT_REGRESSION"
FAIL_BANNER = "FAIL_PHASE_16U35_REPORT_OWNER_PRESENTATION_LAYER_PILOT_REGRESSION"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STATUS_SOURCE = ROOT / "leaf_qt" / "status_presentation.py"
PILOT_SOURCE = ROOT / "leaf_qt" / "foundation_test_runner_window.py"
STATUS_TEST = ROOT / "project_maintenance" / "test_status_presentation_phase_16u32.py"

OUT_JSON = ROOT / "project_maintenance" / "report_owner_presentation_layer_pilot_regression_phase_16u35.json"
OUT_TXT = ROOT / "project_maintenance" / "REPORT_OWNER_PRESENTATION_LAYER_PILOT_REGRESSION_PHASE_16U35.txt"

REQUIRED_STATUS_API = [
    "StatusPresentation",
    "StructuredStatusRenderer",
    "StatusVisualStyle",
    "ReportStatusPresenter",
    "ReportFilterModel",
    "LegacyCompatibilityProducer",
    "present_status",
    "present_finding",
    "display_status",
    "status_severity",
    "status_colour_role",
    "status_icon",
    "status_badge",
    "should_show_for_filter",
    "report_state_filter_options",
]

REQUIRED_PILOT_TOKENS = [
    "from leaf_qt.status_presentation import LegacyCompatibilityProducer",
    "LegacyCompatibilityProducer.marker_from_bool(passed)",
]

FORBIDDEN_PILOT_PATTERNS = [
    r'status_text\s*=\s*["\']PASS["\']\s+if\s+passed\s+else\s+["\']FAIL["\']',
    r'status_text\s*=\s*["\']FAIL["\']\s+if\s+not\s+passed\s+else\s+["\']PASS["\']',
]


def compile_file(path: Path) -> dict:
    try:
        py_compile.compile(str(path), doraise=True)
        return {"file": str(path.relative_to(ROOT)), "passed": True, "error": ""}
    except Exception as exc:
        return {"file": str(path.relative_to(ROOT)), "passed": False, "error": repr(exc)}


def bool_check(name: str, passed: bool, detail: str = "") -> dict:
    return {
        "name": name,
        "passed": bool(passed),
        "detail": detail,
    }


def run_optional_status_test() -> dict:
    if not STATUS_TEST.exists():
        return {
            "exists": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "passed": True,
            "detail": "Optional status presentation unit test not present in this checkout.",
        }

    result = subprocess.run(
        [sys.executable, str(STATUS_TEST.relative_to(ROOT))],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    return {
        "exists": True,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "passed": result.returncode == 0,
        "detail": f"returncode={result.returncode}",
    }


def run_regression() -> dict:
    checks: list[dict] = []

    checks.append(bool_check("status_presentation_file_exists", STATUS_SOURCE.exists(), str(STATUS_SOURCE.relative_to(ROOT))))
    checks.append(bool_check("pilot_window_file_exists", PILOT_SOURCE.exists(), str(PILOT_SOURCE.relative_to(ROOT))))

    if not STATUS_SOURCE.exists() or not PILOT_SOURCE.exists():
        passed = False
        result = {
            "phase": PHASE,
            "status": FAIL_BANNER,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "checks": checks,
            "phase_16u35_report_owner_presentation_layer_pilot_regression_complete": False,
        }
        OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
        OUT_TXT.write_text("PHASE 16U.35 FAILED: required source files missing.\n", encoding="utf-8")
        return result

    status_text = STATUS_SOURCE.read_text(encoding="utf-8", errors="replace")
    pilot_text = PILOT_SOURCE.read_text(encoding="utf-8", errors="replace")

    compile_results = [
        compile_file(STATUS_SOURCE),
        compile_file(PILOT_SOURCE),
    ]
    if STATUS_TEST.exists():
        compile_results.append(compile_file(STATUS_TEST))

    checks.append(
        bool_check(
            "compile_passed",
            all(item["passed"] for item in compile_results),
            f"{sum(1 for item in compile_results if item['passed'])}/{len(compile_results)} compiled",
        )
    )

    module = importlib.import_module("leaf_qt.status_presentation")

    missing_api = [name for name in REQUIRED_STATUS_API if not hasattr(module, name)]
    checks.append(
        bool_check(
            "required_status_api_present",
            not missing_api,
            "missing=" + ", ".join(missing_api) if missing_api else "all required API present",
        )
    )

    compatibility = getattr(module, "LegacyCompatibilityProducer", None)
    marker_true = None
    marker_false = None

    try:
        marker_true = compatibility.marker_from_bool(True)
        marker_false = compatibility.marker_from_bool(False)
        compatibility_passed = marker_true == "PASS" and marker_false == "FAIL"
    except Exception as exc:
        compatibility_passed = False
        marker_true = repr(exc)
        marker_false = repr(exc)

    checks.append(
        bool_check(
            "legacy_compatibility_marker_behaviour",
            compatibility_passed,
            f"True->{marker_true}, False->{marker_false}",
        )
    )

    missing_pilot_tokens = [token for token in REQUIRED_PILOT_TOKENS if token not in pilot_text]
    checks.append(
        bool_check(
            "pilot_uses_shared_presentation_layer",
            not missing_pilot_tokens,
            "missing=" + ", ".join(missing_pilot_tokens) if missing_pilot_tokens else "pilot tokens present",
        )
    )

    forbidden_matches = []
    for pattern in FORBIDDEN_PILOT_PATTERNS:
        if re.search(pattern, pilot_text):
            forbidden_matches.append(pattern)

    checks.append(
        bool_check(
            "legacy_inline_marker_removed_from_pilot",
            not forbidden_matches,
            f"{len(forbidden_matches)} forbidden pattern(s) present",
        )
    )

    status_test = run_optional_status_test()
    checks.append(
        bool_check(
            "status_presentation_unit_tests",
            status_test["passed"],
            status_test["detail"],
        )
    )

    presentation_cases = [
        ("PASS", "PASS"),
        ("PASSED", "PASS"),
        ("VALID", "PASS"),
        ("PASS_WITH_WARNINGS", "WARN"),
        ("WARN", "WARN"),
        ("PARTIAL", "WARN"),
        ("FAIL", "FAIL"),
        ("FAILED", "FAIL"),
        ("BLOCKED", "FAIL"),
        (None, "UNKNOWN"),
    ]

    presentation_failures = []
    for raw, expected in presentation_cases:
        actual = module.present_status(raw).severity
        if actual != expected:
            presentation_failures.append(
                {
                    "raw": repr(raw),
                    "expected": expected,
                    "actual": actual,
                }
            )

    checks.append(
        bool_check(
            "presentation_semantics_regression",
            not presentation_failures,
            f"{len(presentation_failures)} semantic regression(s)",
        )
    )

    passed = all(check["passed"] for check in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if passed else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target_files": [
            str(STATUS_SOURCE.relative_to(ROOT)),
            str(PILOT_SOURCE.relative_to(ROOT)),
        ],
        "missing_api": missing_api,
        "missing_pilot_tokens": missing_pilot_tokens,
        "forbidden_matches": forbidden_matches,
        "compile_results": compile_results,
        "status_test": status_test,
        "presentation_failures": presentation_failures,
        "checks": checks,
        "phase_16u35_report_owner_presentation_layer_pilot_regression_complete": passed,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.35",
        "REPORT OWNER PRESENTATION LAYER PILOT REGRESSION",
        "=================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Regression verification for the first production report-owner presentation-layer pilot.",
        "",
        "FILES VERIFIED",
        "--------------",
        str(STATUS_SOURCE.relative_to(ROOT)),
        str(PILOT_SOURCE.relative_to(ROOT)),
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
            "PHASE 16U.35 COMPLETE." if passed else "PHASE 16U.35 FAILED.",
            "",
            "NEXT PHASE",
            "----------",
            "PHASE 16U.36 — REPORT OWNER PRESENTATION LAYER PILOT CLOSURE GATE",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = run_regression()
    print(result["status"])
    for check in result["checks"]:
        print(f"{check['name']}={'PASS' if check['passed'] else 'FAIL'}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u35_report_owner_presentation_layer_pilot_regression_complete"]:
        raise SystemExit(1)
