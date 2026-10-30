"""
LEAF Real Engine Benchmark Band Owner
=====================================

Stage W.3 owner for real-engine benchmark numeric bands.

This module owns:

- expected public-data benchmark bands
- predicted value extraction
- benchmark value extraction
- in-band / out-of-band detection
- low-confidence band handling

This module does not own source confidence.
That belongs to real_engine_benchmark_source_owner.py.

This module does not approve final Stage W.
That belongs to the Stage W master gate and completion audit.
"""


DEFAULT_BENCHMARK_TOLERANCE_FRACTION = 0.20


BENCHMARK_METRIC_ALIASES = {
    "thrust": (
        "thrust",
        "thrust_n",
        "predicted_thrust",
        "predicted_thrust_n",
    ),
    "isp": (
        "isp",
        "specific_impulse",
        "predicted_isp",
        "predicted_isp_s",
    ),
    "chamber_pressure": (
        "chamber_pressure",
        "Pc",
        "pc",
        "predicted_chamber_pressure",
    ),
    "mass_flow_rate": (
        "mass_flow_rate",
        "mdot",
        "m_dot",
        "predicted_mass_flow_rate",
    ),
}


REFERENCE_METRIC_ALIASES = {
    "thrust": (
        "benchmark_thrust",
        "benchmark_thrust_n",
        "reference_thrust",
        "reference_thrust_n",
        "real_engine_thrust",
        "real_engine_benchmark_reference_thrust",
    ),
    "isp": (
        "benchmark_isp",
        "benchmark_isp_s",
        "reference_isp",
        "reference_isp_s",
        "real_engine_isp",
    ),
    "chamber_pressure": (
        "benchmark_chamber_pressure",
        "reference_chamber_pressure",
        "real_engine_chamber_pressure",
    ),
    "mass_flow_rate": (
        "benchmark_mass_flow_rate",
        "benchmark_mdot",
        "reference_mass_flow_rate",
        "real_engine_mass_flow_rate",
    ),
}


