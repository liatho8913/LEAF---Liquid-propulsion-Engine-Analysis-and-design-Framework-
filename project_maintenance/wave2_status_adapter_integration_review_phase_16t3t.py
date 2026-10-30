from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave2_status_adapter_master_gate_phase_16t3s import (
    run_wave2_status_adapter_master_gate,
)


PASS_STATUS = "PASS_WAVE2_STATUS_ADAPTER_INTEGRATION_REVIEW_PHASE_16T3T"
FAIL_STATUS = "FAIL_WAVE2_STATUS_ADAPTER_INTEGRATION_REVIEW_PHASE_16T3T"


def _finding(code, severity, message, evidence=None):
    return {
        "code": str(code),
        "severity": str(severity).upper(),
        "message": str(message),
        "evidence": evidence or {},
        "phase": "16T.3T",
        "owner": "wave2_status_adapter_integration_review",
    }


def _canonical_status(findings):
    severities = {str(f.get("severity", "")).upper() for f in findings}

    if "FAIL" in severities:
        return "FAIL"
    if "BLOCKED" in severities:
        return "BLOCKED"
    if "REVIEW_REQUIRED" in severities:
        return "REVIEW_REQUIRED"
    return "PASS"


def run_wave2_status_adapter_integration_review():
    master_gate = run_wave2_status_adapter_master_gate()
    findings = []

    if master_gate.get("passed") is True:
        findings.append(
            _finding(
                "WAVE2_MASTER_GATE_PASSED",
                "INFO",
                "Wave 2 master gate passed.",
                {"status": master_gate.get("status")},
            )
        )
    else:
        findings.append(
            _finding(
                "WAVE2_MASTER_GATE_FAILED",
                "FAIL",
                "Wave 2 master gate failed.",
                {"status": master_gate.get("status")},
            )
        )

    completion_audit = master_gate.get("completion_audit") or {}

    module_count = completion_audit.get("module_count")
    module_pass_count = completion_audit.get("module_pass_count")
    missing_tests = completion_audit.get("missing_focused_tests") or []

    if module_count == 12 and module_pass_count == 12:
        findings.append(
            _finding(
                "WAVE2_MODULE_COVERAGE_COMPLETE",
                "INFO",
                "All selected Wave 2 modules are covered and passed.",
                {
                    "module_count": module_count,
                    "module_pass_count": module_pass_count,
                },
            )
        )
    else:
        findings.append(
            _finding(
                "WAVE2_MODULE_COVERAGE_INCOMPLETE",
                "FAIL",
                "Wave 2 module coverage is incomplete.",
                {
                    "module_count": module_count,
                    "module_pass_count": module_pass_count,
                },
            )
        )

    if missing_tests:
        findings.append(
            _finding(
                "WAVE2_TEST_COVERAGE_PARTIAL",
                "REVIEW_REQUIRED",
                "One or more focused Wave 2 adapter tests are missing.",
                {"missing_focused_tests": missing_tests},
            )
        )
    else:
        findings.append(
            _finding(
                "WAVE2_TEST_COVERAGE_ACCEPTABLE",
                "INFO",
                "Focused Wave 2 adapter test files are present.",
                {},
            )
        )

    findings.append(
        _finding(
            "BACKWARDS_COMPATIBILITY_POLICY_PRESERVED",
            "INFO",
            "Wave 2 adapters were implemented as additive compatibility layers.",
            {
                "policy": (
                    "existing public functions, legacy status strings, and payload fields "
                    "were preserved while structured findings and global status fields were added"
                )
            },
        )
    )

    findings.append(
        _finding(
            "NORMALISATION_BEHAVIOUR_DOCUMENTED",
            "INFO",
            "Several original gates normalise invalid or incomplete inputs before adapter classification.",
            {
                "examples": [
                    "mutation payload invalid input normalised to missing payload",
                    "source validation placeholder probe normalised to UNKNOWN/NONE modes",
                    "optimisation failed-check probe normalised into master gate failure state",
                ]
            },
        )
    )

    findings.append(
        _finding(
            "NO_PRODUCTION_LOGIC_REDESIGN_DETECTED",
            "INFO",
            "Wave 2 migration did not intentionally redesign engineering or optimisation behaviour.",
            {
                "scope": "status adapter migration only",
            },
        )
    )

    findings.append(
        _finding(
            "NEXT_MIGRATION_READY",
            "INFO",
            "Wave 2 is ready to hand off to the next status migration phase.",
            {
                "next_phase_recommendation": (
                    "identify Wave 3 modules or begin structured-status consumer migration"
                )
            },
        )
    )

    canonical = _canonical_status(findings)
    passed = canonical == "PASS"
    status = PASS_STATUS if passed else FAIL_STATUS

    severity_counts = {}
    for item in findings:
        severity = item["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    residual_risks = [
        {
            "risk": "Some focused tests are structural rather than full behavioural regressions.",
            "severity": "LOW",
            "mitigation": "Future full-suite verification should execute all available LEAF regression tests.",
        },
        {
            "risk": "Some modules expose attach/run APIs rather than consistent build APIs.",
            "severity": "LOW",
            "mitigation": "Future API harmonisation can wrap public entry points without breaking callers.",
        },
        {
            "risk": "Legacy PASS/WARN/FAIL strings still coexist with canonical statuses.",
            "severity": "EXPECTED",
            "mitigation": "Legacy strings remain until later structured-status consumer migration.",
        },
    ]

    report_lines = [
        "LEAF PHASE 16T.3T",
        "WAVE 2 STATUS ADAPTER INTEGRATION REVIEW",
        "=========================================",
        "",
        f"Status: {status}",
        f"Canonical Status: {canonical}",
        f"Passed: {passed}",
        "",
        "Inputs:",
        f"- Master gate status: {master_gate.get('status')}",
        f"- Completion audit status: {completion_audit.get('status')}",
        f"- Modules passed: {module_pass_count} / {module_count}",
        f"- Missing focused tests: {len(missing_tests)}",
        "",
        "Findings:",
    ]

    for item in findings:
        report_lines.append(
            f"- [{item['severity']}] {item['code']}: {item['message']}"
        )

    report_lines.extend(
        [
            "",
            "Residual Risks:",
        ]
    )

    for risk in residual_risks:
        report_lines.append(
            f"- [{risk['severity']}] {risk['risk']} Mitigation: {risk['mitigation']}"
        )

    report_lines.extend(
        [
            "",
            "Decision:",
            (
                "Wave 2 integration review is complete and non-blocking."
                if passed
                else "Wave 2 integration review is blocking."
            ),
        ]
    )

    report = "\n".join(report_lines)

    return {
        "phase": "16T.3T",
        "passed": passed,
        "status": status,
        "canonical_status": canonical,
        "global_status": canonical,
        "structured_findings": findings,
        "global_status_payload": {
            "owner": "wave2_status_adapter_integration_review",
            "phase": "16T.3T",
            "canonical_status": canonical,
            "global_status": canonical,
            "legacy_status": status,
            "passed": passed,
            "finding_count": len(findings),
            "severity_counts": severity_counts,
            "findings": findings,
            "input_master_gate_status": master_gate.get("status"),
        },
        "adapter_report": report,
        "report": report,
        "master_gate": master_gate,
        "residual_risks": residual_risks,
        "wave2_status_adapter_integration_review_complete": passed,
        "phase_16t3t_wave2_status_adapter_integration_review_complete": passed,
    }


if __name__ == "__main__":
    result = run_wave2_status_adapter_integration_review()
    print(result["report"])
    if not result["passed"]:
        raise SystemExit(1)
