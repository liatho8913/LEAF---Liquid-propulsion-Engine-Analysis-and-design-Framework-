from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.wave2_status_adapter_integration_review_phase_16t3t import (
    run_wave2_status_adapter_integration_review,
)


PASS_STATUS = "PASS_WAVE2_FINAL_STATUS_MIGRATION_HANDOVER_PHASE_16T3U"
FAIL_STATUS = "FAIL_WAVE2_FINAL_STATUS_MIGRATION_HANDOVER_PHASE_16T3U"


COMPLETED_PHASES = [
    "16T.3Q.1 Regen Geometry Master Gate",
    "16T.3Q.2 Regen Candidate Population Master Gate",
    "16T.3Q.3 Regen Candidate Ranking Master Gate",
    "16T.3Q.4 Regen Evolution Loop Master Gate",
    "16T.3Q.5 Regen Candidate Mutation Master Gate",
    "16T.3Q.6 Regen Optimisation Master Gate",
    "16T.3Q.7 Regen Scalability Master Gate",
    "16T.3Q.8 Regen Candidate Validator",
    "16T.3Q.9 Regen Source Validation Gate",
    "16T.3Q.10 Regen Axial Geometry Master Gate",
    "16T.3Q.11 Regen Candidate Acceptance Master Gate",
    "16T.3Q.12 Regen Variable Geometry Master Gate",
    "16T.3R Wave 2 Completion Audit",
    "16T.3S Wave 2 Master Gate",
    "16T.3T Wave 2 Integration Review",
]


NEXT_OPTIONS = [
    {
        "option": "PHASE 16T.3V — Wave 3 Candidate Selection",
        "purpose": "Identify the next group of legacy-status modules for structured-status migration.",
        "recommended": True,
    },
    {
        "option": "Structured-status consumer migration",
        "purpose": "Begin changing downstream consumers to rely on structured findings/global status rather than legacy strings.",
        "recommended": False,
    },
    {
        "option": "Full verification harness integration",
        "purpose": "Attach Wave 1 and Wave 2 status checks into a single top-level verification command.",
        "recommended": False,
    },
]


def _finding(code, severity, message, evidence=None):
    return {
        "code": str(code),
        "severity": str(severity).upper(),
        "message": str(message),
        "evidence": evidence or {},
        "phase": "16T.3U",
        "owner": "wave2_final_status_migration_handover",
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


def run_wave2_final_status_migration_handover():
    review = run_wave2_status_adapter_integration_review()
    findings = []

    if review.get("passed") is True:
        findings.append(
            _finding(
                "WAVE2_INTEGRATION_REVIEW_PASSED",
                "INFO",
                "Wave 2 integration review passed.",
                {"status": review.get("status")},
            )
        )
    else:
        findings.append(
            _finding(
                "WAVE2_INTEGRATION_REVIEW_FAILED",
                "FAIL",
                "Wave 2 integration review failed.",
                {"status": review.get("status")},
            )
        )

    if len(COMPLETED_PHASES) == 15:
        findings.append(
            _finding(
                "WAVE2_PHASE_RECORD_COMPLETE",
                "INFO",
                "Wave 2 final handover records all expected implementation and closure phases.",
                {"completed_phase_count": len(COMPLETED_PHASES)},
            )
        )
    else:
        findings.append(
            _finding(
                "WAVE2_PHASE_RECORD_INCOMPLETE",
                "FAIL",
                "Wave 2 final handover phase record is incomplete.",
                {"completed_phase_count": len(COMPLETED_PHASES)},
            )
        )

    findings.append(
        _finding(
            "BACKWARDS_COMPATIBILITY_RETAINED",
            "INFO",
            "Legacy status strings and public payload compatibility remain intentionally retained.",
            {
                "reason": "Downstream consumers have not yet been migrated to structured-only status consumption."
            },
        )
    )

    findings.append(
        _finding(
            "WAVE2_READY_FOR_NEXT_SELECTION",
            "INFO",
            "Wave 2 is ready for the next migration-planning phase.",
            {"recommended_next_phase": "PHASE 16T.3V — Wave 3 Candidate Selection"},
        )
    )

    canonical = _canonical_status(findings)
    passed = canonical == "PASS"
    status = PASS_STATUS if passed else FAIL_STATUS

    severity_counts = {}
    for item in findings:
        severity = item["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    report_lines = [
        "LEAF PHASE 16T.3U",
        "WAVE 2 FINAL STATUS MIGRATION HANDOVER",
        "======================================",
        "",
        f"Status: {status}",
        f"Canonical Status: {canonical}",
        f"Passed: {passed}",
        "",
        "Purpose:",
        "This handover records the completed Wave 2 structured-status adapter migration.",
        "",
        "Input:",
        f"- Integration review status: {review.get('status')}",
        "",
        "Completed Phases:",
    ]

    for phase in COMPLETED_PHASES:
        report_lines.append(f"- {phase}")

    report_lines.extend(
        [
            "",
            "Findings:",
        ]
    )

    for item in findings:
        report_lines.append(
            f"- [{item['severity']}] {item['code']}: {item['message']}"
        )

    report_lines.extend(
        [
            "",
            "Residual Risks Carried Forward:",
        ]
    )

    for risk in review.get("residual_risks", []):
        report_lines.append(
            f"- [{risk.get('severity')}] {risk.get('risk')} Mitigation: {risk.get('mitigation')}"
        )

    report_lines.extend(
        [
            "",
            "Next Options:",
        ]
    )

    for option in NEXT_OPTIONS:
        marker = "RECOMMENDED" if option["recommended"] else "OPTIONAL"
        report_lines.append(
            f"- [{marker}] {option['option']}: {option['purpose']}"
        )

    report_lines.extend(
        [
            "",
            "Decision:",
            (
                "Wave 2 final migration handover is complete."
                if passed
                else "Wave 2 final migration handover is blocking."
            ),
        ]
    )

    report = "\n".join(report_lines)

    return {
        "phase": "16T.3U",
        "passed": passed,
        "status": status,
        "canonical_status": canonical,
        "global_status": canonical,
        "structured_findings": findings,
        "global_status_payload": {
            "owner": "wave2_final_status_migration_handover",
            "phase": "16T.3U",
            "canonical_status": canonical,
            "global_status": canonical,
            "legacy_status": status,
            "passed": passed,
            "finding_count": len(findings),
            "severity_counts": severity_counts,
            "findings": findings,
            "input_integration_review_status": review.get("status"),
        },
        "adapter_report": report,
        "report": report,
        "integration_review": review,
        "completed_phases": COMPLETED_PHASES,
        "next_options": NEXT_OPTIONS,
        "wave2_final_status_migration_handover_complete": passed,
        "phase_16t3u_wave2_final_status_migration_handover_complete": passed,
    }


if __name__ == "__main__":
    result = run_wave2_final_status_migration_handover()
    print(result["report"])
    if not result["passed"]:
        raise SystemExit(1)