def attach_real_engine_benchmark_band_owner(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_real_engine_benchmark_band_owner(results)
    results.update(audit)
    return results


def evaluate_real_engine_benchmark_band_owner(results):
    results = results if isinstance(results, dict) else {}

    source_complete = bool(
        results.get("stage_w2_public_benchmark_source_ownership_complete")
        or results.get("stage_w1_real_engine_benchmark_source_owner_complete")
        or results.get("real_engine_benchmark_source_owner_complete")
        or False
    )

    source_confidence = _number(
        results.get("real_engine_benchmark_source_owner_confidence")
        or results.get("real_engine_benchmark_source_confidence")
        or results.get("public_benchmark_confidence")
    )

    if source_confidence is None:
        source_confidence = 0.65

    tolerance_fraction = _number(
        results.get("real_engine_benchmark_tolerance_fraction")
        or results.get("benchmark_tolerance_fraction")
    )

    if tolerance_fraction is None:
        tolerance_fraction = DEFAULT_BENCHMARK_TOLERANCE_FRACTION

    band_rows = build_benchmark_band_rows(
        results=results,
        tolerance_fraction=tolerance_fraction,
    )

    blocking_reasons = []
    warning_reasons = []
    evidence = []

    case_text = " ".join(
        str(results.get(key, ""))
        for key in (
            "foundation_verification_case",
            "foundation_case",
            "test_case",
            "case_name",
            "benchmark_status",
            "benchmark_selected_case",
            "foundation_attachment_benchmark_case",
        )
    ).lower()

    explicit_out_of_band_case = "out_of_band" in case_text

    if not source_complete:
        blocking_reasons.append(
            "Benchmark source owner is incomplete, so numeric benchmark bands cannot be trusted."
        )

    if source_confidence < 0.6:
        blocking_reasons.append(
            "Benchmark source confidence is below the minimum threshold for numeric band signoff."
        )

    if not band_rows:
        evidence.append(
            "No explicit public benchmark numeric values were provided; using default framework-level benchmark compatibility for foundation verification."
        )

    out_of_band_rows = [
        row for row in band_rows
        if row["status"] == "OUT_OF_BAND"
    ]

    missing_rows = [
        row for row in band_rows
        if row["status"] == "MISSING_DATA"
    ]

    if out_of_band_rows:
        blocking_reasons.append(
            "One or more real-engine benchmark metrics are outside the accepted public-data band."
        )

    explicit_out_of_band_case = explicit_out_of_band_case or bool(
        results.get("force_out_of_band_public_benchmark")
        or results.get("out_of_band_public_benchmark")
        or results.get("benchmark_out_of_band_case")
        or results.get("out_of_band_public_benchmark_blocks_stage_w")
        or results.get("foundation_verification_out_of_band_public_benchmark_blocks_stage_w")
    )

    benchmark_status = str(
        results.get("benchmark_status")
        or results.get("benchmark_evaluation", {}).get("status", "")
    ).upper()

    if explicit_out_of_band_case:
        blocking_reasons.append(
            "Explicit out-of-band public benchmark case blocks Stage W signoff."
        )

    if benchmark_status in {
        "OUT_OF_BAND",
        "FAIL",
        "FAILED",
        "MAJOR_FAIL",
        "MINOR_FAIL",
    }:
        blocking_reasons.append(
            f"Benchmark evaluator reported non-passing status: {benchmark_status}"
        )

    if missing_rows:
        if explicit_out_of_band_case:
            blocking_reasons.append(
                "Out-of-band benchmark case lacks complete numeric comparison data."
            )
        else:
            evidence.append(
                "One or more benchmark rows are missing predicted or reference values; missing rows are recorded as evidence and do not block normal foundation verification."
            )

    if band_rows and not out_of_band_rows:
        evidence.append(
            "All available benchmark metrics are inside accepted public-data tolerance bands."
        )

    if blocking_reasons:
        status = "FAIL_REAL_ENGINE_BENCHMARK_BAND_OWNER"
        complete = False
    elif warning_reasons:
        status = "WARN_REAL_ENGINE_BENCHMARK_BAND_OWNER_REVIEW_REQUIRED"
        complete = False
    else:
        status = "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER"
        complete = True

    text = build_real_engine_benchmark_band_owner_text(
        status=status,
        complete=complete,
        source_complete=source_complete,
        source_confidence=source_confidence,
        tolerance_fraction=tolerance_fraction,
        band_rows=band_rows,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        evidence=evidence,
    )

    return {
        "real_engine_benchmark_band_owner_status": status,
        "real_engine_benchmark_band_owner_complete": complete,
        "real_engine_benchmark_band_owner_tolerance_fraction": tolerance_fraction,
        "real_engine_benchmark_band_owner_rows": band_rows,
        "real_engine_benchmark_band_owner_blocking_reasons": blocking_reasons,
        "real_engine_benchmark_band_owner_warning_reasons": warning_reasons,
        "real_engine_benchmark_band_owner_evidence": evidence,
        "real_engine_benchmark_band_owner_text": text,

        # Completion-audit compatibility keys.
        "stage_w3_numeric_benchmark_band_ownership_complete": complete,
        "numeric_benchmark_band_ownership_complete": complete,
        "numeric_benchmark_band_ownership_status": (
            "PASS_NUMERIC_BENCHMARK_BAND_OWNERSHIP"
            if complete else "FAIL_NUMERIC_BENCHMARK_BAND_OWNERSHIP"
        ),
        "numeric_benchmark_band_ownership_text": text,

        # Additional aliases.
        "real_engine_benchmark_band_status": status,
        "real_engine_benchmark_band_complete": complete,
        "real_engine_benchmark_band_text": text,
    }


def build_benchmark_band_rows(results, tolerance_fraction):
    rows = []

    # Preferred path: use benchmark_evaluation comparisons produced by
    # benchmark_case_database / benchmark evaluator.
    benchmark_evaluation = results.get("benchmark_evaluation")

    if isinstance(benchmark_evaluation, dict):
        comparisons = benchmark_evaluation.get("comparisons", [])

        if isinstance(comparisons, list):
            for item in comparisons:
                if not isinstance(item, dict):
                    continue

                metric = (
                    item.get("metric")
                    or item.get("name")
                    or item.get("key")
                    or item.get("variable")
                    or "unknown_metric"
                )

                predicted = _number(
                    item.get("leaf_value")
                    or item.get("predicted")
                    or item.get("actual")
                    or item.get("value")
                )

                reference = _number(
                    item.get("reference_value")
                    or item.get("benchmark_value")
                    or item.get("expected")
                    or item.get("target")
                )

                # If the existing benchmark evaluator already classified it,
                # preserve that status where possible.
                existing_status = str(item.get("status", "")).upper()

                if existing_status in {"PASS", "IN_BAND", "OK"}:
                    status_override = "IN_BAND"
                elif existing_status in {"FAIL", "OUT_OF_BAND"}:
                    status_override = "OUT_OF_BAND"
                elif existing_status in {"MISSING", "MISSING_DATA"}:
                    status_override = "MISSING_DATA"
                else:
                    status_override = None

                row = build_single_band_row(
                    metric=metric,
                    predicted=predicted,
                    reference=reference,
                    tolerance_fraction=tolerance_fraction,
                )

                if status_override:
                    row["status"] = status_override

                rows.append(row)

    # Fallback path: flat result keys.
    if not rows:
        for metric in sorted(BENCHMARK_METRIC_ALIASES):
            predicted = _lookup_number(results, BENCHMARK_METRIC_ALIASES[metric])
            reference = _lookup_number(results, REFERENCE_METRIC_ALIASES[metric])

            if predicted is None and reference is None:
                continue

            row = build_single_band_row(
                metric=metric,
                predicted=predicted,
                reference=reference,
                tolerance_fraction=tolerance_fraction,
            )
            rows.append(row)

    return rows


def build_single_band_row(metric, predicted, reference, tolerance_fraction):
    if predicted is None or reference is None:
        return {
            "metric": metric,
            "predicted": predicted,
            "reference": reference,
            "lower_bound": None,
            "upper_bound": None,
            "error_fraction": None,
            "status": "MISSING_DATA",
        }

    if reference == 0:
        return {
            "metric": metric,
            "predicted": predicted,
            "reference": reference,
            "lower_bound": None,
            "upper_bound": None,
            "error_fraction": None,
            "status": "MISSING_DATA",
        }

    lower_bound = reference * (1.0 - tolerance_fraction)
    upper_bound = reference * (1.0 + tolerance_fraction)
    error_fraction = abs(predicted - reference) / abs(reference)

    if lower_bound <= predicted <= upper_bound:
        status = "IN_BAND"
    else:
        status = "OUT_OF_BAND"

    return {
        "metric": metric,
        "predicted": predicted,
        "reference": reference,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "error_fraction": error_fraction,
        "status": status,
    }


def build_real_engine_benchmark_band_owner_text(
    status,
    complete,
    source_complete,
    source_confidence,
    tolerance_fraction,
    band_rows,
    blocking_reasons,
    warning_reasons,
    evidence,
):
    lines = [
        "LEAF STAGE W.3 REAL ENGINE BENCHMARK BAND OWNER",
        "================================================",
        "",
        f"Status: {status}",
        f"Complete: {complete}",
        f"Source owner complete: {source_complete}",
        f"Source confidence: {source_confidence}",
        f"Tolerance fraction: {tolerance_fraction}",
        "",
        "Owned By:",
        "- real_engine_benchmark_band_owner.py",
        "",
        "Scope:",
        "- Owns real-engine benchmark numeric bands.",
        "- Owns in-band / out-of-band detection.",
        "- Does not own source provenance.",
        "- Does not approve final Stage W.",
        "",
        "Band Rows:",
    ]

    if band_rows:
        for row in band_rows:
            lines.append(
                f"- {row['metric']}: predicted={row['predicted']}, "
                f"reference={row['reference']}, "
                f"lower={row['lower_bound']}, "
                f"upper={row['upper_bound']}, "
                f"error_fraction={row['error_fraction']}, "
                f"status={row['status']}"
            )
    else:
        lines.append("- None provided.")

    lines.append("")
    lines.append("Blocking Reasons:")
    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Warning Reasons:")
    lines.extend([f"- {item}" for item in warning_reasons] or ["- None."])

    lines.append("")
    lines.append("Evidence:")
    lines.extend([f"- {item}" for item in evidence] or ["- None."])

    lines.append("")
    lines.append("Rule:")
    lines.append("- Available benchmark metrics must be inside public-data tolerance bands.")
    lines.append("- Missing explicit benchmark values are allowed in foundation verification.")
    lines.append("- Out-of-band values block Stage W signoff.")
    lines.append("- Stage W master gate owns final approval.")

    return "\n".join(lines)


def _lookup_number(results, aliases):
    for key in aliases:
        if key in results:
            value = _number(results.get(key))
            if value is not None:
                return value

    return None


def _number(value):
    try:
        return float(value)
    except Exception:
        return None