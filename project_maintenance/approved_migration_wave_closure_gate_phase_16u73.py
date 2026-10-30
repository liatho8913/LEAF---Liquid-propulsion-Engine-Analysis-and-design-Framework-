from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PHASE = "16U.73"
PASS_BANNER = "PASS_PHASE_16U73_APPROVED_MIGRATION_WAVE_CLOSURE_GATE"
FAIL_BANNER = "FAIL_PHASE_16U73_APPROVED_MIGRATION_WAVE_CLOSURE_GATE"

ROOT = Path(__file__).resolve().parents[1]

PATCH_SCRIPT = ROOT / "project_maintenance" / "approved_migration_wave_patch_phase_16u71.py"
REGRESSION_SCRIPT = ROOT / "project_maintenance" / "approved_migration_wave_regression_phase_16u72.py"

PATCH_JSON = ROOT / "project_maintenance" / "grouped_low_risk_owner_batch_patch_phase_16u71.json"
REGRESSION_JSON = ROOT / "project_maintenance" / "approved_migration_wave_regression_phase_16u72.json"

OUT_TXT = ROOT / "project_maintenance" / "APPROVED_MIGRATION_WAVE_CLOSURE_GATE_PHASE_16U73.txt"
OUT_JSON = ROOT / "project_maintenance" / "approved_migration_wave_closure_gate_phase_16u73.json"

TARGETS = [
    "leaf_qt/failure_root_cause_owner.py",
    "leaf_qt/regen_completion_gate_validation_owner.py",
    "leaf_qt/regen_system_signoff_validation_owner.py",
    "leaf_qt/regen_optimisation_scoring_owner.py",
]


def check(name: str, passed: bool, detail: str = "") -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}


