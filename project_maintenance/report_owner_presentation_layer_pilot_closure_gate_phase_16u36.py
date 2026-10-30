from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PHASE = "16U.36"
PASS_BANNER = "PASS_PHASE_16U36_REPORT_OWNER_PRESENTATION_LAYER_PILOT_CLOSURE_GATE"
FAIL_BANNER = "FAIL_PHASE_16U36_REPORT_OWNER_PRESENTATION_LAYER_PILOT_CLOSURE_GATE"

ROOT = Path(__file__).resolve().parents[1]

REGRESSION_SCRIPT = ROOT / "project_maintenance" / "report_owner_presentation_layer_pilot_regression_phase_16u35.py"
REGRESSION_JSON = ROOT / "project_maintenance" / "report_owner_presentation_layer_pilot_regression_phase_16u35.json"

STATUS_PRESENTATION = ROOT / "leaf_qt" / "status_presentation.py"
PILOT_WINDOW = ROOT / "leaf_qt" / "foundation_test_runner_window.py"

OUT_TXT = ROOT / "project_maintenance" / "REPORT_OWNER_PRESENTATION_LAYER_PILOT_CLOSURE_GATE_PHASE_16U36.txt"
OUT_JSON = ROOT / "project_maintenance" / "report_owner_presentation_layer_pilot_closure_gate_phase_16u36.json"


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def run_16u35_again() -> dict:
    if not REGRESSION_SCRIPT.exists():
        return {
            "passed": False,
            "returncode": None,
            "stdout": "",
            "stderr": "16U.35 regression script missing.",
        }

    result = subprocess.run(
        [sys.executable, str(REGRESSION_SCRIPT.relative_to(ROOT))],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    return {
        "passed": result.returncode == 0 and "PASS_PHASE_16U35_REPORT_OWNER_PRESENTATION_LAYER_PILOT_REGRESSION" in result.stdout,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> dict:
    checks = []

    checks.append(check("status_presentation_exists", STATUS_PRESENTATION.exists(), str(STATUS_PRESENTATION.relative_to(ROOT))))
    checks.append(check("pilot_window_exists", PILOT_WINDOW.exists(), str(PILOT_WINDOW.relative_to(ROOT))))
    checks.append(check("phase_16u35_script_exists", REGRESSION_SCRIPT.exists(), str(REGRESSION_SCRIPT.relative_to(ROOT))))

    rerun = run_16u35_again()
    checks.append(check("phase_16u35_regression_rerun_passed", rerun["passed"], f"returncode={rerun['returncode']}"))

    regression_payload = {}
    if REGRESSION_JSON.exists():
        try:
            regression_payload = json.loads(REGRESSION_JSON.read_text(encoding="utf-8"))
        except Exception as exc:
            regression_payload = {"json_error": repr(exc)}

    checks.append(
        check(
            "phase_16u35_json_exists",
            REGRESSION_JSON.exists(),
            str(REGRESSION_JSON.relative_to(ROOT)),
        )
    )

    checks.append(
        check(
            "phase_16u35_completion_flag_true",
            regression_payload.get("phase_16u35_report_owner_presentation_layer_pilot_regression_complete") is True,
            str(regression_payload.get("phase_16u35_report_owner_presentation_layer_pilot_regression_complete")),
        )
    )

    pilot_text = PILOT_WINDOW.read_text(encoding="utf-8", errors="replace") if PILOT_WINDOW.exists() else ""

    checks.append(
        check(
            "pilot_imports_legacy_compatibility_producer",
            "from leaf_qt.status_presentation import LegacyCompatibilityProducer" in pilot_text,
            "pilot uses shared presentation import",
        )
    )

    checks.append(
        check(
            "pilot_uses_marker_from_bool",
            "LegacyCompatibilityProducer.marker_from_bool(passed)" in pilot_text,
            "pilot status marker delegated to shared layer",
        )
    )

    closure_ready = all(item["passed"] for item in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if closure_ready else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "checks": checks,
        "phase_16u36_report_owner_presentation_layer_pilot_closure_gate_complete": closure_ready,
        "next_phase": "16U.37 — Report Owner Presentation Layer Rollout Audit",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.36",
        "REPORT OWNER PRESENTATION LAYER PILOT CLOSURE GATE",
        "===================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Closure gate for the first production report-owner presentation-layer pilot.",
        "",
        "CHECKS",
        "------",
    ]

    for item in checks:
        lines.append(f"{item['name']}: {'PASS' if item['passed'] else 'FAIL'} — {item['detail']}")

    lines.extend(
        [
            "",
            "CLOSURE DECISION",
            "----------------",
            "The report-owner presentation-layer pilot is CLOSED." if closure_ready else "The report-owner presentation-layer pilot is NOT CLOSED.",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.36 COMPLETE." if closure_ready else "PHASE 16U.36 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.37 — REPORT OWNER PRESENTATION LAYER ROLLOUT AUDIT",
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

    if not result["phase_16u36_report_owner_presentation_layer_pilot_closure_gate_complete"]:
        raise SystemExit(1)
