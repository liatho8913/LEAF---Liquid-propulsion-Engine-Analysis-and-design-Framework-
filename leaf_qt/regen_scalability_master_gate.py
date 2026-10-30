from leaf_qt.structured_status_access import findings_highest_severity, highest_severity as gate_highest_severity, is_pass
"""
LEAF Regen Scalability Master Gate
==================================

Stage V.4 owner for final scalability gate approval.

This module does not classify engine scale.
This module does not perform raw constraint checks.
This module does not own reports.
This module does not benchmark real engines.

It approves Stage V only when the previous Stage V owners are complete:

- Stage V.0 profile owner
- Stage V.1 constraint owner / framework
- Stage V.2 report owner
- Stage V.3 failure / validation owner
"""


def attach_regen_scalability_master_gate(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_regen_scalability_master_gate(results)
    results.update(audit)
    return results


def _leaf_16t3q7_original_evaluate_regen_scalability_master_gate(results):
    results = results if isinstance(results, dict) else {}

    profile_complete = bool(
        results.get("stage_v0_regen_scalability_profile_complete", False)
    )

    constraint_complete = bool(
        results.get("stage_v1_regen_scalability_constraint_owner_complete")
        or results.get("stage_v1_regen_scalability_framework_complete")
        or False
    )

    report_complete = bool(
        results.get("stage_v2_regen_scalability_report_owner_complete")
        or results.get("stage_v2_regen_scalability_report_ownership_complete")
        or False
    )

    failure_owner_complete = bool(
        results.get("stage_v3_regen_scalability_failure_owner_complete", False)
    )

    can_proceed = bool(
        results.get(
            "regen_scalability_failure_owner_can_proceed_to_master_gate",
            False,
        )
    )

    trust_level = str(
        results.get(
            "regen_scalability_failure_owner_trust_level",
            "UNKNOWN",
        )
    ).upper()

    blocking_reasons = []

    if not profile_complete:
        blocking_reasons.append("Stage V.0 scalability profile is incomplete.")

    if not constraint_complete:
        blocking_reasons.append("Stage V.1 scalability constraint owner is incomplete.")

    if not report_complete:
        blocking_reasons.append("Stage V.2 scalability report owner is incomplete.")

    if not failure_owner_complete:
        blocking_reasons.append("Stage V.3 scalability failure owner is incomplete.")

    if not can_proceed:
        blocking_reasons.append(
            "Stage V.3 failure owner has not approved progression to master gate."
        )

    if trust_level != "TRUSTED_SCALABILITY_READY":
        blocking_reasons.append(
            f"Scalability trust level is not trusted: {trust_level}"
        )

    if blocking_reasons:
        status = "FAIL_REGEN_SCALABILITY_MASTER_GATE"
        complete = False
    else:
        status = "PASS_REGEN_SCALABILITY_MASTER_GATE"
        complete = True

    text = build_regen_scalability_master_gate_text(
        status=status,
        complete=complete,
        profile_complete=profile_complete,
        constraint_complete=constraint_complete,
        report_complete=report_complete,
        failure_owner_complete=failure_owner_complete,
        can_proceed=can_proceed,
        trust_level=trust_level,
        blocking_reasons=blocking_reasons,
        results=results,
    )

    return {
        "regen_scalability_master_gate_status": status,
        "regen_scalability_master_gate_complete": complete,
        "regen_scalability_master_gate_blocking_reasons": blocking_reasons,
        "regen_scalability_master_gate_text": text,
        "stage_v4_regen_scalability_master_gate_complete": complete,
    }


def build_regen_scalability_master_gate_text(
    status,
    complete,
    profile_complete,
    constraint_complete,
    report_complete,
    failure_owner_complete,
    can_proceed,
    trust_level,
    blocking_reasons,
    results,
):
    lines = [
        "LEAF STAGE V.4 REGEN SCALABILITY MASTER GATE",
        "=============================================",
        "",
        f"Status: {status}",
        f"Complete: {complete}",
        "",
        "Owned By:",
        "- regen_scalability_master_gate.py",
        "",
        "Scope:",
        "- Owns final Stage V scalability approval.",
        "- Does not benchmark real engines.",
        "- Does not optimise geometry.",
        "",
        "Required Stage V Chain:",
        f"- Stage V.0 profile complete: {profile_complete}",
        f"- Stage V.1 constraint owner complete: {constraint_complete}",
        f"- Stage V.2 report owner complete: {report_complete}",
        f"- Stage V.3 failure owner complete: {failure_owner_complete}",
        f"- Stage V.3 can proceed to master gate: {can_proceed}",
        f"- Stage V.3 trust level: {trust_level}",
        "",
        "Blocking Reasons:",
    ]

    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Upstream Evidence:")
    lines.append(
        f"- Profile status: {results.get('regen_scalability_profile_status', 'N/A')}"
    )
    lines.append(
        f"- Constraint status: {results.get('regen_scalability_constraint_owner_status', results.get('regen_scalability_framework_status', 'N/A'))}"
    )
    lines.append(
        f"- Report owner status: {results.get('regen_scalability_report_owner_status', 'N/A')}"
    )
    lines.append(
        f"- Failure owner status: {results.get('regen_scalability_failure_owner_status', 'N/A')}"
    )

    lines.append("")
    lines.append("Rule:")
    lines.append("- Stage V.4 passes only when V.0–V.3 are complete and trusted.")
    lines.append("- Warning-level scalability cases must not pass master gate.")
    lines.append("- Stage W benchmarking is downstream and separate.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PHASE 16T.3Q.7 — WAVE 2 STATUS ADAPTER
# REGEN SCALABILITY MASTER GATE
# ---------------------------------------------------------------------------

PHASE_16T3Q7_STATUS_ADAPTER_COMPLETE = True
PHASE_16T3Q7_STATUS_ADAPTER_STATUS = (
    "PASS_REGEN_SCALABILITY_STATUS_ADAPTER_PHASE_16T3Q7"
)


def _leaf_16t3q7_make_finding(code, severity, message, evidence=None):
    return {
        "code": str(code),
        "severity": str(severity).upper(),
        "message": str(message),
        "evidence": evidence or {},
        "phase": "16T.3Q.7",
        "owner": "regen_scalability_master_gate",
    }


def _leaf_16t3q7_get_first(payload, keys, default=None):
    if not isinstance(payload, dict):
        return default
    for key in keys:
        if key in payload:
            return payload.get(key)
    return default


def _leaf_16t3q7_canonical_status_from_findings(findings, ready):
    severities = {str(f.get("severity", "")).upper() for f in findings}

    if gate_highest_severity(severities) == "FAIL":
        return "FAIL"
    if "BLOCKED" in severities:
        return "BLOCKED"
    if "REVIEW_REQUIRED" in severities:
        return "REVIEW_REQUIRED"
    if ready is True:
        return "PASS"
    return "FAIL"


def _leaf_16t3q7_classify_scalability_findings(payload):
    findings = []

    if not isinstance(payload, dict):
        return [
            _leaf_16t3q7_make_finding(
                "SCALABILITY_MASTER_GATE_PAYLOAD_INVALID",
                "FAIL",
                "Scalability master gate did not return a dictionary payload.",
                {"payload_type": type(payload).__name__},
            )
        ]

    ready = bool(
        _leaf_16t3q7_get_first(
            payload,
            [
                "regen_scalability_master_gate_ready",
                "regen_scalability_ready",
                "ready",
            ],
            False,
        )
    )

    legacy_status = str(
        _leaf_16t3q7_get_first(
            payload,
            [
                "regen_scalability_master_gate_status",
                "regen_scalability_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    failed_checks = _leaf_16t3q7_get_first(
        payload,
        [
            "regen_scalability_master_gate_failed_checks",
            "regen_scalability_failed_checks",
            "failed_checks",
        ],
        [],
    )

    checks = _leaf_16t3q7_get_first(
        payload,
        [
            "regen_scalability_master_gate_checks",
            "regen_scalability_checks",
            "checks",
        ],
        [],
    )

    if ready:
        findings.append(
            _leaf_16t3q7_make_finding(
                "SCALABILITY_MASTER_GATE_READY",
                "INFO",
                "Regen scalability master gate reports ready.",
                {"legacy_status": legacy_status},
            )
        )
    else:
        severity = "FAIL" if "FAIL" in legacy_status.upper() else "REVIEW_REQUIRED"
        findings.append(
            _leaf_16t3q7_make_finding(
                "SCALABILITY_MASTER_GATE_NOT_READY",
                severity,
                "Regen scalability master gate does not report ready.",
                {"legacy_status": legacy_status},
            )
        )

    if isinstance(failed_checks, list) and failed_checks:
        for index, check in enumerate(failed_checks):
            findings.append(
                _leaf_16t3q7_make_finding(
                    f"FAILED_SCALABILITY_CHECK_{index}",
                    "FAIL",
                    "Regen scalability master gate contains a failed check.",
                    {"check": check},
                )
            )
    elif isinstance(failed_checks, list):
        findings.append(
            _leaf_16t3q7_make_finding(
                "NO_FAILED_SCALABILITY_CHECKS",
                "INFO",
                "No failed regen scalability checks were reported.",
                {},
            )
        )
    else:
        findings.append(
            _leaf_16t3q7_make_finding(
                "FAILED_SCALABILITY_CHECKS_PAYLOAD_INVALID",
                "REVIEW_REQUIRED",
                "Failed-check payload is not a list.",
                {"failed_checks_type": type(failed_checks).__name__},
            )
        )

    if isinstance(checks, list) and checks:
        findings.append(
            _leaf_16t3q7_make_finding(
                "SCALABILITY_CHECKS_PRESENT",
                "INFO",
                "Regen scalability master gate checks are present.",
                {"check_count": len(checks)},
            )
        )
    else:
        findings.append(
            _leaf_16t3q7_make_finding(
                "SCALABILITY_CHECKS_MISSING",
                "REVIEW_REQUIRED",
                "Regen scalability master gate checks are missing or empty.",
                {"checks_type": type(checks).__name__},
            )
        )

    return findings


def _leaf_16t3q7_build_global_status_payload(canonical_status, legacy_status, findings, ready):
    severity_counts = {}
    for finding in findings:
        severity = str(finding.get("severity", "UNKNOWN")).upper()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "owner": "regen_scalability_master_gate",
        "phase": "16T.3Q.7",
        "canonical_status": canonical_status,
        "global_status": canonical_status,
        "legacy_status": legacy_status,
        "ready": bool(ready),
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "findings": findings,
        "adapter": "wave_2_status_adapter",
        "adapter_phase": "16T.3Q.7",
    }


def _leaf_16t3q7_build_adapter_report(canonical_status, legacy_status, findings):
    lines = [
        "LEAF PHASE 16T.3Q.7 STATUS ADAPTER",
        "====================================",
        "",
        "Owner: regen_scalability_master_gate",
        "Target: Regen Scalability Master Gate",
        f"Canonical Status: {canonical_status}",
        f"Legacy Status: {legacy_status}",
        f"Structured Findings: {len(findings)}",
        "",
        "Findings:",
    ]

    for finding in findings:
        lines.append(
            f"- [{finding.get('severity')}] {finding.get('code')}: {finding.get('message')}"
        )

    lines.extend([
        "",
        "Compatibility:",
        "- Existing public function name is preserved.",
        "- Existing payload fields are preserved.",
        "- Existing legacy status strings are preserved.",
        "- Structured status fields are additive only.",
    ])

    return "\n".join(lines)


def evaluate_regen_scalability_master_gate(*args, **kwargs):
    payload = _leaf_16t3q7_original_evaluate_regen_scalability_master_gate(
        *args,
        **kwargs,
    )

    ready = bool(
        _leaf_16t3q7_get_first(
            payload,
            ["regen_scalability_master_gate_ready", "regen_scalability_ready", "ready"],
            False,
        )
    )

    legacy_status = str(
        _leaf_16t3q7_get_first(
            payload,
            ["regen_scalability_master_gate_status", "regen_scalability_status", "status"],
            "UNKNOWN",
        )
    )

    findings = _leaf_16t3q7_classify_scalability_findings(payload)
    canonical_status = _leaf_16t3q7_canonical_status_from_findings(findings, ready)

    global_status_payload = _leaf_16t3q7_build_global_status_payload(
        canonical_status,
        legacy_status,
        findings,
        ready,
    )

    adapter_report = _leaf_16t3q7_build_adapter_report(
        canonical_status,
        legacy_status,
        findings,
    )

    if not isinstance(payload, dict):
        payload = {}

    payload.update({
        "phase_16t3q7_status_adapter_complete": True,
        "phase_16t3q7_regen_scalability_status_adapter_complete": True,
        "regen_scalability_status_adapter_complete": True,
        "regen_scalability_status_adapter_status": PHASE_16T3Q7_STATUS_ADAPTER_STATUS,
        "regen_scalability_master_gate_structured_findings": findings,
        "regen_scalability_master_gate_global_status": canonical_status,
        "regen_scalability_master_gate_global_status_payload": global_status_payload,
        "regen_scalability_master_gate_adapter_report": adapter_report,
        "regen_scalability_master_gate_legacy_status": legacy_status,
        "structured_findings": findings,
        "global_status": canonical_status,
        "global_status_payload": global_status_payload,
        "adapter_report": adapter_report,
    })

    return payload


