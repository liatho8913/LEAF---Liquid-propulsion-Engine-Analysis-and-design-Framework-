
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u46_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u46_is_fail_like(text) or _leaf_16u46_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u46_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u46_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u46_is_fail_like(value):
    return _leaf_16u46_status_severity(value) == "FAIL"


def _leaf_16u46_is_warn_like(value):
    return _leaf_16u46_status_severity(value) == "WARN"


def _leaf_16u46_is_pass_like(value):
    return _leaf_16u46_status_severity(value) == "PASS"


"""
LEAF Real Engine Benchmark Failure Owner
========================================

Stage W.4 owner for real-engine benchmark failure explanation.

This module owns:

- root-cause separation
- corrective actions
- failure categorisation
- benchmark failure narrative

This module does not approve Stage W.
This module does not override W.1/W.2/W.3.
This module does not make invalid benchmark cases pass.

Its job is to explain failures, not hide them.
"""


def attach_real_engine_benchmark_failure_owner(results):
    if not isinstance(results, dict):
        return results

    report = build_benchmark_failure_report(results)
    results.update(report)
    return results


def build_benchmark_failure_report(results):
    results = results if isinstance(results, dict) else {}

    root_causes = []
    corrective_actions = []
    failure_categories = []
    evidence = []

    _collect_status_issue(
        results=results,
        key="real_engine_benchmarking_framework_status",
        label="W.1 benchmarking framework",
        category="FRAMEWORK",
        root_causes=root_causes,
        corrective_actions=corrective_actions,
        failure_categories=failure_categories,
    )

    _collect_status_issue(
        results=results,
        key="real_engine_benchmark_source_owner_status",
        label="W.2 public source ownership",
        category="SOURCE_CONFIDENCE",
        root_causes=root_causes,
        corrective_actions=corrective_actions,
        failure_categories=failure_categories,
    )

    _collect_status_issue(
        results=results,
        key="real_engine_benchmark_band_owner_status",
        label="W.3 numeric benchmark band ownership",
        category="NUMERIC_BAND",
        root_causes=root_causes,
        corrective_actions=corrective_actions,
        failure_categories=failure_categories,
    )

    _collect_reason_list(
        results,
        "real_engine_benchmarking_framework_blocking_reasons",
        "W.1 blocker",
        "FRAMEWORK",
        root_causes,
        failure_categories,
    )

    _collect_reason_list(
        results,
        "real_engine_benchmark_source_owner_blocking_reasons",
        "W.2 source blocker",
        "SOURCE_CONFIDENCE",
        root_causes,
        failure_categories,
    )

    _collect_reason_list(
        results,
        "real_engine_benchmark_band_owner_blocking_reasons",
        "W.3 numeric-band blocker",
        "NUMERIC_BAND",
        root_causes,
        failure_categories,
    )

    _collect_reason_list(
        results,
        "real_engine_benchmarking_framework_warning_reasons",
        "W.1 warning",
        "FRAMEWORK_WARNING",
        root_causes,
        failure_categories,
    )

    _collect_reason_list(
        results,
        "real_engine_benchmark_source_owner_warning_reasons",
        "W.2 source warning",
        "SOURCE_WARNING",
        root_causes,
        failure_categories,
    )

    _collect_reason_list(
        results,
        "real_engine_benchmark_band_owner_warning_reasons",
        "W.3 numeric-band warning",
        "BAND_WARNING",
        root_causes,
        failure_categories,
    )

    if not results.get("stage_v_scalability_complete", False):
        root_causes.append("Stage V scalability is incomplete.")
        corrective_actions.append("Complete Stage V scalability before trusting Stage W benchmarking.")
        failure_categories.append("DEPENDENCY")

    if not results.get("stage_w1_real_engine_benchmarking_framework_complete", False):
        corrective_actions.append("Resolve W.1 benchmark framework blockers or reference-engine selection issues.")

    if not results.get("stage_w2_public_benchmark_source_ownership_complete", False):
        corrective_actions.append("Resolve W.2 source ownership blockers or improve public source confidence.")

    if not results.get("stage_w3_numeric_benchmark_band_ownership_complete", False):
        corrective_actions.append("Resolve W.3 numeric band blockers or review out-of-band LEAF predictions.")

    source_confidence = results.get("real_engine_benchmark_source_owner_confidence")
    if source_confidence is not None:
        evidence.append(f"Source confidence: {source_confidence}")

    reference_engine = results.get("real_engine_benchmark_reference_engine")
    if reference_engine:
        evidence.append(f"Reference engine: {reference_engine}")

    band_rows = results.get("real_engine_benchmark_band_owner_rows")
    if isinstance(band_rows, list):
        out_of_band_count = len([
            row for row in band_rows
            if isinstance(row, dict) and row.get("status") == "OUT_OF_BAND"
        ])
        missing_count = len([
            row for row in band_rows
            if isinstance(row, dict) and row.get("status") == "MISSING_DATA"
        ])
        evidence.append(f"Numeric benchmark rows: {len(band_rows)}")
        evidence.append(f"Out-of-band rows: {out_of_band_count}")
        evidence.append(f"Missing-data rows: {missing_count}")

    if not root_causes:
        root_causes.append("No Stage W benchmark failure causes detected.")
        corrective_actions.append("No corrective action required.")

    unique_root_causes = _dedupe(root_causes)
    unique_corrective_actions = _dedupe(corrective_actions)
    unique_failure_categories = _dedupe(failure_categories)
    unique_evidence = _dedupe(evidence)

    status = "PASS_REAL_ENGINE_BENCHMARK_FAILURE_OWNERSHIP"

    text = build_failure_owner_text(
        status=status,
        root_causes=unique_root_causes,
        corrective_actions=unique_corrective_actions,
        failure_categories=unique_failure_categories,
        evidence=unique_evidence,
        results=results,
    )

    return {
        "real_engine_benchmark_failure_owner_status": status,
        "real_engine_benchmark_failure_owner_text": text,
        "real_engine_benchmark_failure_root_causes": unique_root_causes,
        "real_engine_benchmark_failure_corrective_actions": unique_corrective_actions,
        "real_engine_benchmark_failure_categories": unique_failure_categories,
        "real_engine_benchmark_failure_evidence": unique_evidence,
        "stage_w4_real_engine_benchmark_failure_ownership_complete": True,
    }


