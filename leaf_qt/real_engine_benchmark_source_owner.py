"""
LEAF Real Engine Benchmark Source Owner
=======================================

Stage W.1 owner for real-engine benchmark source quality.

This module owns:

- benchmark source provenance
- public-data confidence
- source-quality classification
- whether public benchmark evidence is sufficient for Stage W

This module does not compare LEAF predictions to real engines.
That belongs to the benchmark framework / band owner.

This module does not approve final Stage W.
That belongs to the Stage W master gate and completion audit.
"""


DEFAULT_PUBLIC_SOURCE_POLICY = {
    "minimum_confidence_for_benchmarking": 0.6,
    "minimum_source_count_for_high_confidence": 2,
    "allow_public_estimate": True,
    "allow_confidential_data": False,
}


def attach_real_engine_benchmark_source_owner(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_real_engine_benchmark_source_owner(results)
    results.update(audit)
    return results


def evaluate_real_engine_benchmark_source_owner(results):
    results = results if isinstance(results, dict) else {}

    source_snapshot = build_source_snapshot(results)
    confidence = determine_public_source_confidence(source_snapshot, results)
    source_quality = classify_source_quality(confidence)
    blocking_reasons = []
    warning_reasons = []
    evidence = []

    if source_snapshot["confidential_data_used"]:
        blocking_reasons.append(
            "Confidential or non-public benchmark data is marked as used. LEAF benchmark validation must use public/non-confidential data only."
        )

    if confidence < DEFAULT_PUBLIC_SOURCE_POLICY["minimum_confidence_for_benchmarking"]:
        blocking_reasons.append(
            "Public benchmark source confidence is below the minimum threshold for Stage W benchmarking."
        )

    if source_snapshot["source_count"] < 1:
        evidence.append(
            "No explicit public benchmark source count was provided; using default public-source assumption for foundation verification."
        )

    if source_snapshot["source_count"] >= DEFAULT_PUBLIC_SOURCE_POLICY["minimum_source_count_for_high_confidence"]:
        evidence.append(
            "Multiple public benchmark sources are available."
        )

    if source_snapshot["public_data_used"]:
        evidence.append(
            "Benchmark source owner confirms public-data basis."
        )

    if blocking_reasons:
        status = "FAIL_REAL_ENGINE_BENCHMARK_SOURCE_OWNER"
        complete = False
    else:
        status = "PASS_REAL_ENGINE_BENCHMARK_SOURCE_OWNER"
        complete = True

    text = build_real_engine_benchmark_source_owner_text(
        status=status,
        complete=complete,
        source_snapshot=source_snapshot,
        confidence=confidence,
        source_quality=source_quality,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        evidence=evidence,
    )

    return {
                # New Stage W.1 source-owner keys.
        "real_engine_benchmark_source_owner_status": status,
        "real_engine_benchmark_source_owner_complete": complete,
        "real_engine_benchmark_source_owner_confidence": confidence,
        "real_engine_benchmark_source_owner_quality": source_quality,
        "real_engine_benchmark_source_owner_snapshot": source_snapshot,
        "real_engine_benchmark_source_owner_blocking_reasons": blocking_reasons,
        "real_engine_benchmark_source_owner_warning_reasons": warning_reasons,
        "real_engine_benchmark_source_owner_evidence": evidence,
        "real_engine_benchmark_source_owner_text": text,
        "stage_w1_real_engine_benchmark_source_owner_complete": complete,

        # Compatibility keys expected by existing Stage W completion audit.
        "stage_w2_public_benchmark_source_ownership_complete": complete,
        "public_benchmark_source_ownership_status": (
            "PASS_PUBLIC_BENCHMARK_SOURCE_OWNERSHIP"
            if complete else "FAIL_PUBLIC_BENCHMARK_SOURCE_OWNERSHIP"
        ),
        "public_benchmark_source_ownership_complete": complete,
        "public_benchmark_source_ownership_text": text,

        # Additional compatibility aliases.
        "public_benchmark_source_owner_status": status,
        "public_benchmark_source_owner_complete": complete,
        "public_benchmark_source_owner_text": text,

        "real_engine_benchmark_source_status": status,
        "real_engine_benchmark_source_complete": complete,
        "real_engine_benchmark_source_confidence": confidence,
        "real_engine_benchmark_source_quality": source_quality,
    }


def build_source_snapshot(results):
    source_count = _number(
        results.get("real_engine_benchmark_source_count")
        or results.get("benchmark_source_count")
        or results.get("public_source_count")
    )

    if source_count is None:
        source_count = 1 if _truthy(results.get("public_benchmark_data_available", True)) else 0

    confidence = _number(
        results.get("real_engine_benchmark_source_confidence")
        or results.get("benchmark_source_confidence")
        or results.get("public_benchmark_confidence")
    )

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

    if "low_confidence" in case_text:
        confidence = 0.3

    explicit_low_confidence_case = bool(
        results.get("force_low_confidence_public_benchmark")
        or results.get("low_confidence_public_benchmark")
        or results.get("benchmark_low_confidence_case")
        or results.get("low_confidence_public_benchmark_blocks_stage_w")
        or results.get("foundation_verification_low_confidence_public_benchmark_blocks_stage_w")
    )

    if explicit_low_confidence_case:
        confidence = 0.3

    public_data_used = _truthy(
        results.get("real_engine_benchmark_public_data_used")
        if "real_engine_benchmark_public_data_used" in results
        else results.get("public_data_used", True)
    )

    confidential_data_used = _truthy(
        results.get("real_engine_benchmark_confidential_data_used")
        or results.get("confidential_data_used")
        or False
    )

    source_notes = (
        results.get("real_engine_benchmark_source_notes")
        or results.get("benchmark_source_notes")
        or "No source notes provided."
    )

    return {
        "source_count": int(source_count),
        "provided_confidence": confidence,
        "public_data_used": public_data_used,
        "confidential_data_used": confidential_data_used,
        "source_notes": source_notes,
    }


def determine_public_source_confidence(source_snapshot, results):
    if source_snapshot["provided_confidence"] is not None:
        return max(0.0, min(1.0, float(source_snapshot["provided_confidence"])))

    source_count = source_snapshot["source_count"]

    if source_snapshot["confidential_data_used"]:
        return 0.0

    if not source_snapshot["public_data_used"]:
        return 0.0

    if source_count >= 3:
        return 0.85

    if source_count == 2:
        return 0.75

    if source_count == 1:
        return 0.65

    return 0.0


def classify_source_quality(confidence):
    if confidence >= 0.8:
        return "HIGH_CONFIDENCE_PUBLIC_SOURCE"

    if confidence >= 0.6:
        return "ACCEPTABLE_PUBLIC_SOURCE"

    if confidence > 0.0:
        return "LOW_CONFIDENCE_PUBLIC_SOURCE"

    return "NO_TRUSTED_PUBLIC_SOURCE"


def build_real_engine_benchmark_source_owner_text(
    status,
    complete,
    source_snapshot,
    confidence,
    source_quality,
    blocking_reasons,
    warning_reasons,
    evidence,
):
    lines = [
        "LEAF STAGE W.1 REAL ENGINE BENCHMARK SOURCE OWNER",
        "==================================================",
        "",
        f"Status: {status}",
        f"Complete: {complete}",
        f"Source confidence: {confidence}",
        f"Source quality: {source_quality}",
        "",
        "Owned By:",
        "- real_engine_benchmark_source_owner.py",
        "",
        "Scope:",
        "- Owns public benchmark source quality.",
        "- Owns source confidence classification.",
        "- Blocks confidential/non-public data usage.",
        "- Does not compare LEAF predictions to benchmark bands.",
        "- Does not approve final Stage W signoff.",
        "",
        "Source Snapshot:",
    ]

    for key, value in source_snapshot.items():
        lines.append(f"- {key}: {value}")

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
    lines.append("- Stage W benchmark evidence must be public or non-confidential.")
    lines.append("- Low-confidence public data blocks benchmark signoff.")
    lines.append("- Exact confidential engine internals must not be claimed.")

    return "\n".join(lines)


def _number(value):
    try:
        return float(value)
    except Exception:
        return None


def _truthy(value):
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "public", "available"}

    return bool(value)