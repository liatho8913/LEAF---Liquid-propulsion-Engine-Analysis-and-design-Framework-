REFERENCE_ENGINES = {
    "RL10": {
        "scale_class": "MEDIUM_ENGINE",
        "cycle": "EXPANDER",
        "propellant": "LH2/LOX",
        "public_confidence": "MEDIUM",
        "source_type": "PUBLIC_RANGE_SET",
        "source_quality": "MEDIUM",
        "numeric_data_status": "SOURCED_PUBLIC_RANGE",
    },
    "Merlin_1D": {
        "scale_class": "LARGE_ENGINE",
        "cycle": "GAS_GENERATOR",
        "propellant": "RP-1/LOX",
        "public_confidence": "MEDIUM",
        "source_type": "PUBLIC_RANGE_SET",
        "source_quality": "MEDIUM",
        "numeric_data_status": "SOURCED_PUBLIC_RANGE",
    },
    "BE-3": {
        "scale_class": "LARGE_ENGINE",
        "cycle": "TAP_OFF",
        "propellant": "LH2/LOX",
        "public_confidence": "LOW_MEDIUM",
        "source_type": "PUBLIC_METADATA_ONLY",
        "source_quality": "LOW_MEDIUM",
        "numeric_data_status": "RANGE_OR_PLACEHOLDER",
    },
    "BE-4": {
        "scale_class": "VERY_LARGE_ENGINE",
        "cycle": "OX_RICH_STAGED_COMBUSTION",
        "propellant": "CH4/LOX",
        "public_confidence": "LOW_MEDIUM",
        "source_type": "PUBLIC_METADATA_ONLY",
        "source_quality": "LOW_MEDIUM",
        "numeric_data_status": "RANGE_OR_PLACEHOLDER",
    },
    "RS-25": {
        "scale_class": "VERY_LARGE_ENGINE",
        "cycle": "FUEL_RICH_STAGED_COMBUSTION",
        "propellant": "LH2/LOX",
        "public_confidence": "MEDIUM",
        "source_type": "PUBLIC_RANGE_SET",
        "source_quality": "MEDIUM",
        "numeric_data_status": "SOURCED_PUBLIC_RANGE",
    },
    "Raptor": {
        "scale_class": "VERY_LARGE_ENGINE",
        "cycle": "FULL_FLOW_STAGED_COMBUSTION",
        "propellant": "CH4/LOX",
        "public_confidence": "LOW",
        "source_type": "PUBLIC_METADATA_ONLY",
        "source_quality": "LOW",
        "numeric_data_status": "RANGE_OR_PLACEHOLDER",
    },
}