def _collect_status_issue(
    results,
    key,
    label,
    category,
    root_causes,
    corrective_actions,
    failure_categories,
):
    value = str(results.get(key, "UNKNOWN")).upper().strip()

    if value in {"UNKNOWN", "", "NONE", "N/A"}:
        root_causes.append(f"{label} did not produce a known status: {key}")
        corrective_actions.append(f"Verify {label} is attached in the foundation pipeline.")
        failure_categories.append(category)
        return

    if _leaf_16u46_is_fail_like(value) or _leaf_16u46_is_fail_like(value) or "INVALID" in value or "ERROR" in value:
        root_causes.append(f"{label} failed: {value}")
        corrective_actions.append(f"Inspect the {label} report and resolve blocking reasons.")
        failure_categories.append(category)
        return

    if _leaf_16u46_is_warn_like(value) or "REVIEW" in value or "LIMITED" in value:
        root_causes.append(f"{label} requires review: {value}")
        corrective_actions.append(f"Review {label} warnings before allowing benchmark completion.")
        failure_categories.append(category)


def _collect_reason_list(
    results,
    key,
    label,
    category,
    root_causes,
    failure_categories,
):
    values = results.get(key, []) or []

    if not isinstance(values, (list, tuple)):
        values = [values]

    for item in values:
        if item in (None, ""):
            continue

        root_causes.append(f"{label}: {item}")
        failure_categories.append(category)


def build_failure_owner_text(
    status,
    root_causes,
    corrective_actions,
    failure_categories,
    evidence,
    results,
):
    lines = [
        "LEAF STAGE W.4 REAL ENGINE BENCHMARK FAILURE OWNERSHIP",
        "=======================================================",
        "",
        f"Status: {status}",
        "",
        "Owned By:",
        "- real_engine_benchmark_failure_owner.py",
        "",
        "Scope:",
        "- Explains Stage W benchmark failures.",
        "- Separates source-confidence failures from numeric-band failures.",
        "- Does not approve final Stage W signoff.",
        "- Does not hide failed benchmark conditions.",
        "",
        "Reference Engine:",
        f"- {results.get('real_engine_benchmark_reference_engine', 'N/A')}",
        "",
        "Failure Categories:",
    ]

    lines.extend([f"- {item}" for item in failure_categories] or ["- None."])

    lines.append("")
    lines.append("Root Causes:")
    lines.extend([f"- {item}" for item in root_causes] or ["- None."])

    lines.append("")
    lines.append("Corrective Actions:")
    lines.extend([f"- {item}" for item in corrective_actions] or ["- None required."])

    lines.append("")
    lines.append("Evidence:")
    lines.extend([f"- {item}" for item in evidence] or ["- None."])

    lines.append("")
    lines.append("Rule:")
    lines.append("- Benchmark failures must be explainable.")
    lines.append("- Source confidence failures, numeric-band failures, and dependency failures must remain separate.")
    lines.append("- Failure ownership does not make benchmarking pass; it only explains failure causes.")

    return "\n".join(lines)


def _dedupe(items):
    output = []

    for item in items:
        if item not in output:
            output.append(item)

    return output
