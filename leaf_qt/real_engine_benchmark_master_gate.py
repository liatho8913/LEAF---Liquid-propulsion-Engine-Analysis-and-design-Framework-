from leaf_qt.structured_status_access import findings_highest_severity, highest_severity as gate_highest_severity, is_pass
"""
LEAF Real Engine Benchmark Master Gate
======================================

Stage W.5 final trust gate for real-engine benchmarking.

This module owns:

- final Stage W pass permission
- dependency checking
- owner-status aggregation
- conservative benchmark signoff

This module does not:
- select benchmark engines
- classify source confidence
- compute numeric bands
- explain root causes in detail

Those responsibilities belong to W.1-W.4.
"""


PASS_PREFIXES = (
    "PASS",
)


from leaf_qt.global_status_classification_engine import (
    classify_status,
    make_finding,
)


OWNER = "Real Engine Benchmark Master Gate"


BLOCKING_STATUS_FRAGMENTS = (
    "FAIL",
    "BLOCK",
    "ERROR",
    "INVALID",
    "UNKNOWN",
)


REVIEW_STATUS_FRAGMENTS = (
    "WARN",
    "REVIEW",
    "LIMITED",
)


def _real_engine_benchmark_master_gate_findings(
    *,
    blocking_reasons,
    warning_reasons,
    evidence,
):
    findings = []

    for reason in blocking_reasons:
        reason_text = str(reason)

        if "FAIL" in reason_text.upper() or "ERROR" in reason_text.upper() or "INVALID" in reason_text.upper():
            category = "VALIDATION_FAILURE"
        elif "missing" in reason_text.lower() or "incomplete" in reason_text.lower() or "unknown" in reason_text.lower():
            category = "VALIDATION_INCOMPLETE"
        else:
            category = "VALIDATION_INCOMPLETE"

        findings.append(
            make_finding(
                message=reason_text,
                category=category,
                owner=OWNER,
                evidence=evidence,
            )
        )

    for reason in warning_reasons:
        findings.append(
            make_finding(
                message=str(reason),
                category="MANUAL_REVIEW_REQUIRED",
                owner=OWNER,
                evidence=evidence,
            )
        )

    if not findings:
        findings.append(
            make_finding(
                message="Real-engine benchmark master gate passed.",
                category="COMPLETE",
                owner=OWNER,
                evidence=evidence,
            )
        )

    return findings


