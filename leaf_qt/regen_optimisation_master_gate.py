from leaf_qt.structured_status_access import findings_highest_severity, highest_severity as gate_highest_severity, is_pass
"""
LEAF Regen Optimisation Master Gate
===================================

REGEN PHASE 8G

Owns the trust gate for regen optimisation recommendation evidence.

This module decides whether optimisation recommendation evidence is structurally
approval-ready.

It does NOT:
- apply geometry
- modify engine inputs
- run optimisation automatically
- replace validation gates
- act as the completion audit
"""


def attach_regen_optimisation_master_gate(results):
    if not isinstance(results, dict):
        return results

    gate = build_regen_optimisation_master_gate(results)
    results.update(gate)
    return results


def _leaf_16t3q6_original_build_regen_optimisation_master_gate(results):
    results = results if isinstance(results, dict) else {}

    dependencies = {
        "phase_8a_profile_complete": bool(
            results.get("phase_8a_regen_optimisation_profile_complete", False)
        ),
        "phase_8b_candidate_generator_complete": bool(
            results.get("phase_8b_regen_optimisation_candidate_generator_complete", False)
        ),
        "phase_8c_scoring_owner_complete": bool(
            results.get("phase_8c_regen_optimisation_scoring_owner_complete", False)
        ),
        "phase_8d_failure_owner_complete": bool(
            results.get("phase_8d_regen_optimisation_failure_owner_complete", False)
        ),
        "phase_8e_report_owner_complete": bool(
            results.get("phase_8e_regen_optimisation_report_owner_complete", False)
        ),
        "phase_8f_recommendation_owner_complete": bool(
            results.get("phase_8f_regen_optimisation_recommendation_owner_complete", False)
        ),
    }

    recommendation_allowed = bool(
        results.get("regen_optimisation_recommendation_allowed", False)
    )

    recommendation_candidate = results.get("regen_optimisation_recommendation_candidate")
    recommendation_exists = isinstance(recommendation_candidate, dict)

    blocking_failure_count = _safe_int(
        results.get("regen_optimisation_blocking_failure_count"),
        default=0,
    )

    report_complete = bool(
        results.get("regen_optimisation_report_owner_complete", False)
    )

    gate_reasons = _build_gate_reasons(
        dependencies=dependencies,
        recommendation_allowed=recommendation_allowed,
        recommendation_exists=recommendation_exists,
        blocking_failure_count=blocking_failure_count,
        report_complete=report_complete,
        results=results,
    )

    approval_ready = not gate_reasons

    status = (
        "PASS_REGEN_OPTIMISATION_MASTER_GATE"
        if approval_ready
        else "FAIL_REGEN_OPTIMISATION_MASTER_GATE"
    )

    text = build_regen_optimisation_master_gate_text(
        status=status,
        approval_ready=approval_ready,
        dependencies=dependencies,
        recommendation_allowed=recommendation_allowed,
        recommendation_exists=recommendation_exists,
        blocking_failure_count=blocking_failure_count,
        report_complete=report_complete,
        gate_reasons=gate_reasons,
        recommendation_candidate=recommendation_candidate,
    )

    return {
        "regen_optimisation_master_gate_status": status,
        "regen_optimisation_master_gate_complete": True,
        "regen_optimisation_master_gate_approval_ready": approval_ready,
        "regen_optimisation_master_gate_dependencies": dependencies,
        "regen_optimisation_master_gate_reasons": gate_reasons,
        "regen_optimisation_master_gate_recommendation_allowed": recommendation_allowed,
        "regen_optimisation_master_gate_recommendation_exists": recommendation_exists,
        "regen_optimisation_master_gate_blocking_failure_count": blocking_failure_count,
        "regen_optimisation_master_gate_report_complete": report_complete,
        "regen_optimisation_master_gate_geometry_application_allowed": False,
        "regen_optimisation_master_gate_automatic_selection_allowed": False,
        "regen_optimisation_master_gate_text": text,
        "phase_8g_regen_optimisation_master_gate_complete": True,
    }


