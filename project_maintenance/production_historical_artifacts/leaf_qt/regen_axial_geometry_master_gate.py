from leaf_qt.structured_status_access import findings_highest_severity, highest_severity as gate_highest_severity, is_pass
try:
    from project_maintenance.production_historical_artifacts.leaf_qt.regen_axial_geometry_completion_audit import (
        run_regen_axial_geometry_completion_audit,
        flatten_regen_axial_completion_audit_result,
    )
except Exception:
    from project_maintenance.production_historical_artifacts.leaf_qt.regen_axial_geometry_completion_audit import (
        run_regen_axial_geometry_completion_audit,
        flatten_regen_axial_completion_audit_result,
    )


PASS_STATUS = "PASS_REGEN_AXIAL_GEOMETRY_MASTER_GATE"
FAIL_STATUS = "FAIL_REGEN_AXIAL_GEOMETRY_MASTER_GATE"


def _leaf_16t3q10_original_run_regen_axial_geometry_master_gate():
    errors = []
    warnings = []

    completion_result = run_regen_axial_geometry_completion_audit()

    if not completion_result.get("regen_axial_completion_audit_pass", False):
        errors.append("Axial completion audit did not pass.")

    validation_result = completion_result.get("validation_result") or {}

    if not validation_result.get("regen_axial_validation_owner_pass", False):
        errors.append("Axial validation owner did not pass.")

    solver_result = validation_result.get("axial_solver_result") or {}
    constraint_result = validation_result.get("axial_constraint_result") or {}
    report_result = validation_result.get("axial_report_result") or {}

    if not solver_result.get("axial_geometry_solver_pass", False):
        errors.append("Axial solver owner did not pass.")

    if not constraint_result.get("regen_axial_constraint_owner_pass", False):
        errors.append("Axial constraint owner did not pass.")

    if not report_result.get("regen_axial_report_owner_pass", False):
        errors.append("Axial report owner did not pass.")

    warnings.extend(validation_result.get("warnings", []))
    warnings.extend(completion_result.get("errors", []))

    gate_pass = len(errors) == 0

    return {
        "regen_axial_master_gate_status": PASS_STATUS if gate_pass else FAIL_STATUS,
        "regen_axial_master_gate_pass": gate_pass,
        "phase_2_architecturally_complete": gate_pass,
        "phase_3_variable_geometry_allowed": gate_pass,
        "completion_result": completion_result,
        "errors": errors,
        "warnings": warnings,
        "master_gate_statement": (
            "REGEN GEOMETRY PHASE 2 ACCEPTED FOR FUTURE VARIABLE-GEOMETRY DEVELOPMENT"
            if gate_pass
            else "REGEN GEOMETRY PHASE 2 BLOCKED FROM FUTURE VARIABLE-GEOMETRY DEVELOPMENT"
        ),
    }


def flatten_regen_axial_master_gate_result(result, prefix="recommended"):
    flat = {
        f"{prefix}_regen_axial_master_gate_status": result.get(
            "regen_axial_master_gate_status"
        ),
        f"{prefix}_regen_axial_master_gate_pass": (
            1.0 if result.get("regen_axial_master_gate_pass") else 0.0
        ),
        f"{prefix}_regen_axial_phase_2_architecturally_complete": (
            1.0 if result.get("phase_2_architecturally_complete") else 0.0
        ),
        f"{prefix}_regen_axial_phase_3_variable_geometry_allowed": (
            1.0 if result.get("phase_3_variable_geometry_allowed") else 0.0
        ),
        f"{prefix}_regen_axial_master_gate_error_count": float(
            len(result.get("errors", []))
        ),
        f"{prefix}_regen_axial_master_gate_warning_count": float(
            len(result.get("warnings", []))
        ),
        f"{prefix}_regen_axial_master_gate_statement": result.get(
            "master_gate_statement"
        ),
    }

    flat.update(
        flatten_regen_axial_completion_audit_result(
            result.get("completion_result", {}),
            prefix=prefix,
        )
    )

    return flat


# ---------------------------------------------------------------------------
# PHASE 16T.3Q.10 — WAVE 2 STATUS ADAPTER
# REGEN AXIAL GEOMETRY MASTER GATE
# ---------------------------------------------------------------------------

PHASE_16T3Q10_STATUS_ADAPTER_COMPLETE = True
PHASE_16T3Q10_STATUS_ADAPTER_STATUS = (
    "PASS_REGEN_AXIAL_GEOMETRY_STATUS_ADAPTER_PHASE_16T3Q10"
)


def _leaf_16t3q10_make_finding(code, severity, message, evidence=None):
    return {
        "code": str(code),
        "severity": str(severity).upper(),
        "message": str(message),
        "evidence": evidence or {},
        "phase": "16T.3Q.10",
        "owner": "regen_axial_geometry_master_gate",
    }


def _leaf_16t3q10_get_first(payload, keys, default=None):
    if not isinstance(payload, dict):
        return default

    for key in keys:
        if key in payload:
            return payload.get(key)

    return default


def _leaf_16t3q10_canonical_status_from_findings(findings, ready):
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


