from leaf_qt.structured_status_access import highest_severity as solver_highest_severity, is_pass
try:
    from leaf_qt.material_database import (
        PLACEHOLDER_MODE,
        PARTIAL_SOURCE_MODE,
        SOURCED_VALIDATION_MODE,
        INSUFFICIENT_SOURCE_MODE,
    )
except Exception:
    PLACEHOLDER_MODE = "PLACEHOLDER_MODE"
    PARTIAL_SOURCE_MODE = "PARTIAL_SOURCE_MODE"
    SOURCED_VALIDATION_MODE = "SOURCED_VALIDATION_MODE"
    INSUFFICIENT_SOURCE_MODE = "INSUFFICIENT_SOURCE_MODE"


BLOCKING_MODES = {
    PLACEHOLDER_MODE,
    INSUFFICIENT_SOURCE_MODE,
}

ACCEPTED_MODES = {
    SOURCED_VALIDATION_MODE,
}

WARNING_MODES = {
    PARTIAL_SOURCE_MODE,
}


def attach_regen_source_validation_gate(results):
    if not isinstance(results, dict):
        return results

    audit = audit_regen_source_validation(results)

    for key, value in audit.items():
        results[key] = value

    _apply_conservative_regen_gating(results)

    return results


def _leaf_16t3q9_original_audit_regen_source_validation(results):
    material_mode = _first_available(
        results,
        (
            "material_source_validation_mode",
            "source_validation_mode",
            "material_validation_mode",
        ),
    )

    coating_mode = _first_available(
        results,
        (
            "coating_source_validation_mode",
            "coating_validation_mode",
        ),
    )

    material_score = _first_available(
        results,
        (
            "material_source_validation_score",
            "source_validation_score",
        ),
        default=0,
    )

    coating_score = _first_available(
        results,
        (
            "coating_source_validation_score",
        ),
        default=0,
    )

    material_placeholder = _truthy(
        _first_available(
            results,
            (
                "material_source_is_placeholder",
                "source_is_placeholder",
            ),
            default=False,
        )
    )

    coating_placeholder = _truthy(
        _first_available(
            results,
            (
                "coating_source_is_placeholder",
            ),
            default=False,
        )
    )

    blocking_reasons = []
    warning_reasons = []

    _audit_source(
        label="Material",
        mode=material_mode,
        score=material_score,
        placeholder=material_placeholder,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
    )

    if coating_mode not in (None, "", "NONE", "N/A"):
        _audit_source(
            label="Coating",
            mode=coating_mode,
            score=coating_score,
            placeholder=coating_placeholder,
            blocking_reasons=blocking_reasons,
            warning_reasons=warning_reasons,
        )

    if blocking_reasons:
        status = "FAIL_SOURCE_VALIDATION_BLOCKED"
        pass_allowed = False
    elif warning_reasons:
        status = "WARN_PARTIAL_SOURCE_VALIDATION"
        pass_allowed = False
    else:
        status = "PASS_SOURCED_VALIDATION"
        pass_allowed = True

    text = build_regen_source_validation_gate_text(
        status=status,
        pass_allowed=pass_allowed,
        material_mode=material_mode,
        coating_mode=coating_mode,
        material_score=material_score,
        coating_score=coating_score,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
    )

    return {
        "regen_source_validation_gate_status": status,
        "regen_source_validation_pass_allowed": pass_allowed,
        "regen_source_validation_material_mode": material_mode or "UNKNOWN",
        "regen_source_validation_coating_mode": coating_mode or "NONE",
        "regen_source_validation_material_score": material_score,
        "regen_source_validation_coating_score": coating_score,
        "regen_source_validation_blocking_reasons": blocking_reasons,
        "regen_source_validation_warning_reasons": warning_reasons,
        "regen_source_validation_text": text,
    }


def _audit_source(
        label,
        mode,
        score,
        placeholder,
        blocking_reasons,
        warning_reasons,
):
    mode = str(mode or "").strip()

    if not mode:
        blocking_reasons.append(f"{label} source validation mode is missing.")
        return

    if placeholder:
        blocking_reasons.append(
            f"{label} data is marked as placeholder and cannot produce PASS."
        )

    if mode in BLOCKING_MODES:
        blocking_reasons.append(
            f"{label} source validation mode is {mode}; regen validation must be blocked."
        )
        return

    if mode in WARNING_MODES:
        warning_reasons.append(
            f"{label} source validation mode is {mode}; partial source data cannot produce final PASS."
        )
        return

    if mode not in ACCEPTED_MODES:
        blocking_reasons.append(
            f"{label} source validation mode is unknown or unsupported: {mode}."
        )
        return

    try:
        score = float(score)
    except Exception:
        score = 0.0

    if score < 85.0:
        warning_reasons.append(
            f"{label} is sourced but source score is below full validation threshold: {score}."
        )