def build_regen_optimisation_master_gate_text(
        status,
        approval_ready,
        dependencies,
        recommendation_allowed,
        recommendation_exists,
        blocking_failure_count,
        report_complete,
        gate_reasons,
        recommendation_candidate,
):
    lines = [
        "LEAF REGEN PHASE 8G OPTIMISATION MASTER GATE",
        "==============================================",
        "",
        f"Status: {status}",
        f"Approval ready: {approval_ready}",
        f"Recommendation allowed: {recommendation_allowed}",
        f"Recommendation exists: {recommendation_exists}",
        f"Blocking failure count: {blocking_failure_count}",
        f"Report complete: {report_complete}",
        "",
        "Owned By:",
        "- regen_optimisation_master_gate.py",
        "",
        "Scope:",
        "- Owns optimisation recommendation trust gating.",
        "- Checks Phase 8A-8F dependency completion.",
        "- Checks recommendation evidence existence.",
        "- Checks blocking failure state.",
        "- Checks report ownership state.",
        "- Does not apply geometry.",
        "- Does not modify engine inputs.",
        "- Does not run optimisation automatically.",
        "- Does not act as completion audit.",
        "",
        "Phase Locks:",
        "- Geometry application allowed: False",
        "- Automatic selection allowed: False",
        "",
        "Dependency Status:",
    ]

    for key, value in dependencies.items():
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("Gate Reasons:")

    if gate_reasons:
        for reason in gate_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Recommendation Candidate:")

    if isinstance(recommendation_candidate, dict):
        lines.append(f"- candidate_id: {recommendation_candidate.get('candidate_id')}")
        lines.append(f"- total_score: {recommendation_candidate.get('total_score')}")
        lines.append(f"- recommendation_rank: {recommendation_candidate.get('recommendation_rank')}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 8G is verified, build Phase 8H completion audit before any geometry application logic."
    )

    return "\n".join(lines)


def _build_gate_reasons(
        dependencies,
        recommendation_allowed,
        recommendation_exists,
        blocking_failure_count,
        report_complete,
        results,
):
    reasons = []

    for key, value in dependencies.items():
        if not value:
            reasons.append(f"Dependency not complete: {key}")

    if not report_complete:
        reasons.append("Optimisation report owner is not complete.")

    if not recommendation_allowed:
        reasons.append("Recommendation evidence is not currently allowed.")

    if not recommendation_exists:
        reasons.append("No recommendation candidate exists.")

    if blocking_failure_count > 0:
        reasons.append(
            "Blocking optimisation failures exist, so master gate approval readiness is blocked."
        )

    if results.get("regen_optimisation_apply_geometry_requested"):
        reasons.append(
            "Geometry application was requested, but Phase 8G only gates recommendation trust."
        )

    if results.get("regen_optimisation_auto_select_requested"):
        reasons.append(
            "Automatic selection was requested, but Phase 8G does not select or apply geometry."
        )

    return reasons


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


# ---------------------------------------------------------------------------
# PHASE 16T.3Q.6 — WAVE 2 STATUS ADAPTER
# REGEN OPTIMISATION MASTER GATE
# ---------------------------------------------------------------------------

PHASE_16T3Q6_STATUS_ADAPTER_COMPLETE = True
PHASE_16T3Q6_STATUS_ADAPTER_STATUS = (
    "PASS_REGEN_OPTIMISATION_STATUS_ADAPTER_PHASE_16T3Q6"
)


def _leaf_16t3q6_make_finding(code, severity, message, evidence=None):
    return {
        "code": str(code),
        "severity": str(severity).upper(),
        "message": str(message),
        "evidence": evidence or {},
        "phase": "16T.3Q.6",
        "owner": "regen_optimisation_master_gate",
    }


def _leaf_16t3q6_get_first(payload, keys, default=None):
    if not isinstance(payload, dict):
        return default

    for key in keys:
        if key in payload:
            return payload.get(key)

    return default


def _leaf_16t3q6_canonical_status_from_findings(findings, ready):
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


