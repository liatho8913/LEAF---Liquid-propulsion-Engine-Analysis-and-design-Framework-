from leaf_qt.status_presentation import status_severity
"""
LEAF Real Engine Benchmark Completion Audit
==========================================

Stage W.6 completion audit for real-engine benchmarking.

This module owns final architectural signoff evidence for Stage W.

It confirms:

- Stage V dependency is complete
- W.1 framework is complete
- W.2 source owner is complete
- W.3 band owner is complete
- W.4 failure owner is complete
- W.5 master gate is complete
- Required reports exist
- Required statuses are passing

It does not create pass/fail logic.
It only audits ownership completion.
"""


try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
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

def attach_real_engine_benchmark_completion_audit(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_real_engine_benchmark_completion_audit(results)
    results.update(audit)
    return results


def evaluate_real_engine_benchmark_completion_audit(results):
    results = results if isinstance(results, dict) else {}

    if (
        results.get("real_engine_benchmarking_framework_status")
        == "NOT_APPLICABLE_NO_SUITABLE_REFERENCE"
    ):
        status = "NOT_APPLICABLE_NO_SUITABLE_REFERENCE"
        complete = True
        checks = [
            {
                "name": "Benchmark applicability assessment",
                "passed": True,
                "detail": (
                    "No suitable public reference exists; "
                    "benchmark validation is not applicable."
                ),
            },
        ]
        text = (
            "LEAF REAL-ENGINE BENCHMARK COMPLETION AUDIT\n"
            "===========================================\n\n"
            "Status: NOT_APPLICABLE_NO_SUITABLE_REFERENCE\n"
            "Applicability assessment complete: True\n"
            "Benchmark PASS claimed: False\n\n"
            "No suitable public reference engine exists for this design scope."
        )
        return {
            "real_engine_benchmark_completion_audit_status": status,
            "real_engine_benchmark_completion_audit_complete": complete,
            "real_engine_benchmark_completion_audit_checks": checks,
            "real_engine_benchmark_completion_audit_blocking_reasons": [],
            "real_engine_benchmark_completion_audit_warning_reasons": [],
            "real_engine_benchmark_completion_audit_text": text,
            "stage_w_real_engine_benchmarking_complete": True,
            "stage_w_real_engine_benchmark_complete": True,
            "stage_w_complete": True,
            "stage_w6_real_engine_benchmark_completion_audit_complete": True,
            "stage_w5_real_engine_benchmark_completion_audit_complete": True,
        }

    blocking_reasons = []
    warning_reasons = []
    checks = []

    stage_v_complete = bool(
        results.get("stage_v_scalability_complete")
        or results.get("stage_v_complete")
        or results.get("stage_v_regen_scalability_complete")
    )

    _add_check(
        checks,
        blocking_reasons,
        name="Stage V scalability dependency",
        passed=stage_v_complete,
        blocking_reason="Stage V scalability is incomplete, so Stage W cannot be signed off.",
    )

    required_completion_checks = [
        (
            "W.1 benchmarking framework",
            "stage_w1_real_engine_benchmarking_framework_complete",
        ),
        (
            "W.2 public source ownership",
            "stage_w2_public_benchmark_source_ownership_complete",
        ),
        (
            "W.3 numeric benchmark band ownership",
            "stage_w3_numeric_benchmark_band_ownership_complete",
        ),
        (
            "W.4 failure ownership",
            "stage_w4_real_engine_benchmark_failure_ownership_complete",
        ),
        (
            "W.5 master gate",
            "stage_w5_real_engine_benchmark_master_gate_complete",
        ),
    ]

    for label, key in required_completion_checks:
        passed = bool(results.get(key, False))
        _add_check(
            checks,
            blocking_reasons,
            name=label,
            passed=passed,
            blocking_reason=f"{label} is incomplete or false: {key}",
        )

    required_report_checks = [
        (
            "W.1 framework report",
            "real_engine_benchmarking_framework_text",
        ),
        (
            "W.2 source owner report",
            "real_engine_benchmark_source_owner_text",
        ),
        (
            "W.3 numeric band report",
            "real_engine_benchmark_band_owner_text",
        ),
        (
            "W.4 failure owner report",
            "real_engine_benchmark_failure_owner_text",
        ),
        (
            "W.5 master gate report",
            "real_engine_benchmark_master_gate_text",
        ),
    ]

    for label, key in required_report_checks:
        passed = bool(results.get(key))
        _add_check(
            checks,
            blocking_reasons,
            name=label,
            passed=passed,
            blocking_reason=f"{label} is missing: {key}",
        )

    required_status_checks = [
        (
            "W.1 framework status",
            "real_engine_benchmarking_framework_status",
        ),
        (
            "W.2 source owner status",
            "real_engine_benchmark_source_owner_status",
        ),
        (
            "W.3 numeric band owner status",
            "real_engine_benchmark_band_owner_status",
        ),
        (
            "W.4 failure owner status",
            "real_engine_benchmark_failure_owner_status",
        ),
        (
            "W.5 master gate status",
            "real_engine_benchmark_master_gate_status",
        ),
    ]

    for label, key in required_status_checks:
        status_value = str(results.get(key, "UNKNOWN")).upper().strip()

        if not _status_is_known(status_value):
            _add_check(
                checks,
                blocking_reasons,
                name=label,
                passed=False,
                blocking_reason=f"{label} is missing or unknown: {key}",
            )
            continue

        if _status_blocks(status_value):
            _add_check(
                checks,
                blocking_reasons,
                name=label,
                passed=False,
                blocking_reason=f"{label} blocks Stage W completion: {key}={status_value}",
            )
            continue

        if _status_requires_review(status_value):
            _add_check(
                checks,
                warning_reasons,
                name=label,
                passed=False,
                blocking_reason=f"{label} requires review before completion: {key}={status_value}",
            )
            continue

        _add_check(
            checks,
            blocking_reasons,
            name=label,
            passed=True,
            blocking_reason="",
        )

    reference_engine = results.get("real_engine_benchmark_reference_engine", "N/A")
    master_gate_status = results.get("real_engine_benchmark_master_gate_status", "UNKNOWN")

    complete = not blocking_reasons and not warning_reasons

    if complete:
        status = "PASS_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"
    else:
        status = "FAIL_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"

    text = build_real_engine_benchmark_completion_audit_text(
        status=status,
        complete=complete,
        reference_engine=reference_engine,
        master_gate_status=master_gate_status,
        checks=checks,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        results=results,
    )

    return {
        "real_engine_benchmark_completion_audit_status": status,
        "real_engine_benchmark_completion_audit_complete": complete,
        "real_engine_benchmark_completion_audit_checks": checks,
        "real_engine_benchmark_completion_audit_blocking_reasons": blocking_reasons,
        "real_engine_benchmark_completion_audit_warning_reasons": warning_reasons,
        "real_engine_benchmark_completion_audit_text": text,

        # Canonical Stage W completion keys.
        "stage_w_real_engine_benchmarking_complete": complete,
        "stage_w_real_engine_benchmark_complete": complete,
        "stage_w_complete": complete,

        # Stage W.6 owned key.
        "stage_w6_real_engine_benchmark_completion_audit_complete": complete,

        # Older compatibility key used by save/load or handover systems.
        "stage_w5_real_engine_benchmark_completion_audit_complete": complete,
    }


def _add_check(checks, reason_target, name, passed, blocking_reason):
    checks.append({
        "name": name,
        "passed": bool(passed),
        "reason": "" if passed else blocking_reason,
    })

    if not passed and blocking_reason:
        reason_target.append(blocking_reason)


def build_real_engine_benchmark_completion_audit_text(
    status,
    complete,
    reference_engine,
    master_gate_status,
    checks,
    blocking_reasons,
    warning_reasons,
    results,
):
    lines = [
        "LEAF STAGE W.6 REAL ENGINE BENCHMARK COMPLETION AUDIT",
        "======================================================",
        "",
        f"Status: {status}",
        f"Stage W real-engine benchmarking complete: {complete}",
        "",
        "Owned By:",
        "- real_engine_benchmark_completion_audit.py",
        "",
        "Reference:",
        f"- Engine: {reference_engine}",
        "",
        "Master Gate:",
        f"- Status: {master_gate_status}",
        f"- Pass allowed: {results.get('real_engine_benchmark_master_gate_pass_allowed', False)}",
        "",
        "Completion Inputs:",
        f"- Stage V scalability complete: {results.get('stage_v_scalability_complete', False)}",
        f"- W.1 complete: {results.get('stage_w1_real_engine_benchmarking_framework_complete', False)}",
        f"- W.2 complete: {results.get('stage_w2_public_benchmark_source_ownership_complete', False)}",
        f"- W.3 complete: {results.get('stage_w3_numeric_benchmark_band_ownership_complete', False)}",
        f"- W.4 complete: {results.get('stage_w4_real_engine_benchmark_failure_ownership_complete', False)}",
        f"- W.5 complete: {results.get('stage_w5_real_engine_benchmark_master_gate_complete', False)}",
        "",
        "Checks:",
    ]

    for check in checks:
        marker = LegacyCompatibilityProducer.marker_from_bool(check["passed"])
        lines.append(f"- [{marker}] {check['name']}")
        if check.get("reason"):
            lines.append(f"  Reason: {check['reason']}")

    lines.append("")
    lines.append("Blocking Reasons:")
    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Warnings:")
    lines.extend([f"- {item}" for item in warning_reasons] or ["- None."])

    lines.append("")
    lines.append("Rule:")
    lines.append("- Stage W is complete only when W.1-W.5 are complete.")
    lines.append("- Missing reports block completion.")
    lines.append("- Unknown, warning, or failed statuses block final benchmark signoff.")
    lines.append("- Benchmarking must remain conservative, public-data-based, and auditable.")

    return "\n".join(lines)


def _status_is_known(status):
    status = str(status or "").upper().strip()
    return status not in {"", "NONE", "N/A", "UNKNOWN"}


def _status_blocks(status):
    status = str(status or "").upper().strip()

    if status_severity(status) == "PASS":
        return False

    return any(fragment in status for fragment in (
        "FAIL",
        "BLOCK",
        "ERROR",
        "INVALID",
        "UNKNOWN",
    ))


def _status_requires_review(status):
    status = str(status or "").upper().strip()

    if status_severity(status) == "PASS":
        return False

    return any(fragment in status for fragment in (
        "WARN",
        "REVIEW",
        "LIMITED",
    ))