def attach_real_engine_benchmark_master_gate(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_real_engine_benchmark_master_gate(results)
    results.update(audit)
    return results


def evaluate_real_engine_benchmark_master_gate(results):
    results = results if isinstance(results, dict) else {}

    if (
        results.get("real_engine_benchmarking_framework_status")
        == "NOT_APPLICABLE_NO_SUITABLE_REFERENCE"
    ):
        status = "NOT_APPLICABLE_NO_SUITABLE_REFERENCE"
        pass_allowed = False
        evidence = [
            "Benchmark applicability assessment completed: no suitable public reference engine.",
        ]
        text = (
            "LEAF REAL-ENGINE BENCHMARK MASTER GATE\n"
            "======================================\n\n"
            "Status: NOT_APPLICABLE_NO_SUITABLE_REFERENCE\n"
            "PASS allowed: False\n\n"
            "Benchmark applicability is complete, but benchmark signoff is not applicable."
        )
        return {
            "real_engine_benchmark_master_gate_status": status,
            "real_engine_benchmark_master_gate_pass_allowed": pass_allowed,
            "real_engine_benchmark_master_gate_blocking_reasons": [],
            "real_engine_benchmark_master_gate_warning_reasons": [],
            "real_engine_benchmark_master_gate_owner_summary": [],
            "real_engine_benchmark_master_gate_evidence": evidence,
            "real_engine_benchmark_master_gate_text": text,
            "stage_w5_real_engine_benchmark_master_gate_complete": True,
        }

    blocking_reasons = []
    warning_reasons = []
    evidence = []

    stage_v_complete = bool(
        results.get("stage_v_scalability_complete")
        or results.get("stage_v_complete")
        or results.get("stage_v_regen_scalability_complete")
    )

    if not stage_v_complete:
        blocking_reasons.append(
            "Stage V scalability is incomplete, so Stage W benchmarking cannot be trusted."
        )

    owner_checks = [
        {
            "label": "W.1 benchmarking framework",
            "complete_key": "stage_w1_real_engine_benchmarking_framework_complete",
            "status_key": "real_engine_benchmarking_framework_status",
            "text_key": "real_engine_benchmarking_framework_text",
        },
        {
            "label": "W.2 public source ownership",
            "complete_key": "stage_w2_public_benchmark_source_ownership_complete",
            "status_key": "real_engine_benchmark_source_owner_status",
            "text_key": "real_engine_benchmark_source_owner_text",
        },
        {
            "label": "W.3 numeric benchmark band ownership",
            "complete_key": "stage_w3_numeric_benchmark_band_ownership_complete",
            "status_key": "real_engine_benchmark_band_owner_status",
            "text_key": "real_engine_benchmark_band_owner_text",
        },
        {
            "label": "W.4 failure ownership",
            "complete_key": "stage_w4_real_engine_benchmark_failure_ownership_complete",
            "status_key": "real_engine_benchmark_failure_owner_status",
            "text_key": "real_engine_benchmark_failure_owner_text",
        },
    ]

    owner_summary = []

    for check in owner_checks:
        summary = evaluate_owner_check(results, check)
        owner_summary.append(summary)

        if summary["blocking_reasons"]:
            blocking_reasons.extend(summary["blocking_reasons"])

        if summary["warning_reasons"]:
            warning_reasons.extend(summary["warning_reasons"])

        evidence.append(
            f"{summary['label']}: complete={summary['complete']}, status={summary['status']}"
        )

    reference_engine = results.get("real_engine_benchmark_reference_engine")
    if reference_engine:
        evidence.append(f"Reference engine: {reference_engine}")
    else:
        blocking_reasons.append(
            "No real-engine benchmark reference engine is available for Stage W signoff."
        )

    source_confidence = results.get("real_engine_benchmark_source_owner_confidence")
    if source_confidence is not None:
        evidence.append(f"Source confidence: {source_confidence}")

    band_rows = results.get("real_engine_benchmark_band_owner_rows")
    if isinstance(band_rows, list):
        evidence.append(f"Numeric benchmark rows: {len(band_rows)}")

    if blocking_reasons:
        status = "FAIL_REAL_ENGINE_BENCHMARK_MASTER_GATE"
        pass_allowed = False
    elif warning_reasons:
        status = "WARN_REAL_ENGINE_BENCHMARK_MASTER_GATE_REVIEW_REQUIRED"
        pass_allowed = False
    else:
        status = "PASS_REAL_ENGINE_BENCHMARK_MASTER_GATE"
        pass_allowed = True

    structured_findings = _real_engine_benchmark_master_gate_findings(
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        evidence=evidence,
    )
    global_status_payload = classify_status(
        structured_findings,
        production_gate=True,
    )

    text = build_master_gate_text(
        status=status,
        pass_allowed=pass_allowed,
        stage_v_complete=stage_v_complete,
        owner_summary=owner_summary,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        evidence=evidence,
        global_status_payload=global_status_payload,
    )

    return {
        "real_engine_benchmark_master_gate_status": status,
        "real_engine_benchmark_master_gate_pass_allowed": pass_allowed,
        "real_engine_benchmark_master_gate_blocking_reasons": blocking_reasons,
        "real_engine_benchmark_master_gate_warning_reasons": warning_reasons,
        "real_engine_benchmark_master_gate_owner_summary": owner_summary,
        "real_engine_benchmark_master_gate_evidence": evidence,
        "real_engine_benchmark_master_gate_structured_findings": structured_findings,
        "real_engine_benchmark_master_gate_global_status": global_status_payload["status"],
        "real_engine_benchmark_master_gate_global_status_payload": global_status_payload,
        "real_engine_benchmark_master_gate_text": text,

        # Completion-audit compatibility key.
        "stage_w5_real_engine_benchmark_master_gate_complete": pass_allowed,
    }


def evaluate_owner_check(results, check):
    label = check["label"]
    complete_key = check["complete_key"]
    status_key = check["status_key"]
    text_key = check["text_key"]

    complete = bool(results.get(complete_key, False))
    status = str(results.get(status_key, "UNKNOWN")).upper().strip()
    text_present = bool(results.get(text_key))

    blocking_reasons = []
    warning_reasons = []

    if not complete:
        blocking_reasons.append(
            f"{label} is incomplete or false: {complete_key}"
        )

    if not text_present:
        blocking_reasons.append(
            f"{label} report is missing: {text_key}"
        )

    if not _status_is_known(status):
        blocking_reasons.append(
            f"{label} status is missing or unknown: {status_key}"
        )
    elif _status_blocks(status):
        blocking_reasons.append(
            f"{label} status blocks Stage W signoff: {status_key}={status}"
        )
    elif _status_requires_review(status):
        warning_reasons.append(
            f"{label} status requires review before signoff: {status_key}={status}"
        )

    return {
        "label": label,
        "complete_key": complete_key,
        "status_key": status_key,
        "text_key": text_key,
        "complete": complete,
        "status": status,
        "text_present": text_present,
        "blocking_reasons": blocking_reasons,
        "warning_reasons": warning_reasons,
    }


def build_master_gate_text(
    status,
    pass_allowed,
    stage_v_complete,
    owner_summary,
    blocking_reasons,
    warning_reasons,
    evidence,
    global_status_payload=None,
):
    lines = [
        "LEAF STAGE W.5 REAL ENGINE BENCHMARK MASTER GATE",
        "=================================================",
        "",
        f"Status: {status}",
        f"Benchmark PASS allowed: {pass_allowed}",
        "",
        "Owned By:",
        "- real_engine_benchmark_master_gate.py",
        "",
        "Scope:",
        "- Aggregates W.1-W.4 ownership.",
        "- Allows final Stage W signoff only when all benchmark owners pass.",
        "- Blocks unknown, warning, failed, incomplete, or missing-report states.",
        "- Does not perform benchmark calculations directly.",
        "",
        "Stage Dependencies:",
        f"- Stage V scalability complete: {stage_v_complete}",
        "",
        "Owner Summary:",
    ]

    for item in owner_summary:
        lines.append(
            f"- {item['label']}: complete={item['complete']}, "
            f"status={item['status']}, text_present={item['text_present']}"
        )

    lines.append("")
    lines.append("Blocking Reasons:")
    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Warning Reasons:")
    lines.extend([f"- {item}" for item in warning_reasons] or ["- None."])

    lines.append("")
    lines.append("Evidence:")
    lines.extend([f"- {item}" for item in evidence] or ["- None."])

    if global_status_payload is not None:
        lines.append("")
        lines.append("Global Status Engine:")
        lines.append(f"- canonical_status: {global_status_payload.get('status')}")
        lines.append(f"- finding_count: {global_status_payload.get('finding_count')}")
        lines.append(f"- blocked: {global_status_payload.get('blocked')}")
        lines.append(f"- failed: {global_status_payload.get('failed')}")

    lines.append("")
    lines.append("Rule:")
    lines.append("- Stage W PASS is allowed only when W.1-W.4 are complete and passing.")
    lines.append("- Warnings block final signoff until reviewed.")
    lines.append("- Missing reports block signoff.")
    lines.append("- Benchmarking remains conservative and public-data based.")
    lines.append("- Structured findings now control canonical global status classification.")

    return "\n".join(lines)


def _status_is_known(status):
    return status not in {"", "NONE", "N/A", "UNKNOWN"}


def _status_blocks(status):
    status = str(status or "").upper().strip()

    if is_pass(status):
        return False

    return any(fragment in status for fragment in BLOCKING_STATUS_FRAGMENTS)


def _status_requires_review(status):
    status = str(status or "").upper().strip()

    if is_pass(status):
        return False

    return any(fragment in status for fragment in REVIEW_STATUS_FRAGMENTS)