def _leaf_16t3q6_classify_optimisation_findings(payload):
    findings = []

    if not isinstance(payload, dict):
        return [
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_MASTER_GATE_PAYLOAD_INVALID",
                "FAIL",
                "Optimisation master gate did not return a dictionary payload.",
                {"payload_type": type(payload).__name__},
            )
        ]

    ready = bool(
        _leaf_16t3q6_get_first(
            payload,
            [
                "regen_optimisation_master_gate_ready",
                "regen_candidate_optimisation_master_gate_ready",
                "regen_optimisation_ready",
                "ready",
            ],
            False,
        )
    )

    legacy_status = str(
        _leaf_16t3q6_get_first(
            payload,
            [
                "regen_optimisation_master_gate_status",
                "regen_candidate_optimisation_master_gate_status",
                "regen_optimisation_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    failed_checks = _leaf_16t3q6_get_first(
        payload,
        [
            "regen_optimisation_master_gate_failed_checks",
            "regen_candidate_optimisation_master_gate_failed_checks",
            "regen_optimisation_failed_checks",
            "failed_checks",
        ],
        [],
    )

    checks = _leaf_16t3q6_get_first(
        payload,
        [
            "regen_optimisation_master_gate_checks",
            "regen_candidate_optimisation_master_gate_checks",
            "regen_optimisation_checks",
            "checks",
        ],
        [],
    )

    if ready:
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_MASTER_GATE_READY",
                "INFO",
                "Regen optimisation master gate reports ready.",
                {"legacy_status": legacy_status},
            )
        )
    else:
        severity = "FAIL" if "FAIL" in legacy_status.upper() else "REVIEW_REQUIRED"
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_MASTER_GATE_NOT_READY",
                severity,
                "Regen optimisation master gate does not report ready.",
                {"legacy_status": legacy_status},
            )
        )

    if isinstance(failed_checks, list) and failed_checks:
        for index, check in enumerate(failed_checks):
            findings.append(
                _leaf_16t3q6_make_finding(
                    f"FAILED_OPTIMISATION_CHECK_{index}",
                    "FAIL",
                    "Regen optimisation master gate contains a failed check.",
                    {"check": check},
                )
            )
    elif isinstance(failed_checks, list):
        findings.append(
            _leaf_16t3q6_make_finding(
                "NO_FAILED_OPTIMISATION_CHECKS",
                "INFO",
                "No failed regen optimisation checks were reported.",
                {},
            )
        )
    else:
        findings.append(
            _leaf_16t3q6_make_finding(
                "FAILED_OPTIMISATION_CHECKS_PAYLOAD_INVALID",
                "REVIEW_REQUIRED",
                "Failed-check payload is not a list.",
                {"failed_checks_type": type(failed_checks).__name__},
            )
        )

    if isinstance(checks, list) and checks:
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_CHECKS_PRESENT",
                "INFO",
                "Regen optimisation master gate checks are present.",
                {"check_count": len(checks)},
            )
        )
    else:
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_CHECKS_MISSING",
                "REVIEW_REQUIRED",
                "Regen optimisation master gate checks are missing or empty.",
                {"checks_type": type(checks).__name__},
            )
        )

    runtime_mutation_allowed = _leaf_16t3q6_get_first(
        payload,
        [
            "regen_candidate_runtime_mutation_allowed",
            "regen_runtime_mutation_allowed",
            "runtime_mutation_allowed",
        ],
        None,
    )

    runtime_evolution_allowed = _leaf_16t3q6_get_first(
        payload,
        [
            "regen_candidate_runtime_evolution_allowed",
            "regen_runtime_evolution_allowed",
            "runtime_evolution_allowed",
        ],
        None,
    )

    runtime_solver_allowed = _leaf_16t3q6_get_first(
        payload,
        [
            "regen_candidate_runtime_solver_allowed",
            "regen_runtime_solver_allowed",
            "runtime_solver_allowed",
        ],
        None,
    )

    runtime_acceptance_allowed = _leaf_16t3q6_get_first(
        payload,
        [
            "regen_candidate_runtime_acceptance_allowed",
            "regen_runtime_acceptance_allowed",
            "runtime_acceptance_allowed",
        ],
        None,
    )

    runtime_flags = {
        "mutation": runtime_mutation_allowed,
        "evolution": runtime_evolution_allowed,
        "solver": runtime_solver_allowed,
        "acceptance": runtime_acceptance_allowed,
    }

    missing_runtime = [
        name for name, value in runtime_flags.items()
        if value is None
    ]

    if missing_runtime:
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_RUNTIME_FLAGS_MISSING",
                "REVIEW_REQUIRED",
                "One or more optimisation runtime permission flags are missing.",
                {"missing_runtime_flags": missing_runtime},
            )
        )
    else:
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_RUNTIME_FLAGS_PRESENT",
                "INFO",
                "Optimisation runtime permission flags are present.",
                {"runtime_flags": runtime_flags},
            )
        )

    optimisation_payload = _leaf_16t3q6_get_first(
        payload,
        [
            "regen_optimisation_payload",
            "regen_candidate_optimisation_payload",
            "optimisation_payload",
        ],
        None,
    )

    if optimisation_payload is None:
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_PAYLOAD_MISSING",
                "REVIEW_REQUIRED",
                "Regen optimisation payload is missing.",
                {},
            )
        )
    elif isinstance(optimisation_payload, dict):
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_PAYLOAD_PRESENT",
                "INFO",
                "Regen optimisation payload is present.",
                {"payload_keys": sorted(optimisation_payload.keys())[:20]},
            )
        )
    else:
        findings.append(
            _leaf_16t3q6_make_finding(
                "OPTIMISATION_PAYLOAD_INVALID",
                "FAIL",
                "Regen optimisation payload is present but not a dictionary.",
                {"payload_type": type(optimisation_payload).__name__},
            )
        )

    return findings