def attach_real_engine_benchmarking_framework(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_real_engine_benchmarking(results)
    results.update(audit)
    return results


def evaluate_real_engine_benchmarking(results):
    blocking = []
    warnings = []

    if (
        "foundation_attachment_benchmark_case" in results
        and
        results.get("foundation_attachment_benchmark_case") is None
    ):
        selected_reference = "UNSELECTED"
        comparison = {
            "reference_engine": selected_reference,
            "comparison_quality": "NONE",
            "comparisons": [],
            "warnings": [],
        }
        status = "NOT_APPLICABLE_NO_SUITABLE_REFERENCE"
        pass_allowed = False
        text = (
            "LEAF REAL-ENGINE BENCHMARKING FRAMEWORK\n"
            "========================================\n\n"
            "Status: NOT_APPLICABLE_NO_SUITABLE_REFERENCE\n"
            "Reference engine: UNSELECTED\n"
            "Comparison quality: NONE\n\n"
            "No suitable public reference engine exists for this design scope."
        )
        return {
            "real_engine_benchmarking_framework_status": status,
            "real_engine_benchmarking_framework_pass_allowed": pass_allowed,
            "real_engine_benchmark_reference_engine": selected_reference,
            "real_engine_benchmark_reference_data": {},
            "real_engine_benchmark_comparison": comparison,
            "real_engine_benchmarking_framework_blocking_reasons": [],
            "real_engine_benchmarking_framework_warning_reasons": [],
            "real_engine_benchmarking_framework_text": text,
            "stage_w1_real_engine_benchmarking_framework_complete": True,
        }

    if not results.get("stage_v_scalability_complete", False):
        blocking.append("Stage V scalability is not complete, so real-engine benchmarking cannot be trusted.")

    selected_reference = str(
        results.get("benchmark_reference_engine")
        or results.get("foundation_attachment_benchmark_case")
        or results.get("selected_benchmark_case")
        or results.get("benchmark_case")
        or ""
    ).strip()

    selected_reference = normalise_reference_engine_key(selected_reference)

    if not selected_reference:
        selected_reference = infer_reference_engine(results)

    reference = REFERENCE_ENGINES.get(selected_reference)

    if reference is None:
        warnings.append("No suitable public reference engine could be selected.")
        selected_reference = "UNSELECTED"
        reference = {}

    comparison = build_reference_comparison(results, selected_reference, reference)

    if comparison["warnings"]:
        warnings.extend(comparison["warnings"])

    if blocking:
        status = "FAIL_REAL_ENGINE_BENCHMARKING_BLOCKED"
        pass_allowed = False
    elif warnings:
        status = "WARN_REAL_ENGINE_BENCHMARKING_REVIEW_REQUIRED"
        pass_allowed = False
    else:
        status = "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK"
        pass_allowed = True

    text = build_benchmarking_framework_text(
        status=status,
        pass_allowed=pass_allowed,
        selected_reference=selected_reference,
        reference=reference,
        comparison=comparison,
        blocking=blocking,
        warnings=warnings,
        results=results,
    )

    return {
        "real_engine_benchmarking_framework_status": status,
        "real_engine_benchmarking_framework_pass_allowed": pass_allowed,
        "real_engine_benchmark_reference_engine": selected_reference,
        "real_engine_benchmark_reference_data": reference,
        "real_engine_benchmark_comparison": comparison,
        "real_engine_benchmarking_framework_blocking_reasons": blocking,
        "real_engine_benchmarking_framework_warning_reasons": warnings,
        "real_engine_benchmarking_framework_text": text,
        "stage_w1_real_engine_benchmarking_framework_complete": pass_allowed,
    }


def infer_reference_engine(results):
    scale = str(results.get("regen_scalability_engine_class", "")).upper()
    propellant = str(results.get("propellant_pair", "")).upper()
    cycle = str(results.get("cycle_type", "")).upper()

    if "FULL" in cycle and "STAGED" in cycle:
        return "Raptor"

    if "CH4" in propellant or "METHANE" in propellant:
        if scale == "VERY_LARGE_ENGINE":
            return "Raptor"
        return "BE-4"

    if "RP" in propellant or "KEROSENE" in propellant:
        return "Merlin_1D"

    if "LH2" in propellant or "HYDROGEN" in propellant:
        if scale == "VERY_LARGE_ENGINE":
            return "RS-25"
        if scale == "LARGE_ENGINE":
            return "BE-3"
        return "RL10"

    if scale == "VERY_LARGE_ENGINE":
        return "RS-25"

    if scale == "LARGE_ENGINE":
        return "Merlin_1D"

    if scale == "MEDIUM_ENGINE":
        return "RL10"

    return ""

def normalise_reference_engine_key(value):
    value = str(value or "").strip()

    if not value:
        return ""

    value_upper = value.upper().replace("-", "_").replace(" ", "_")

    aliases = {
        "RL10": "RL10",
        "RL_10": "RL10",
        "MERLIN": "Merlin_1D",
        "MERLIN_1D": "Merlin_1D",
        "MERLIN_CLASS": "Merlin_1D",
        "BE3": "BE-3",
        "BE_3": "BE-3",
        "BE-3": "BE-3",
        "BE4": "BE-4",
        "BE_4": "BE-4",
        "BE-4": "BE-4",
        "RS25": "RS-25",
        "RS_25": "RS-25",
        "RS-25": "RS-25",
        "RAPTOR": "Raptor",
        "RAPTOR_CLASS": "Raptor",
    }

    return aliases.get(value_upper, value)

def build_reference_comparison(results, selected_reference, reference):
    warnings = []
    notes = []

    if selected_reference == "UNSELECTED":
        return {
            "comparison_quality": "NONE",
            "warnings": ["Benchmark comparison unavailable without selected reference engine."],
            "notes": [],
        }

    scale = str(results.get("regen_scalability_engine_class", "UNKNOWN"))
    reference_scale = reference.get("scale_class", "UNKNOWN")

    if scale != "UNKNOWN_ENGINE_SCALE" and reference_scale != "UNKNOWN" and scale != reference_scale:
        notes.append(
            f"LEAF scale class {scale} differs from reference scale class {reference_scale}; benchmark remains conservative."
        )

    public_confidence = reference.get("public_confidence", "UNKNOWN")

    explicit_low_confidence_case = bool(
        results.get("force_low_confidence_public_benchmark")
        or results.get("low_confidence_public_benchmark")
        or results.get("benchmark_low_confidence_case")
    )

    if public_confidence in {"LOW", "LOW_MEDIUM"}:
        if explicit_low_confidence_case:
            warnings.append(
                f"Reference engine public data confidence is {public_confidence}; comparison must remain conservative."
            )
        else:
            notes.append(
                f"Reference engine public data confidence is {public_confidence}; retained as conservative public-data note."
            )

    notes.append("Benchmarking is range-based and conservative.")
    notes.append("This framework does not infer confidential dimensions or hidden manufacturer data.")
    notes.append("Future W stages should add public source metadata and numeric comparison bands.")

    return {
        "comparison_quality": "PRELIMINARY_PUBLIC_REFERENCE",
        "warnings": warnings,
        "notes": notes,
    }


def build_benchmarking_framework_text(
    status,
    pass_allowed,
    selected_reference,
    reference,
    comparison,
    blocking,
    warnings,
    results,
):
    lines = [
        "LEAF STAGE W.1 REAL ENGINE BENCHMARKING FRAMEWORK",
        "==================================================",
        "",
        f"Status: {status}",
        f"Benchmarking PASS allowed: {pass_allowed}",
        "",
        "Selected Reference Engine:",
        f"- {selected_reference}",
        "",
        "Reference Metadata:",
        f"- Scale class: {reference.get('scale_class', 'N/A')}",
        f"- Cycle: {reference.get('cycle', 'N/A')}",
        f"- Propellant: {reference.get('propellant', 'N/A')}",
        f"- Public confidence: {reference.get('public_confidence', 'N/A')}",
        "",
        "Stage Dependencies:",
        f"- Stage V scalability complete: {results.get('stage_v_scalability_complete', False)}",
        f"- Stage V audit: {results.get('regen_scalability_completion_audit_status', 'N/A')}",
        "",
        "Comparison Quality:",
        f"- {comparison.get('comparison_quality', 'N/A')}",
        "",
        "Blocking Reasons:",
    ]

    lines.extend([f"- {item}" for item in blocking] or ["- None."])

    lines.append("")
    lines.append("Warnings:")
    lines.extend([f"- {item}" for item in warnings] or ["- None."])

    lines.append("")
    lines.append("Notes:")
    lines.extend([f"- {item}" for item in comparison.get("notes", [])] or ["- None."])

    lines.append("")
    lines.append("Rule:")
    lines.append("- Real-engine benchmarking cannot pass until Stage V scalability is complete.")
    lines.append("- Public data confidence must be visible.")
    lines.append("- Benchmarking must remain conservative and range-based.")
    lines.append("- LEAF must not claim confidential exact internal engine data.")

    return "\n".join(lines)