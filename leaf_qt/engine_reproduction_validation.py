from benchmark_evaluator import evaluate_benchmark_case


def build_engine_reproduction_validation(results, case_key):
    results = results if isinstance(results, dict) else {}

    benchmark = evaluate_benchmark_case(results, case_key)

    if benchmark.get("status") == "NO_SUITABLE_REFERENCE":
        return {
            "engine_reproduction_case": None,
            "engine_reproduction_status": "NOT_APPLICABLE_NO_SUITABLE_REFERENCE",
            "engine_reproduction_confidence": "NOT_APPLICABLE",
            "engine_reproduction_score": None,
            "engine_reproduction_reasons": [
                "No suitable public reference engine exists for this design scope.",
            ],
            "engine_reproduction_report_text": (
                "LEAF ENGINE REPRODUCTION VALIDATION\n"
                "===================================\n\n"
                "Status: NOT_APPLICABLE_NO_SUITABLE_REFERENCE\n"
                "Score: N/A\n"
                "Confidence: NOT_APPLICABLE\n\n"
                "No suitable public reference engine exists for this design scope."
            ),
        }

    if benchmark.get("status") == "UNKNOWN_CASE":
        return {
            "engine_reproduction_case": case_key,
            "engine_reproduction_status": "REPRODUCTION_FAILED",
            "engine_reproduction_confidence": "VERY_LOW",
            "engine_reproduction_score": 0.0,
            "engine_reproduction_reasons": [
                f"Unknown benchmark case: {case_key!r}.",
            ],
            "engine_reproduction_report_text": (
                "LEAF ENGINE REPRODUCTION VALIDATION\n"
                "===================================\n\n"
                "Status: REPRODUCTION_FAILED\n"
                f"Benchmark case: {case_key!r}\n"
                "Reason: Unknown benchmark case."
            ),
        }
    comparisons = benchmark.get("comparisons", [])

    if not comparisons:
        return {
            "engine_reproduction_case": case_key,
            "engine_reproduction_status": "REPRODUCTION_FAILED",
            "engine_reproduction_confidence": "VERY_LOW",
            "engine_reproduction_score": 0.0,
            "engine_reproduction_reasons": [
                "Benchmark evaluation produced no comparable outputs.",
            ],
            "engine_reproduction_report_text": (
                "LEAF ENGINE REPRODUCTION VALIDATION\n"
                "===================================\n\n"
                "Status: REPRODUCTION_FAILED\n"
                "Score: 0.0\n"
                "Reason: No comparable benchmark outputs were available."
            ),
        }

    score = 100.0
    reasons = []

    for comparison in comparisons:
        status = comparison.get("status")
        percent_error = comparison.get("percent_error")

        if status == "PASS":
            continue

        if status == "MISSING":
            score -= 12.5
            reasons.append(f"Missing comparable output for {comparison.get('target_key')}.")
            continue

        if percent_error is not None:
            score -= min(abs(percent_error), 35.0)
            reasons.append(
                f"{comparison.get('target_key')} deviates by {percent_error:.3g}%."
            )

    score = max(0.0, min(100.0, score))

    if score >= 85.0:
        status = "PUBLIC_BEHAVIOUR_REPRODUCED"
        confidence = "HIGH"
    elif score >= 65.0:
        status = "PUBLIC_BEHAVIOUR_APPROXIMATED"
        confidence = "MEDIUM"
    elif score >= 40.0:
        status = "PARTIAL_REPRODUCTION_ONLY"
        confidence = "LOW"
    else:
        status = "REPRODUCTION_FAILED"
        confidence = "VERY_LOW"

    text = build_reproduction_report_text(
        benchmark=benchmark,
        score=score,
        status=status,
        confidence=confidence,
        reasons=reasons,
    )

    return {
        "engine_reproduction_case": case_key,
        "engine_reproduction_status": status,
        "engine_reproduction_confidence": confidence,
        "engine_reproduction_score": score,
        "engine_reproduction_reasons": reasons,
        "engine_reproduction_report_text": text,
    }


def build_reproduction_report_text(benchmark, score, status, confidence, reasons):
    lines = []
    lines.append("LEAF REAL ENGINE REPRODUCTION VALIDATION")
    lines.append("=======================================")
    lines.append("")
    lines.append(f"Benchmark case: {benchmark.get('display_name')}")
    lines.append(f"Reproduction status: {status}")
    lines.append(f"Confidence: {confidence}")
    lines.append(f"Score: {score:.1f}/100")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Check whether LEAF reproduces public engine behaviour.")
    lines.append("- This does not claim access to confidential internal engine design.")
    lines.append("- This validates physical realism, not exact duplication.")
    lines.append("")

    if reasons:
        lines.append("Reasons:")
        for reason in reasons:
            lines.append(f"- {reason}")
        lines.append("")
    else:
        lines.append("No major reproduction deviations recorded.")
        lines.append("")

    lines.append("Benchmark comparison evidence:")
    lines.append("")

    for comparison in benchmark.get("comparisons", []):
        lines.append(f"{comparison.get('target_key')}")
        lines.append(f"- LEAF value: {comparison.get('value')}")
        lines.append(f"- Public range: {comparison.get('target_range')}")
        lines.append(f"- Status: {comparison.get('status')}")
        lines.append(f"- Percent error: {comparison.get('percent_error')}")
        lines.append("")

    return "\n".join(lines)


def attach_engine_reproduction_validation(results, case_key):
    if results is None:
        return results

    reproduction = build_engine_reproduction_validation(results, case_key)

    for key, value in reproduction.items():
        results[key] = value

    return results