def _apply_conservative_regen_gating(results):
    pass_allowed = bool(results.get("regen_source_validation_pass_allowed"))

    if pass_allowed:
        results["regen_conservative_validation_gate_status"] = "PASS_ALLOWED"
        results["regen_conservative_validation_gate_reason"] = (
            "Material/coating source validation is sufficient for sourced validation."
        )
        return

    reason = "; ".join(
        str(item)
        for item in results.get("regen_source_validation_blocking_reasons", [])
    )

    if not reason:
        reason = "; ".join(
            str(item)
            for item in results.get("regen_source_validation_warning_reasons", [])
        )

    if not reason:
        reason = "Regen source validation did not explicitly allow PASS."

    results["regen_conservative_validation_gate_status"] = "PASS_BLOCKED"
    results["regen_conservative_validation_gate_reason"] = reason

    for key in (
        "full_engine_regen_geometry_pass",
        "best_full_engine_regen_pass",
        "regen_validation_pass",
    ):
        if key in results:
            results[key] = 0

    for key in (
        "full_engine_regen_geometry_status",
        "best_full_engine_regen_status",
        "regen_validation_status",
    ):
        if key in results and is_pass(results.get(key)):
            results[key] = "BLOCKED_BY_SOURCE_VALIDATION"

    reasons = results.get("full_engine_regen_geometry_reasons")

    if isinstance(reasons, list):
        reasons.append("PASS blocked by regen source validation gate: " + reason)


def _first_available(results, keys, default=None):
    for key in keys:
        value = results.get(key)

        if value not in (None, ""):
            return value

    return default


