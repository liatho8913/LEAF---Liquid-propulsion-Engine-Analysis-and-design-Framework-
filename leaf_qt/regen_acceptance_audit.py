"""
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    def status_severity(value):
        text = str(value or "").upper()
        if "FAIL" in text or "BLOCKED" in text or "ERROR" in text:
            return "FAIL"
        if "WARN" in text or "PARTIAL" in text or "DEGRADED" in text:
            return "WARN"
        if "PASS" in text or "OK" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"

    class LegacyCompatibilityProducer:
        @staticmethod
        def marker_from_bool(value, pass_marker="PASS", fail_marker="FAIL"):
            return pass_marker if bool(value) else fail_marker

        @staticmethod
        def marker_from_status(value):
            severity = status_severity(value)
            if severity in {"PASS", "WARN", "FAIL"}:
                return severity
            return "UNKNOWN"

        @staticmethod
        def status_severity(value):
            return status_severity(value)

PHASE 16L.3 — Acceptance Audit

Purpose:
- Audit acceptance criteria and engineering acceptance report.
- Confirm acceptance evidence is complete and internally consistent.
- Does not alter geometry.
- Does not rerun solver.
"""
from leaf_qt.status_presentation import LegacyCompatibilityProducer

PASS_STATUS = "PASS_REGEN_ACCEPTANCE_AUDIT_PHASE_16L3"
FAIL_STATUS = "FAIL_REGEN_ACCEPTANCE_AUDIT_PHASE_16L3"


def attach_regen_acceptance_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16l2_complete") is not True:
        blockers.append("Phase 16L.2 engineering acceptance report has not passed.")

    criteria = results.get("regen_acceptance_criteria_payload")
    report_payload = results.get("regen_engineering_acceptance_report_payload")

    if not isinstance(criteria, dict) or not criteria:
        blockers.append("Acceptance criteria payload is missing.")

    if not isinstance(report_payload, dict) or not report_payload:
        blockers.append("Engineering acceptance report payload is missing.")

    audit_items = []

    if isinstance(criteria, dict):
        audit_items.append(_audit_item(
            "criteria_all_passed",
            criteria.get("failed_count") == 0,
            f"failed_count={criteria.get('failed_count')}",
        ))
        audit_items.append(_audit_item(
            "criteria_counts_consistent",
            criteria.get("criteria_count") == criteria.get("passed_count") + criteria.get("failed_count"),
            "criteria_count should equal passed_count + failed_count",
        ))

    if isinstance(report_payload, dict):
        summary = report_payload.get("acceptance_summary") or {}
        audit_items.append(_audit_item(
            "readiness_statement_present",
            report_payload.get("readiness") == "ENGINEERING_ACCEPTANCE_READY",
            f"readiness={report_payload.get('readiness')}",
        ))
        audit_items.append(_audit_item(
            "report_failed_count_zero",
            summary.get("failed_count") == 0,
            f"failed_count={summary.get('failed_count')}",
        ))
        audit_items.append(_audit_item(
            "trust_score_one",
            summary.get("trust_score") == 1.0,
            f"trust_score={summary.get('trust_score')}",
        ))
        audit_items.append(_audit_item(
            "limits_present",
            isinstance(report_payload.get("limits"), list) and len(report_payload.get("limits")) > 0,
            "engineering limits must be stated",
        ))

    failed_items = [item for item in audit_items if item.get("passed") is not True]

    for item in failed_items:
        blockers.append(f"Acceptance audit item failed: {item.get('name')}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = {
        "status": status,
        "source_phase": "16L.3",
        "visibility": "REPORT_ONLY",
        "candidate_id": _candidate_id(criteria, report_payload),
        "audit_item_count": len(audit_items),
        "passed_count": sum(1 for item in audit_items if item.get("passed") is True),
        "failed_count": len(failed_items),
        "audit_items": audit_items,
    }

    report = _build_report(status, blockers, payload)

    results["regen_acceptance_audit_complete"] = True
    results["phase_16l3_complete"] = status == PASS_STATUS
    results["regen_acceptance_audit_status"] = status
    results["phase_16l3_status"] = status
    results["regen_acceptance_audit_blockers"] = blockers
    results["regen_acceptance_audit_payload"] = payload
    results["regen_acceptance_audit_report"] = report

    results["phase_16l4_acceptance_master_gate_allowed"] = status == PASS_STATUS

    return results


def _audit_item(name, passed, detail):
    return {
        "name": name,
        "passed": bool(passed),
        "detail": detail,
    }


def _candidate_id(*payloads):
    for payload in payloads:
        if isinstance(payload, dict) and payload.get("candidate_id"):
            return payload.get("candidate_id")
    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16L.3 ACCEPTANCE AUDIT",
        "===================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Audits acceptance criteria.",
        "- Audits engineering acceptance report.",
        "- Confirms acceptance evidence consistency.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Audit Summary:",
        f"- Candidate ID: {payload.get('candidate_id')}",
        f"- Audit items: {payload.get('audit_item_count')}",
        f"- Passed: {payload.get('passed_count')}",
        f"- Failed: {payload.get('failed_count')}",
        "",
        "Audit Items:",
    ])

    for item in payload.get("audit_items", []):
        lines.append(
            f"- {item.get('name')}: {LegacyCompatibilityProducer.marker_from_bool(item.get('passed'))}"
        )

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16L.4 Acceptance Master Gate.",
    ])

    return "\n".join(lines)