def _leaf_16t3q10_classify_axial_geometry_findings(payload):
    findings = []

    if not isinstance(payload, dict):
        return [
            _leaf_16t3q10_make_finding(
                "AXIAL_GEOMETRY_MASTER_GATE_PAYLOAD_INVALID",
                "FAIL",
                "Axial geometry master gate did not return a dictionary payload.",
                {"payload_type": type(payload).__name__},
            )
        ]

    complete = bool(
        _leaf_16t3q10_get_first(
            payload,
            [
                "regen_axial_geometry_master_gate_complete",
                "recommended_regen_axial_geometry_master_gate_complete",
                "axial_geometry_master_gate_complete",
                "complete",
            ],
            False,
        )
    )

    status = str(
        _leaf_16t3q10_get_first(
            payload,
            [
                "regen_axial_geometry_master_gate_status",
                "recommended_regen_axial_geometry_master_gate_status",
                "axial_geometry_master_gate_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    failed_checks = _leaf_16t3q10_get_first(
        payload,
        [
            "regen_axial_geometry_master_gate_failed_checks",
            "recommended_regen_axial_geometry_master_gate_failed_checks",
            "axial_geometry_master_gate_failed_checks",
            "failed_checks",
        ],
        [],
    )

    checks = _leaf_16t3q10_get_first(
        payload,
        [
            "regen_axial_geometry_master_gate_checks",
            "recommended_regen_axial_geometry_master_gate_checks",
            "axial_geometry_master_gate_checks",
            "checks",
        ],
        [],
    )

    if complete:
        findings.append(
            _leaf_16t3q10_make_finding(
                "AXIAL_GEOMETRY_MASTER_GATE_COMPLETE",
                "INFO",
                "Axial geometry master gate reports complete.",
                {"legacy_status": status},
            )
        )
    else:
        severity = "FAIL" if "FAIL" in status.upper() else "REVIEW_REQUIRED"
        findings.append(
            _leaf_16t3q10_make_finding(
                "AXIAL_GEOMETRY_MASTER_GATE_INCOMPLETE",
                severity,
                "Axial geometry master gate does not report complete.",
                {"legacy_status": status},
            )
        )

    if isinstance(failed_checks, list) and failed_checks:
        for index, check in enumerate(failed_checks):
            findings.append(
                _leaf_16t3q10_make_finding(
                    f"FAILED_AXIAL_GEOMETRY_CHECK_{index}",
                    "FAIL",
                    "Axial geometry master gate contains a failed check.",
                    {"check": check},
                )
            )
    elif isinstance(failed_checks, list):
        findings.append(
            _leaf_16t3q10_make_finding(
                "NO_FAILED_AXIAL_GEOMETRY_CHECKS",
                "INFO",
                "No failed axial geometry checks were reported.",
                {},
            )
        )
    else:
        findings.append(
            _leaf_16t3q10_make_finding(
                "FAILED_AXIAL_GEOMETRY_CHECKS_PAYLOAD_INVALID",
                "REVIEW_REQUIRED",
                "Failed-check payload is not a list.",
                {"failed_checks_type": type(failed_checks).__name__},
            )
        )

    if isinstance(checks, list) and checks:
        findings.append(
            _leaf_16t3q10_make_finding(
                "AXIAL_GEOMETRY_CHECKS_PRESENT",
                "INFO",
                "Axial geometry master gate checks are present.",
                {"check_count": len(checks)},
            )
        )
    else:
        findings.append(
            _leaf_16t3q10_make_finding(
                "AXIAL_GEOMETRY_CHECKS_MISSING",
                "REVIEW_REQUIRED",
                "Axial geometry master gate checks are missing or empty.",
                {"checks_type": type(checks).__name__},
            )
        )

    report = _leaf_16t3q10_get_first(
        payload,
        [
            "regen_axial_geometry_master_gate_report",
            "recommended_regen_axial_geometry_master_gate_report",
            "axial_geometry_master_gate_report",
            "report",
        ],
        None,
    )

    text = _leaf_16t3q10_get_first(
        payload,
        [
            "regen_axial_geometry_master_gate_text",
            "recommended_regen_axial_geometry_master_gate_text",
            "axial_geometry_master_gate_text",
            "text",
        ],
        None,
    )

    if isinstance(report, str) and report.strip():
        findings.append(
            _leaf_16t3q10_make_finding(
                "AXIAL_GEOMETRY_REPORT_PRESENT",
                "INFO",
                "Axial geometry report payload is present.",
                {"report_length": len(report)},
            )
        )
    elif isinstance(text, str) and text.strip():
        findings.append(
            _leaf_16t3q10_make_finding(
                "AXIAL_GEOMETRY_TEXT_PRESENT",
                "INFO",
                "Axial geometry text payload is present.",
                {"text_length": len(text)},
            )
        )
    else:
        findings.append(
            _leaf_16t3q10_make_finding(
                "AXIAL_GEOMETRY_REPORT_MISSING",
                "REVIEW_REQUIRED",
                "Axial geometry report/text payload is missing.",
                {},
            )
        )

    return findings


def _leaf_16t3q10_build_global_status_payload(
    canonical_status,
    legacy_status,
    findings,
    ready,
):
    severity_counts = {}

    for finding in findings:
        severity = str(finding.get("severity", "UNKNOWN")).upper()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "owner": "regen_axial_geometry_master_gate",
        "phase": "16T.3Q.10",
        "canonical_status": canonical_status,
        "global_status": canonical_status,
        "legacy_status": legacy_status,
        "ready": bool(ready),
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "findings": findings,
        "adapter": "wave_2_status_adapter",
        "adapter_phase": "16T.3Q.10",
    }


def _leaf_16t3q10_build_adapter_report(
    canonical_status,
    legacy_status,
    findings,
):
    lines = [
        "LEAF PHASE 16T.3Q.10 STATUS ADAPTER",
        "=====================================",
        "",
        "Owner: regen_axial_geometry_master_gate",
        "Target: Regen Axial Geometry Master Gate",
        f"Canonical Status: {canonical_status}",
        f"Legacy Status: {legacy_status}",
        f"Structured Findings: {len(findings)}",
        "",
        "Findings:",
    ]

    if findings:
        for finding in findings:
            lines.append(
                f"- [{finding.get('severity')}] "
                f"{finding.get('code')}: {finding.get('message')}"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "Compatibility:",
            "- Existing public function name is preserved.",
            "- Existing payload fields are preserved.",
            "- Existing legacy status strings are preserved.",
            "- flatten_regen_axial_master_gate_result remains compatible.",
        ]
    )

    return "\n".join(lines)


