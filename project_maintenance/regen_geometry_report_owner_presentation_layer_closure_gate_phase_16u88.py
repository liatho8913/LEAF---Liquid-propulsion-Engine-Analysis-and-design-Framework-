from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PHASE = "16U.88"
PASS_BANNER = "PASS_PHASE_16U88_REGEN_GEOMETRY_REPORT_OWNER_PRESENTATION_LAYER_CLOSURE_GATE"
FAIL_BANNER = "FAIL_PHASE_16U88_REGEN_GEOMETRY_REPORT_OWNER_PRESENTATION_LAYER_CLOSURE_GATE"

ROOT = Path(__file__).resolve().parents[1]

TARGET = ROOT / "leaf_qt" / "regen_geometry_report_owner.py"

PATCH_SCRIPT = ROOT / "project_maintenance" / "regen_geometry_report_owner_presentation_layer_patch_phase_16u86.py"
REGRESSION_SCRIPT = ROOT / "project_maintenance" / "regen_geometry_report_owner_presentation_layer_regression_phase_16u87.py"

PATCH_JSON = ROOT / "project_maintenance" / "regen_geometry_report_owner_presentation_layer_patch_phase_16u86.json"
REGRESSION_JSON = ROOT / "project_maintenance" / "regen_geometry_report_owner_presentation_layer_regression_phase_16u87.json"

OUT_TXT = ROOT / "project_maintenance" / "REGEN_GEOMETRY_REPORT_OWNER_PRESENTATION_LAYER_CLOSURE_GATE_PHASE_16U88.txt"
OUT_JSON = ROOT / "project_maintenance" / "regen_geometry_report_owner_presentation_layer_closure_gate_phase_16u88.json"


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def run_script(script: Path, banner: str) -> dict:
    if not script.exists():
        return {
            "passed": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"missing script: {script}",
        }

    proc = subprocess.run(
        [sys.executable, str(script.relative_to(ROOT))],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    return {
        "passed": proc.returncode == 0 and banner in proc.stdout,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"json_error": repr(exc)}


def main() -> dict:
    checks = []

    checks.append(check("production_target_exists", TARGET.exists(), str(TARGET.relative_to(ROOT))))
    checks.append(check("phase_16u86_patch_script_exists", PATCH_SCRIPT.exists(), str(PATCH_SCRIPT.relative_to(ROOT))))
    checks.append(check("phase_16u87_regression_script_exists", REGRESSION_SCRIPT.exists(), str(REGRESSION_SCRIPT.relative_to(ROOT))))

    patch_run = run_script(
        PATCH_SCRIPT,
        "PASS_PHASE_16U86_REGEN_GEOMETRY_REPORT_OWNER_PRESENTATION_LAYER_PATCH",
    )
    checks.append(check("phase_16u86_patch_rerun_passed", patch_run["passed"], f"returncode={patch_run['returncode']}"))

    regression_run = run_script(
        REGRESSION_SCRIPT,
        "PASS_PHASE_16U87_REGEN_GEOMETRY_REPORT_OWNER_PRESENTATION_LAYER_REGRESSION",
    )
    checks.append(check("phase_16u87_regression_rerun_passed", regression_run["passed"], f"returncode={regression_run['returncode']}"))

    patch_payload = read_json(PATCH_JSON)
    regression_payload = read_json(REGRESSION_JSON)

    checks.append(
        check(
            "phase_16u86_completion_flag_true",
            patch_payload.get("phase_16u86_regen_geometry_report_owner_presentation_layer_patch_complete") is True,
            str(patch_payload.get("status")),
        )
    )

    checks.append(
        check(
            "phase_16u87_completion_flag_true",
            regression_payload.get("phase_16u87_regen_geometry_report_owner_presentation_layer_regression_complete") is True,
            str(regression_payload.get("status")),
        )
    )

    target_text = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""

    checks.append(
        check(
            "production_target_contains_shared_status_layer",
            "from leaf_qt.status_presentation import" in target_text
            and "status_severity" in target_text
            and "_leaf_16u86_status_severity" in target_text,
            "shared status presentation helper present",
        )
    )

    checks.append(
        check(
            "production_target_has_no_legacy_status_patterns_after_helper",
            '"FAIL" in ' not in target_text[1500:]
            and '"WARN" in ' not in target_text[1500:]
            and '"PASS" in ' not in target_text[1500:]
            and '"BLOCKED" in ' not in target_text[1500:],
            "legacy literals allowed only inside helper fallback",
        )
    )

    closure_ready = all(item["passed"] for item in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if closure_ready else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target": str(TARGET.relative_to(ROOT)),
        "checks": checks,
        "phase_16u88_regen_geometry_report_owner_presentation_layer_closure_gate_complete": closure_ready,
        "next_phase": "16U.89 — Updated Global Remaining-Candidate Audit",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.88",
        "REGEN GEOMETRY REPORT OWNER PRESENTATION LAYER CLOSURE GATE",
        "============================================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Closure gate for the regen geometry report owner presentation-layer migration.",
        "",
        "TARGET CLOSED",
        "-------------",
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
            "CLOSURE DECISION",
            "----------------",
            "The regen geometry report owner presentation-layer migration is CLOSED." if closure_ready else "The regen geometry report owner presentation-layer migration is NOT CLOSED.",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.88 COMPLETE." if closure_ready else "PHASE 16U.88 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.89 — UPDATED GLOBAL REMAINING-CANDIDATE AUDIT",
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

    if not result["phase_16u88_regen_geometry_report_owner_presentation_layer_closure_gate_complete"]:
        raise SystemExit(1)
