from benchmark_case_database import get_benchmark_case


COMPARISON_KEY_MAP = {
    "thrust_vacuum_range_n": [
        "vacuum_thrust",
        "thrust_vacuum",
        "thrust",
    ],
    "thrust_sea_level_range_n": [
        "sea_level_thrust",
        "thrust_sea_level",
        "thrust",
    ],
    "specific_impulse_vacuum_range_s": [
        "vacuum_specific_impulse",
        "specific_impulse_vacuum",
        "specific_impulse",
    ],
    "specific_impulse_sea_level_range_s": [
        "sea_level_specific_impulse",
        "specific_impulse_sea_level",
        "specific_impulse",
    ],
    "chamber_pressure_range_pa": [
        "chamber_pressure",
    ],
    "expansion_ratio_range": [
        "expansion_ratio",
    ],
}


def _number(value):
    try:
        if value in (None, "", "N/A", "None"):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_available(results, keys):
    for key in keys:
        value = _number(results.get(key))
        if value is not None:
            return key, value

    return None, None


def _range_check(value, target_range):
    if value is None or target_range is None:
        return {
            "status": "MISSING",
            "error": None,
            "percent_error": None,
            "nearest_bound": None,
        }

    low, high = target_range

    if low <= value <= high:
        return {
            "status": "PASS",
            "error": 0.0,
            "percent_error": 0.0,
            "nearest_bound": None,
        }

    if value < low:
        error = value - low
        percent_error = 100.0 * error / abs(low) if low else None
        severity = "LOW_MAJOR" if percent_error is not None and abs(percent_error) > 15.0 else "LOW_MINOR"

        return {
            "status": severity,
            "error": error,
            "percent_error": percent_error,
            "nearest_bound": low,
        }

    error = value - high
    percent_error = 100.0 * error / abs(high) if high else None
    severity = "HIGH_MAJOR" if percent_error is not None and abs(percent_error) > 15.0 else "HIGH_MINOR"

    return {
        "status": severity,
        "error": error,
        "percent_error": percent_error,
        "nearest_bound": high,
    }


def evaluate_benchmark_case(results, case_key):
    results = results if isinstance(results, dict) else {}

    if case_key is None:
        return {
            "case_key": None,
            "display_name": "No suitable public reference",
            "source_status": "NOT_APPLICABLE",
            "engine_family": "",
            "notes": [
                "No suitable public reference engine was selected for this design scope.",
            ],
            "status": "NO_SUITABLE_REFERENCE",
            "comparisons": [],
            "failed_count": 0,
            "major_failed_count": 0,
            "minor_failed_count": 0,
            "missing_count": 0,
            "comparison_count": 0,
            "summary": (
                "No suitable public reference engine exists for this design scope."
            ),
        }
    case = get_benchmark_case(case_key)

    if not case:
        return {
            "case_key": case_key,
            "status": "UNKNOWN_CASE",
            "comparisons": [],
            "summary": "Benchmark case not found.",
        }

    comparisons = []

    targets = case.get("targets", {})

    for target_key, target_range in targets.items():
        if not target_key.endswith("_range_n") and not target_key.endswith("_range_s") and not target_key.endswith("_range_pa") and not target_key.endswith("_range"):
            continue

        result_keys = COMPARISON_KEY_MAP.get(target_key, [])
        source_key, value = _first_available(results, result_keys)
        range_result = _range_check(value, target_range)

        comparisons.append({
            "target_key": target_key,
            "source_key": source_key,
            "value": value,
            "target_range": target_range,
            "status": range_result["status"],
            "error": range_result["error"],
            "percent_error": range_result["percent_error"],
            "nearest_bound": range_result["nearest_bound"],
        })

    failed = [
        comparison for comparison in comparisons
        if comparison["status"] not in ("PASS",)
    ]

    major_failed = [
        comparison for comparison in comparisons
        if comparison["status"] in ("LOW_MAJOR", "HIGH_MAJOR")
    ]

    minor_failed = [
        comparison for comparison in comparisons
        if comparison["status"] in ("LOW_MINOR", "HIGH_MINOR")
    ]

    missing = [
        comparison for comparison in comparisons
        if comparison["status"] == "MISSING"
    ]

    if not comparisons:
        status = "NO_COMPARABLE_OUTPUTS"
    elif major_failed:
        status = "MAJOR_DEVIATION_FROM_PUBLIC_BENCHMARK"
    elif minor_failed:
        status = "MINOR_DEVIATION_FROM_PUBLIC_BENCHMARK"
    elif missing:
        status = "PARTIAL_BENCHMARK_MISSING_OUTPUTS"
    else:
        status = "WITHIN_PUBLIC_BENCHMARK_ENVELOPE"

    return {
        "case_key": case_key,
        "display_name": case.get("display_name", case_key),
        "source_status": case.get("source_status", "UNKNOWN"),
        "engine_family": case.get("engine_family", ""),
        "notes": case.get("notes", []),
        "status": status,
        "comparisons": comparisons,
        "failed_count": len(failed),
        "major_failed_count": len(major_failed),
        "minor_failed_count": len(minor_failed),
        "missing_count": len(missing),
        "comparison_count": len(comparisons),
    }


def attach_benchmark_evaluation(results, case_key=None):
    if results is None:
        return results

    evaluation = evaluate_benchmark_case(results, case_key)

    results["benchmark_selected_case"] = case_key
    results["benchmark_status"] = evaluation.get("status")
    results["benchmark_failed_count"] = evaluation.get("failed_count")
    results["benchmark_major_failed_count"] = evaluation.get("major_failed_count")
    results["benchmark_minor_failed_count"] = evaluation.get("minor_failed_count")
    results["benchmark_missing_count"] = evaluation.get("missing_count")
    results["benchmark_comparison_count"] = evaluation.get("comparison_count")
    results["benchmark_evaluation"] = evaluation
    results["benchmark_report_text"] = build_benchmark_report_text(evaluation)

    return results


def build_benchmark_report_text(evaluation):
    lines = []
    lines.append("LEAF BENCHMARK COMPARISON REPORT")
    lines.append("================================")
    lines.append("")
    lines.append(f"Case: {evaluation.get('display_name', evaluation.get('case_key'))}")
    lines.append(f"Status: {evaluation.get('status')}")
    lines.append(f"Source status: {evaluation.get('source_status')}")
    lines.append(f"Engine family: {evaluation.get('engine_family')}")
    lines.append("")

    notes = evaluation.get("notes") or []

    if notes:
        lines.append("Notes:")
        for note in notes:
            lines.append(f"- {note}")
        lines.append("")

    comparisons = evaluation.get("comparisons") or []

    if not comparisons:
        lines.append("No comparable LEAF outputs were available.")
        return "\n".join(lines)

    lines.append("Comparisons:")
    lines.append("")

    for comparison in comparisons:
        percent_error = comparison.get("percent_error")

        if percent_error is None:
            percent_text = "N/A"
        else:
            percent_text = f"{percent_error:.3g}%"

        lines.append(f"{comparison.get('target_key')}")
        lines.append(f"- LEAF source key: {comparison.get('source_key')}")
        lines.append(f"- LEAF value: {comparison.get('value')}")
        lines.append(f"- Public target range: {comparison.get('target_range')}")
        lines.append(f"- Nearest bound: {comparison.get('nearest_bound')}")
        lines.append(f"- Absolute error: {comparison.get('error')}")
        lines.append(f"- Percent error from nearest bound: {percent_text}")
        lines.append(f"- Severity: {comparison.get('status')}")
        lines.append("")

    return "\n".join(lines)