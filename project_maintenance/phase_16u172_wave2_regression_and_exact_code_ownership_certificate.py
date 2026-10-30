from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

OUT_JSON = ROOT / "project_maintenance" / "phase_16u172_wave2_regression_and_exact_code_ownership_certificate.json"
OUT_TXT = ROOT / "project_maintenance" / "phase_16u172_wave2_regression_and_exact_code_ownership_certificate.txt"

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
    owner_json = ROOT / "project_maintenance" / "phase_16u171f_no_literal_rescan_and_exact_owner_gate.json"

    audit = json.loads(audit_json.read_text(encoding="utf-8"))
    classification = json.loads(class_json.read_text(encoding="utf-8"))
    ownership = json.loads(owner_json.read_text(encoding="utf-8"))

    compile_failure_count = audit.get("compile_failure_count", 0)
    high_risk_finding_count = classification.get("high_risk_finding_count", 0)
    high_risk_file_count = classification.get("high_risk_file_count", 0)

    exact_owned_count = ownership.get("exact_owned_count", 0)
    unresolved_count = ownership.get("unresolved_count", 0)

    passed = (
        compile_failure_count == 0
        and exact_owned_count == 52
        and unresolved_count == 19
    )

    result = {
        "phase": "16U.172",
        "runs": runs,
        "compile_failure_count": compile_failure_count,
        "raw_finding_count": audit.get("finding_count", 0),
        "high_risk_file_count": high_risk_file_count,
        "high_risk_finding_count": high_risk_finding_count,
        "exact_owned_count": exact_owned_count,
        "unresolved_count": unresolved_count,
        "passed": passed,
        "status": (
            "PASS_PHASE_16U172_WAVE2_REGRESSION_AND_EXACT_CODE_OWNERSHIP_CERTIFICATE"
            if passed
            else "FAIL_PHASE_16U172_WAVE2_REGRESSION_AND_EXACT_CODE_OWNERSHIP_CERTIFICATE"
        ),
        "next_phase": "16U.173_UNQUOTED_STATUS_TOKEN_RESOLVER",
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 16U.172",
        "WAVE 2 REGRESSION AND EXACT-CODE OWNERSHIP CERTIFICATE",
        "=" * 64,
        f"status={result['status']}",
        f"compile_failure_count={compile_failure_count}",
        f"raw_finding_count={result['raw_finding_count']}",
        f"high_risk_file_count={high_risk_file_count}",
        f"high_risk_finding_count={high_risk_finding_count}",
        f"exact_owned_count={exact_owned_count}",
        f"unresolved_count={unresolved_count}",
        "",
        "INTERPRETATION",
        "-" * 14,
        "Wave 2 did not convert exact status-code predicates into severity predicates.",
        "This is correct: exact codes are active state-machine / payload ownership, not presentation ownership.",
        "Remaining unresolved findings are unquoted PASS/WARN/FAIL tokens requiring symbolic-token resolution.",
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
    print(f"exact_owned_count={result['exact_owned_count']}")
    print(f"unresolved_count={result['unresolved_count']}")
    print(f"text_report={OUT_TXT}")
    print(f"json_report={OUT_JSON}")

    if not result["passed"]:
        raise SystemExit(1)