def _truthy(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value != 0

    text = str(value).strip().lower()

    return text in {"1", "true", "yes", "y", "placeholder"}


def build_regen_source_validation_gate_text(
        status,
        pass_allowed,
        material_mode,
        coating_mode,
        material_score,
        coating_score,
        blocking_reasons,
        warning_reasons,
):
    lines = [
        "LEAF REGEN SOURCE VALIDATION GATE",
        "=================================",
        "",
        f"Status: {status}",
        f"PASS allowed: {pass_allowed}",
        "",
        "Source Modes:",
        f"- Material mode: {material_mode or 'UNKNOWN'}",
        f"- Coating mode: {coating_mode or 'NONE'}",
        "",
        "Source Scores:",
        f"- Material score: {material_score}",
        f"- Coating score: {coating_score}",
        "",
        "Blocking Reasons:",
    ]

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Warning Reasons:")

    if warning_reasons:
        for reason in warning_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Conservative Rule:")
    lines.append("- PLACEHOLDER_MODE can never produce PASS.")
    lines.append("- INSUFFICIENT_SOURCE_MODE can never produce PASS.")
    lines.append("- PARTIAL_SOURCE_MODE may support review, but cannot produce final PASS.")
    lines.append("- SOURCED_VALIDATION_MODE is required for final validation PASS.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# PHASE 16T.3Q.9 — WAVE 2 STATUS ADAPTER
# REGEN SOURCE VALIDATION GATE
# ---------------------------------------------------------------------------

PHASE_16T3Q9_STATUS_ADAPTER_COMPLETE = True
PHASE_16T3Q9_STATUS_ADAPTER_STATUS = (
    "PASS_REGEN_SOURCE_VALIDATION_GATE_STATUS_ADAPTER_PHASE_16T3Q9"
)


def _leaf_16t3q9_make_finding(code, severity, message, evidence=None):
    return {
        "code": str(code),
        "severity": str(severity).upper(),
        "message": str(message),
        "evidence": evidence or {},
        "phase": "16T.3Q.9",
        "owner": "regen_source_validation_gate",
    }


def _leaf_16t3q9_get_first(payload, keys, default=None):
    if not isinstance(payload, dict):
        return default
    for key in keys:
        if key in payload:
            return payload.get(key)
    return default


def _leaf_16t3q9_canonical_status_from_findings(findings, ready):
    severities = {str(f.get("severity", "")).upper() for f in findings}
    if solver_highest_severity(severities) == "FAIL":
        return "FAIL"
    if "BLOCKED" in severities:
        return "BLOCKED"
    if "REVIEW_REQUIRED" in severities:
        return "REVIEW_REQUIRED"
    if ready is True:
        return "PASS"
    return "FAIL"


def _leaf_16t3q9_classify_source_validation_findings(payload):
    findings = []

    if not isinstance(payload, dict):
        return [
            _leaf_16t3q9_make_finding(
                "SOURCE_VALIDATION_GATE_PAYLOAD_INVALID",
                "FAIL",
                "Source validation gate did not return a dictionary payload.",
                {"payload_type": type(payload).__name__},
            )
        ]

    pass_allowed = bool(
        _leaf_16t3q9_get_first(
            payload,
            [
                "regen_source_validation_pass_allowed",
                "source_validation_pass_allowed",
                "pass_allowed",
            ],
            False,
        )
    )

    status = str(
        _leaf_16t3q9_get_first(
            payload,
            [
                "regen_source_validation_gate_status",
                "regen_source_validation_status",
                "source_validation_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    blocking_reasons = _leaf_16t3q9_get_first(
        payload,
        [
            "regen_source_validation_blocking_reasons",
            "source_validation_blocking_reasons",
            "blocking_reasons",
        ],
        [],
    )

    warning_reasons = _leaf_16t3q9_get_first(
        payload,
        [
            "regen_source_validation_warning_reasons",
            "source_validation_warning_reasons",
            "warning_reasons",
        ],
        [],
    )

    if pass_allowed:
        findings.append(
            _leaf_16t3q9_make_finding(
                "SOURCE_VALIDATION_PASS_ALLOWED",
                "INFO",
                "Source validation gate allows pass.",
                {"legacy_status": status},
            )
        )
    else:
        severity = "FAIL" if "FAIL" in status.upper() else "BLOCKED"
        findings.append(
            _leaf_16t3q9_make_finding(
                "SOURCE_VALIDATION_PASS_BLOCKED",
                severity,
                "Source validation gate blocks pass.",
                {"legacy_status": status},
            )
        )

    if isinstance(blocking_reasons, list) and blocking_reasons:
        for index, reason in enumerate(blocking_reasons):
            findings.append(
                _leaf_16t3q9_make_finding(
                    f"SOURCE_VALIDATION_BLOCKING_REASON_{index}",
                    "BLOCKED",
                    "Source validation gate reports a blocking reason.",
                    {"reason": reason},
                )
            )
    elif isinstance(blocking_reasons, list):
        findings.append(
            _leaf_16t3q9_make_finding(
                "SOURCE_VALIDATION_NO_BLOCKING_REASONS",
                "INFO",
                "No source validation blocking reasons were reported.",
                {},
            )
        )
    else:
        findings.append(
            _leaf_16t3q9_make_finding(
                "SOURCE_VALIDATION_BLOCKING_REASONS_INVALID",
                "REVIEW_REQUIRED",
                "Source validation blocking reasons payload is not a list.",
                {"blocking_reasons_type": type(blocking_reasons).__name__},
            )
        )

    if isinstance(warning_reasons, list) and warning_reasons:
        for index, reason in enumerate(warning_reasons):
            findings.append(
                _leaf_16t3q9_make_finding(
                    f"SOURCE_VALIDATION_WARNING_REASON_{index}",
                    "REVIEW_REQUIRED",
                    "Source validation gate reports a warning reason.",
                    {"reason": reason},
                )
            )
    elif isinstance(warning_reasons, list):
        findings.append(
            _leaf_16t3q9_make_finding(
                "SOURCE_VALIDATION_NO_WARNING_REASONS",
                "INFO",
                "No source validation warning reasons were reported.",
                {},
            )
        )
    else:
        findings.append(
            _leaf_16t3q9_make_finding(
                "SOURCE_VALIDATION_WARNING_REASONS_INVALID",
                "REVIEW_REQUIRED",
                "Source validation warning reasons payload is not a list.",
                {"warning_reasons_type": type(warning_reasons).__name__},
            )
        )

    for label, keys in {
        "MATERIAL_MODE": [
            "regen_material_source_validation_mode",
            "material_source_validation_mode",
            "material_mode",
        ],
        "COATING_MODE": [
            "regen_coating_source_validation_mode",
            "coating_source_validation_mode",
            "coating_mode",
        ],
    }.items():
        mode = _leaf_16t3q9_get_first(payload, keys, None)
        text = str(mode).upper() if mode is not None else ""

        if not text:
            findings.append(
                _leaf_16t3q9_make_finding(
                    f"{label}_MISSING",
                    "REVIEW_REQUIRED",
                    f"{label} is missing.",
                    {label.lower(): mode},
                )
            )
        elif "PLACEHOLDER" in text:
            findings.append(
                _leaf_16t3q9_make_finding(
                    f"{label}_PLACEHOLDER",
                    "BLOCKED",
                    f"{label} is placeholder-only and cannot produce pass.",
                    {label.lower(): mode},
                )
            )
        elif "PARTIAL" in text:
            findings.append(
                _leaf_16t3q9_make_finding(
                    f"{label}_PARTIAL",
                    "REVIEW_REQUIRED",
                    f"{label} is partially sourced.",
                    {label.lower(): mode},
                )
            )
        else:
            findings.append(
                _leaf_16t3q9_make_finding(
                    f"{label}_SOURCED",
                    "INFO",
                    f"{label} is sourced.",
                    {label.lower(): mode},
                )
            )

    return findings


def _leaf_16t3q9_build_global_status_payload(canonical_status, legacy_status, findings, ready):
    severity_counts = {}
    for finding in findings:
        severity = str(finding.get("severity", "UNKNOWN")).upper()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    return {
        "owner": "regen_source_validation_gate",
        "phase": "16T.3Q.9",
        "canonical_status": canonical_status,
        "global_status": canonical_status,
        "legacy_status": legacy_status,
        "ready": bool(ready),
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "findings": findings,
        "adapter": "wave_2_status_adapter",
        "adapter_phase": "16T.3Q.9",
    }


def _leaf_16t3q9_build_adapter_report(canonical_status, legacy_status, findings):
    lines = [
        "LEAF PHASE 16T.3Q.9 STATUS ADAPTER",
        "====================================",
        "",
        "Owner: regen_source_validation_gate",
        "Target: Regen Source Validation Gate",
        f"Canonical Status: {canonical_status}",
        f"Legacy Status: {legacy_status}",
        f"Structured Findings: {len(findings)}",
        "",
        "Findings:",
    ]

    if findings:
        for finding in findings:
            lines.append(
                f"- [{finding.get('severity')}] {finding.get('code')}: {finding.get('message')}"
            )
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Compatibility:",
        "- Existing public function name is preserved.",
        "- Existing payload fields are preserved.",
        "- Existing legacy status strings are preserved.",
        "- Conservative source gating is preserved.",
        "- attach_regen_source_validation_gate remains compatible.",
    ])

    return "\n".join(lines)


def audit_regen_source_validation(*args, **kwargs):
    payload = _leaf_16t3q9_original_audit_regen_source_validation(*args, **kwargs)

    ready = bool(
        _leaf_16t3q9_get_first(
            payload,
            [
                "regen_source_validation_pass_allowed",
                "source_validation_pass_allowed",
                "pass_allowed",
            ],
            False,
        )
    )

    legacy_status = str(
        _leaf_16t3q9_get_first(
            payload,
            [
                "regen_source_validation_gate_status",
                "regen_source_validation_status",
                "source_validation_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    findings = _leaf_16t3q9_classify_source_validation_findings(payload)
    canonical_status = _leaf_16t3q9_canonical_status_from_findings(findings, ready)

    global_status_payload = _leaf_16t3q9_build_global_status_payload(
        canonical_status,
        legacy_status,
        findings,
        ready,
    )

    adapter_report = _leaf_16t3q9_build_adapter_report(
        canonical_status,
        legacy_status,
        findings,
    )

    if not isinstance(payload, dict):
        payload = {}

    payload.update({
        "phase_16t3q9_status_adapter_complete": True,
        "phase_16t3q9_regen_source_validation_gate_status_adapter_complete": True,
        "regen_source_validation_gate_status_adapter_complete": True,
        "regen_source_validation_gate_status_adapter_status": PHASE_16T3Q9_STATUS_ADAPTER_STATUS,
        "regen_source_validation_gate_structured_findings": findings,
        "regen_source_validation_gate_global_status": canonical_status,
        "regen_source_validation_gate_global_status_payload": global_status_payload,
        "regen_source_validation_gate_adapter_report": adapter_report,
        "regen_source_validation_gate_legacy_status": legacy_status,
        "structured_findings": findings,
        "global_status": canonical_status,
        "global_status_payload": global_status_payload,
        "adapter_report": adapter_report,
    })

    return payload