def _leaf_16t3q6_build_global_status_payload(
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
        "owner": "regen_optimisation_master_gate",
        "phase": "16T.3Q.6",
        "canonical_status": canonical_status,
        "global_status": canonical_status,
        "legacy_status": legacy_status,
        "ready": bool(ready),
        "finding_count": len(findings),
        "severity_counts": severity_counts,
        "findings": findings,
        "adapter": "wave_2_status_adapter",
        "adapter_phase": "16T.3Q.6",
    }


def _leaf_16t3q6_build_adapter_report(
    canonical_status,
    legacy_status,
    findings,
):
    lines = [
        "LEAF PHASE 16T.3Q.6 STATUS ADAPTER",
        "====================================",
        "",
        "Owner: regen_optimisation_master_gate",
        "Target: Regen Optimisation Master Gate",
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
            "- Structured status fields are additive only.",
        ]
    )

    return "\n".join(lines)


def build_regen_optimisation_master_gate(*args, **kwargs):
    payload = _leaf_16t3q6_original_build_regen_optimisation_master_gate(
        *args,
        **kwargs,
    )

    if not isinstance(payload, dict):
        findings = _leaf_16t3q6_classify_optimisation_findings(payload)
        canonical_status = "FAIL"
        legacy_status = "UNKNOWN"
        ready = False

        global_status_payload = _leaf_16t3q6_build_global_status_payload(
            canonical_status=canonical_status,
            legacy_status=legacy_status,
            findings=findings,
            ready=ready,
        )

        adapter_report = _leaf_16t3q6_build_adapter_report(
            canonical_status=canonical_status,
            legacy_status=legacy_status,
            findings=findings,
        )

        return {
            "phase_16t3q6_status_adapter_complete": True,
            "phase_16t3q6_regen_optimisation_status_adapter_complete": True,
            "regen_optimisation_status_adapter_complete": True,
            "regen_optimisation_status_adapter_status": (
                PHASE_16T3Q6_STATUS_ADAPTER_STATUS
            ),
            "regen_optimisation_master_gate_structured_findings": findings,
            "regen_optimisation_master_gate_global_status": canonical_status,
            "regen_optimisation_master_gate_global_status_payload": (
                global_status_payload
            ),
            "regen_optimisation_master_gate_adapter_report": adapter_report,
            "regen_optimisation_master_gate_legacy_status": legacy_status,
            "structured_findings": findings,
            "global_status": canonical_status,
            "global_status_payload": global_status_payload,
            "adapter_report": adapter_report,
        }

    ready = bool(
        _leaf_16t3q6_get_first(
            payload,
            [
                "regen_optimisation_master_gate_ready",
                "regen_candidate_optimisation_master_gate_ready",
                "regen_optimisation_ready",
                "ready",
            ],
            False,
        )
    )

    legacy_status = str(
        _leaf_16t3q6_get_first(
            payload,
            [
                "regen_optimisation_master_gate_status",
                "regen_candidate_optimisation_master_gate_status",
                "regen_optimisation_status",
                "status",
            ],
            "UNKNOWN",
        )
    )

    findings = _leaf_16t3q6_classify_optimisation_findings(payload)
    canonical_status = _leaf_16t3q6_canonical_status_from_findings(
        findings=findings,
        ready=ready,
    )

    global_status_payload = _leaf_16t3q6_build_global_status_payload(
        canonical_status=canonical_status,
        legacy_status=legacy_status,
        findings=findings,
        ready=ready,
    )

    adapter_report = _leaf_16t3q6_build_adapter_report(
        canonical_status=canonical_status,
        legacy_status=legacy_status,
        findings=findings,
    )

    payload.update(
        {
            "phase_16t3q6_status_adapter_complete": True,
            "phase_16t3q6_regen_optimisation_status_adapter_complete": True,
            "regen_optimisation_status_adapter_complete": True,
            "regen_optimisation_status_adapter_status": (
                PHASE_16T3Q6_STATUS_ADAPTER_STATUS
            ),
            "regen_optimisation_master_gate_structured_findings": findings,
            "regen_optimisation_master_gate_global_status": canonical_status,
            "regen_optimisation_master_gate_global_status_payload": (
                global_status_payload
            ),
            "regen_optimisation_master_gate_adapter_report": adapter_report,
            "regen_optimisation_master_gate_legacy_status": legacy_status,
            "structured_findings": findings,
            "global_status": canonical_status,
            "global_status_payload": global_status_payload,
            "adapter_report": adapter_report,
        }
    )

    return payload


