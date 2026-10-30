from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PHASE = "16U.40"
PASS_BANNER = "PASS_PHASE_16U40_REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_CLOSURE_GATE"
FAIL_BANNER = "FAIL_PHASE_16U40_REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_CLOSURE_GATE"

ROOT = Path(__file__).resolve().parents[1]

PATCH_SCRIPT = ROOT / "project_maintenance" / "regen_cross_section_viewer_presentation_layer_patch_phase_16u38.py"
REGRESSION_SCRIPT = ROOT / "project_maintenance" / "regen_cross_section_viewer_presentation_layer_regression_phase_16u39.py"

PATCH_JSON = ROOT / "project_maintenance" / "regen_cross_section_viewer_presentation_layer_patch_phase_16u38.json"
REGRESSION_JSON = ROOT / "project_maintenance" / "regen_cross_section_viewer_presentation_layer_regression_phase_16u39.json"

TARGET = ROOT / "leaf_qt" / "regen_cross_section_viewer.py"
UPLOAD_COPY = ROOT / "LEAF_UPLOAD" / "leaf_qt" / "regen_cross_section_viewer.py"

OUT_TXT = ROOT / "project_maintenance" / "REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_CLOSURE_GATE_PHASE_16U40.txt"
OUT_JSON = ROOT / "project_maintenance" / "regen_cross_section_viewer_presentation_layer_closure_gate_phase_16u40.json"


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def run_script(script: Path, expected_banner: str) -> dict:
    if not script.exists():
        return {
            "passed": False,
            "returncode": None,
            "stdout": "",
            "stderr": f"Missing script: {script}",
        }

    proc = subprocess.run(
        [sys.executable, str(script.relative_to(ROOT))],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    return {
        "passed": proc.returncode == 0 and expected_banner in proc.stdout,
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
    checks.append(check("upload_duplicate_exists", UPLOAD_COPY.exists(), str(UPLOAD_COPY.relative_to(ROOT)) if UPLOAD_COPY.exists() else "not present"))
    checks.append(check("phase_16u38_patch_script_exists", PATCH_SCRIPT.exists(), str(PATCH_SCRIPT.relative_to(ROOT))))
    checks.append(check("phase_16u39_regression_script_exists", REGRESSION_SCRIPT.exists(), str(REGRESSION_SCRIPT.relative_to(ROOT))))

    patch_run = run_script(
        PATCH_SCRIPT,
        "PASS_PHASE_16U38_REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_PATCH",
    )
    checks.append(check("phase_16u38_patch_rerun_passed", patch_run["passed"], f"returncode={patch_run['returncode']}"))

    regression_run = run_script(
        REGRESSION_SCRIPT,
        "PASS_PHASE_16U39_REGEN_CROSS_SECTION_VIEWER_PRESENTATION_LAYER_REGRESSION",
    )
    checks.append(check("phase_16u39_regression_rerun_passed", regression_run["passed"], f"returncode={regression_run['returncode']}"))

    patch_json = read_json(PATCH_JSON)
    regression_json = read_json(REGRESSION_JSON)

    checks.append(
        check(
            "phase_16u38_completion_flag_true",
            patch_json.get("phase_16u38_regen_cross_section_viewer_presentation_layer_patch_complete") is True,
            str(patch_json.get("status")),
        )
    )

    checks.append(
        check(
            "phase_16u39_completion_flag_true",
            regression_json.get("phase_16u39_regen_cross_section_viewer_presentation_layer_regression_complete") is True,
            str(regression_json.get("status")),
        )
    )

    target_text = TARGET.read_text(encoding="utf-8", errors="replace") if TARGET.exists() else ""
    checks.append(
        check(
            "production_target_contains_shared_status_layer",
            "from leaf_qt.status_presentation import" in target_text
            and "_leaf_16u38_status_severity" in target_text,
            "shared presentation helpers present",
        )
    )

    if UPLOAD_COPY.exists():
        upload_text = UPLOAD_COPY.read_text(encoding="utf-8", errors="replace")
        checks.append(
            check(
                "leaf_upload_duplicate_still_unpatched",
                "_leaf_16u38_status_severity" not in upload_text,
                "duplicate remains untouched",
            )
        )

    closure_ready = all(item["passed"] for item in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if closure_ready else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target": str(TARGET.relative_to(ROOT)),
        "checks": checks,
        "phase_16u40_regen_cross_section_viewer_presentation_layer_closure_gate_complete": closure_ready,
        "next_phase": "16U.41 — Next Report Owner Rollout Candidate Audit",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.40",
        "REGEN CROSS SECTION VIEWER PRESENTATION LAYER CLOSURE GATE",
        "==========================================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Closure gate for the first wider report-owner/UI presentation-layer rollout.",
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
            "The regen cross-section viewer presentation-layer rollout is CLOSED." if closure_ready else "The regen cross-section viewer presentation-layer rollout is NOT CLOSED.",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.40 COMPLETE." if closure_ready else "PHASE 16U.40 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.41 — NEXT REPORT OWNER ROLLOUT CANDIDATE AUDIT",
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

    if not result["phase_16u40_regen_cross_section_viewer_presentation_layer_closure_gate_complete"]:
        raise SystemExit(1)