def run_script(script: Path, acceptable_banners: list[str]) -> dict:
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

    banner_found = any(banner in proc.stdout for banner in acceptable_banners)

    return {
        "passed": proc.returncode == 0 and banner_found,
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

    checks.append(check("phase_16u71_patch_script_exists", PATCH_SCRIPT.exists(), str(PATCH_SCRIPT.relative_to(ROOT))))
    checks.append(check("phase_16u72_regression_script_exists", REGRESSION_SCRIPT.exists(), str(REGRESSION_SCRIPT.relative_to(ROOT))))

    patch_run = run_script(
        PATCH_SCRIPT,
        [
            "PASS_PHASE_16U71_APPROVED_MIGRATION_WAVE_PATCH",
            "PASS_PHASE_16U71_GROUPED_LOW_RISK_OWNER_BATCH_PATCH",
        ],
    )
    checks.append(check("phase_16u71_patch_rerun_passed", patch_run["passed"], f"returncode={patch_run['returncode']}"))

    regression_run = run_script(
        REGRESSION_SCRIPT,
        ["PASS_PHASE_16U72_APPROVED_MIGRATION_WAVE_REGRESSION"],
    )
    checks.append(check("phase_16u72_regression_rerun_passed", regression_run["passed"], f"returncode={regression_run['returncode']}"))

    patch_payload = read_json(PATCH_JSON)
    regression_payload = read_json(REGRESSION_JSON)

    patch_complete = (
        patch_payload.get("phase_16u71_approved_migration_wave_patch_complete") is True
        or patch_payload.get("phase_16u71_grouped_low_risk_owner_batch_patch_complete") is True
    )

    regression_complete = (
        regression_payload.get("phase_16u72_approved_migration_wave_regression_complete") is True
    )

    checks.append(check("phase_16u71_completion_flag_true", patch_complete, str(patch_payload.get("status"))))
    checks.append(check("phase_16u72_completion_flag_true", regression_complete, str(regression_payload.get("status"))))

    patch_files = {item.get("file"): item for item in patch_payload.get("per_file", [])}
    regression_files = {item.get("file"): item for item in regression_payload.get("per_file", [])}

    per_file = []
    for target in TARGETS:
        path = ROOT / target
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""

        patch_item = patch_files.get(target, {})
        regression_item = regression_files.get(target, {})

        file_checks = [
            check("target_exists", path.exists(), target),
            check("patch_payload_passed", patch_item.get("passed") is True, str(patch_item.get("passed"))),
            check("regression_payload_passed", regression_item.get("passed") is True, str(regression_item.get("passed"))),
            check(
                "contains_shared_status_layer",
                "from leaf_qt.status_presentation import status_severity" in text
                and "_leaf_16u71_status_severity" in text,
                "shared helper present",
            ),
            check(
                "no_legacy_status_patterns_after_helper",
                '"FAIL" in ' not in text[1500:]
                and '"WARN" in ' not in text[1500:]
                and '"PASS" in ' not in text[1500:]
                and '"BLOCKED" in ' not in text[1500:],
                "legacy literals allowed only inside helper fallback",
            ),
        ]

        per_file.append(
            {
                "file": target,
                "passed": all(item["passed"] for item in file_checks),
                "checks": file_checks,
            }
        )

    checks.append(
        check(
            "all_wave_files_closed",
            all(item["passed"] for item in per_file),
            f"{sum(1 for item in per_file if item['passed'])}/{len(per_file)} closed",
        )
    )

    closure_ready = all(item["passed"] for item in checks)

    result = {
        "phase": PHASE,
        "status": PASS_BANNER if closure_ready else FAIL_BANNER,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "target_count": len(TARGETS),
        "closed_count": sum(1 for item in per_file if item["passed"]),
        "failed_count": sum(1 for item in per_file if not item["passed"]),
        "checks": checks,
        "per_file": per_file,
        "phase_16u73_approved_migration_wave_closure_gate_complete": closure_ready,
        "next_phase": "16U.74 — Updated Global Remaining-Candidate Audit",
        "countdown_after_pass": {
            "estimated_remaining_until_16u_conclusion": "~8–74 phases",
            "likely_final_range": "16U.100–16U.120",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.73",
        "APPROVED MIGRATION WAVE CLOSURE GATE",
        "====================================",
        "",
        f"STATUS: {result['status']}",
        f"Generated: {result['generated']}",
        "",
        "FEATURE",
        "-------",
        "Closure gate for the Phase 16U.71 approved migration wave.",
        "",
        "COUNTDOWN",
        "---------",
        "Current completed before this phase: 16U.72",
        "Estimated remaining after this phase if PASS: ~8–74 phases",
        "Likely final range: 16U.100–16U.120",
        "",
        "SUMMARY",
        "-------",
        f"Target count: {result['target_count']}",
        f"Closed count: {result['closed_count']}",
        f"Failed count: {result['failed_count']}",
        "",
        "GATE CHECKS",
        "-----------",
    ]

    for item in checks:
        lines.append(f"{item['name']}: {'PASS' if item['passed'] else 'FAIL'} — {item['detail']}")

    lines.extend(["", "PER-FILE CLOSURE", "----------------"])

    for item in per_file:
        lines.append(f"{item['file']}: {'PASS' if item['passed'] else 'FAIL'}")
        for sub in item["checks"]:
            lines.append(f"  {sub['name']}: {'PASS' if sub['passed'] else 'FAIL'} — {sub['detail']}")

    lines.extend(
        [
            "",
            "CLOSURE DECISION",
            "----------------",
            "The approved migration wave is CLOSED." if closure_ready else "The approved migration wave is NOT CLOSED.",
            "",
            "COMPLETION NOTICE",
            "-----------------",
            "PHASE 16U.73 COMPLETE." if closure_ready else "PHASE 16U.73 FAILED.",
            "",
            "NEXT FEATURE",
            "------------",
            "PHASE 16U.74 — UPDATED GLOBAL REMAINING-CANDIDATE AUDIT",
        ]
    )

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"target_count={result['target_count']}")
    print(f"closed_count={result['closed_count']}")
    print(f"failed_count={result['failed_count']}")
    for item in result["per_file"]:
        print(f"{item['file']}={'PASS' if item['passed'] else 'FAIL'}")
    print(f"countdown_after_pass={result['countdown_after_pass']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")

    if not result["phase_16u73_approved_migration_wave_closure_gate_complete"]:
        raise SystemExit(1)