def run_regen_axial_geometry_master_gate(*args, **kwargs):
    payload = _leaf_16t3q10_original_run_regen_axial_geometry_master_gate(
        *args,
        **kwargs,
    )

    if not isinstance(payload, dict):
        findings = _leaf_16t3q10_classify_axial_geometry_findings(payload)
        canonical_status = "FAIL"
        legacy_status = "UNKNOWN"
        ready = False

        global_status_payload = _leaf_16t3q10_build_global_status_payload(
            canonical_status=canonical_status,
            legacy_status=legacy_status,
            findings=findings,
            ready=ready,
        )

        adapter_report = _leaf_16t3q10_build_adapter_report(
            canonical_status=canonical_status,
            legacy_status=legacy_status,
            findings=findings,
        )

        return {
            "phase_16t3q10_status_adapter_complete": True,
            "phase_16t3q10_regen_axial_geometry_status_adapter_complete": True,
            "regen_axial_geometry_status_adapter_complete": True,
            "regen_axial_geometry_status_adapter_status": (
                PHASE_16T3Q10_STATUS_ADAPTER_STATUS
            ),
            "regen_axial_geometry_master_gate_structured_findings": findings,
            "regen_axial_geometry_master_gate_global_status": canonical_status,
            "regen_axial_geometry_master_gate_global_status_payload": global_status_payload,
            "regen_axial_geometry_master_gate_adapter_report": adapter_report,
            "regen_axial_geometry_master_gate_legacy_status": legacy_status,
            "structured_findings": findings,
            "global_status": canonical_status,
            "global_status_payload": global_status_payload,
            "adapter_report": adapter_report,
        }

    ready = bool(
        _leaf_16t3q10_get_first(
            payload,
            [
                "regen_axial_geometry_master_gate_complete",
                "recommended_regen_axial_geometry_master_gate_complete",
                "axial_geometry_master_gate_complete",
                "complete",
            ],
            False,
        )
    )

    legacy_status = str(
        _leaf_16t3q10_get_first(
            payload,
            [
                "regen_axial_geometry_master_gate_status",
                "recommended_regen_axial_geometry_master_gate_status",
                "axial_geometry_master_gate_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    findings = _leaf_16t3q10_classify_axial_geometry_findings(payload)
    canonical_status = _leaf_16t3q10_canonical_status_from_findings(
        findings=findings,
        ready=ready,
    )

    global_status_payload = _leaf_16t3q10_build_global_status_payload(
        canonical_status=canonical_status,
        legacy_status=legacy_status,
        findings=findings,
        ready=ready,
    )

    adapter_report = _leaf_16t3q10_build_adapter_report(
        canonical_status=canonical_status,
        legacy_status=legacy_status,
        findings=findings,
    )

    payload.update(
        {
            "phase_16t3q10_status_adapter_complete": True,
            "phase_16t3q10_regen_axial_geometry_status_adapter_complete": True,
            "regen_axial_geometry_status_adapter_complete": True,
            "regen_axial_geometry_status_adapter_status": (
                PHASE_16T3Q10_STATUS_ADAPTER_STATUS
            ),
            "regen_axial_geometry_master_gate_structured_findings": findings,
            "regen_axial_geometry_master_gate_global_status": canonical_status,
            "regen_axial_geometry_master_gate_global_status_payload": global_status_payload,
            "regen_axial_geometry_master_gate_adapter_report": adapter_report,
            "regen_axial_geometry_master_gate_legacy_status": legacy_status,
            "structured_findings": findings,
            "global_status": canonical_status,
            "global_status_payload": global_status_payload,
            "adapter_report": adapter_report,
        }
    )

    return payload


