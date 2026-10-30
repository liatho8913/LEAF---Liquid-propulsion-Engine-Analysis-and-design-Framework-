from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

OUT_JSON = ROOT / "project_maintenance" / "phase_16u166_safe_wave_regression_and_reclassification.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u166_safe_wave_regression_and_reclassification.txt"

SCRIPTS = [
    ROOT / "project_maintenance" / "phase_16u162_global_repository_presentation_layer_sanity_audit.py",
    ROOT / "project_maintenance" / "phase_16u163_presentation_debt_classifier.py",
    ROOT / "project_maintenance" / "phase_16u164_high_risk_presentation_debt_manifest.py",
]


def run_script(path: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    return {
        "script": str(path.relative_to(ROOT)),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main() -> dict:
    runs = [run_script(path) for path in SCRIPTS]

    audit_json = ROOT / "project_maintenance" / "phase_16u162_global_repository_presentation_layer_sanity_audit.json"
    class_json = ROOT / "project_maintenance" / "phase_16u163_presentation_debt_classification.json"
    manifest_json = ROOT / "project_maintenance" / "phase_16u164_high_risk_presentation_debt_manifest.json"

    audit = json.loads(audit_json.read_text(encoding="utf-8"))
    classification = json.loads(class_json.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_json.read_text(encoding="utf-8"))

    compile_failure_count = audit.get("compile_failure_count", 0)
    high_risk_finding_count = classification.get("high_risk_finding_count", 0)
    high_risk_file_count = classification.get("high_risk_file_count", 0)
    safe_wave_candidate_count = manifest.get("safe_wave_candidate_count", 0)

    passed = (
        compile_failure_count == 0
        and high_risk_finding_count <= 90
        and high_risk_file_count <= 45
    )

    result = {
        "phase": "16U.166",
        "runs": runs,
        "compile_failure_count": compile_failure_count,
        "raw_finding_count": audit.get("finding_count", 0),
        "high_risk_finding_count": high_risk_finding_count,
        "high_risk_file_count": high_risk_file_count,
        "safe_wave_candidate_count": safe_wave_candidate_count,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U166_SAFE_WAVE_REGRESSION_AND_RECLASSIFICATION"
            if passed
            else "FAIL_PHASE_16U166_SAFE_WAVE_REGRESSION_AND_RECLASSIFICATION"
        ),
        "next_phase": "16U.167_MANUAL_REVIEW_PRESENTATION_DEBT_ARCHITECTURE_MANIFEST",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.166",
        "SAFE WAVE REGRESSION AND RECLASSIFICATION",
        "=" * 48,
        f"status={result['status']}",
        f"compile_failure_count={compile_failure_count}",
        f"raw_finding_count={result['raw_finding_count']}",
        f"high_risk_file_count={high_risk_file_count}",
        f"high_risk_finding_count={high_risk_finding_count}",
        f"safe_wave_candidate_count={safe_wave_candidate_count}",
        "",
        "SCRIPT RUNS",
        "-" * 11,
    ]

    for run in runs:
        lines.append("")
        lines.append(f"script={run['script']}")
        lines.append(f"returncode={run['returncode']}")
        if run["stdout"].strip():
            lines.append("stdout:")
            lines.append(run["stdout"].strip())
        if run["stderr"].strip():
            lines.append("stderr:")
            lines.append(run["stderr"].strip())

    lines.extend(["", f"json={OUT_JSON}", f"text={OUT_TXT}"])
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

    return result


if __name__ == "__main__":
    result = main()
    print(result["status"])
    print(f"compile_failure_count={result['compile_failure_count']}")
    print(f"raw_finding_count={result['raw_finding_count']}")
    print(f"high_risk_file_count={result['high_risk_file_count']}")
    print(f"high_risk_finding_count={result['high_risk_finding_count']}")
    print(f"safe_wave_candidate_count={result['safe_wave_candidate_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
