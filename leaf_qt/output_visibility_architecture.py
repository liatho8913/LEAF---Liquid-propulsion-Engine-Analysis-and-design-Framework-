try:
    from foundation_dynamic_registry_seed_phase_16o2 import classify_dynamic_key
except Exception:
    classify_dynamic_key = None

from variable_registry import (
    VARIABLES,
    get_output_visibility,
    OUTPUT_VISIBILITY_SCALAR,
    OUTPUT_VISIBILITY_VALIDATION,
    OUTPUT_VISIBILITY_DIAGNOSTIC,
    OUTPUT_VISIBILITY_RECOMMENDATION,
    OUTPUT_VISIBILITY_AXIAL_REPORT,
    OUTPUT_VISIBILITY_INTERNAL,
)


VALID_VISIBILITIES = {
    OUTPUT_VISIBILITY_SCALAR,
    OUTPUT_VISIBILITY_VALIDATION,
    OUTPUT_VISIBILITY_DIAGNOSTIC,
    OUTPUT_VISIBILITY_RECOMMENDATION,
    OUTPUT_VISIBILITY_AXIAL_REPORT,
    OUTPUT_VISIBILITY_INTERNAL,
}


NON_SCALAR_FRAGMENTS = (
    "status",
    "warning",
    "diagnostic",
    "validation",
    "recommendation",
    "report",
    "audit",
    "attachment",
    "pipeline",
    "traceback",
    "error",
    "failure",
    "root_cause",
    "proof",
    "narrative",
    "benchmark",
    "reproduction",
    "startup_health",
    "history",
)


def attach_output_visibility_architecture(results):
    if not isinstance(results, dict):
        return results

    audit = audit_output_visibility_architecture(results)

    for key, value in audit.items():
        results[key] = value

    return results


def audit_output_visibility_architecture(results):
    visibility_counts = {}
    scalar_pollution = []
    unregistered_keys = []
    invalid_visibility_keys = []
    registered_non_scalar_keys = []

    for key, value in sorted(results.items()):
        if value is None:
            continue

        if key not in VARIABLES:
            dynamic_seed = None
            if classify_dynamic_key is not None:
                dynamic_seed = classify_dynamic_key(key, value)

            if dynamic_seed is not None:
                visibility_counts[dynamic_seed.visibility] = (
                    visibility_counts.get(dynamic_seed.visibility, 0) + 1
                )
            else:
                unregistered_keys.append(key)
            continue

        visibility = get_output_visibility(key)
        visibility_counts[visibility] = visibility_counts.get(visibility, 0) + 1

        if visibility not in VALID_VISIBILITIES:
            invalid_visibility_keys.append(key)

        if visibility == OUTPUT_VISIBILITY_SCALAR:
            if _looks_non_scalar(key, value):
                scalar_pollution.append(key)
        else:
            registered_non_scalar_keys.append(key)

    status = "PASS"

    if invalid_visibility_keys:
        status = "FAIL_INVALID_VISIBILITY"
    elif scalar_pollution:
        status = "FAIL_SCALAR_OUTPUT_POLLUTION"
    elif unregistered_keys:
        status = "WARN_UNREGISTERED_KEYS"

    text = build_output_visibility_architecture_text(
        status=status,
        visibility_counts=visibility_counts,
        scalar_pollution=scalar_pollution,
        unregistered_keys=unregistered_keys,
        invalid_visibility_keys=invalid_visibility_keys,
        registered_non_scalar_keys=registered_non_scalar_keys,
    )

    return {
        "output_visibility_architecture_status": status,
        "output_visibility_architecture_visibility_counts": visibility_counts,
        "output_visibility_architecture_scalar_pollution": scalar_pollution,
        "output_visibility_architecture_unregistered_keys": unregistered_keys,
        "output_visibility_architecture_invalid_visibility_keys": invalid_visibility_keys,
        "output_visibility_architecture_non_scalar_registered_count": len(registered_non_scalar_keys),
        "output_visibility_architecture_text": text,
    }


def _looks_non_scalar(key, value):
    key_l = str(key).lower()

    if any(fragment in key_l for fragment in NON_SCALAR_FRAGMENTS):
        return True

    if isinstance(value, (dict, list, tuple)):
        return True

    if isinstance(value, str) and len(value) > 80:
        return True

    return False


def build_output_visibility_architecture_text(
        status,
        visibility_counts,
        scalar_pollution,
        unregistered_keys,
        invalid_visibility_keys,
        registered_non_scalar_keys,
):
    lines = [
        "LEAF OUTPUT VISIBILITY ARCHITECTURE AUDIT",
        "=========================================",
        "",
        f"Status: {status}",
        "",
        "Visibility Counts:",
    ]

    if visibility_counts:
        for visibility, count in sorted(visibility_counts.items()):
            lines.append(f"- {visibility}: {count}")
    else:
        lines.append("- None")

    lines.append("")
    lines.append("Scalar Output Pollution:")

    if scalar_pollution:
        for key in scalar_pollution:
            lines.append(f"- {key}")
    else:
        lines.append("- None detected.")

    lines.append("")
    lines.append("Invalid Visibility Keys:")

    if invalid_visibility_keys:
        for key in invalid_visibility_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None detected.")

    lines.append("")
    lines.append("Unregistered Keys:")

    if unregistered_keys:
        for key in unregistered_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None detected.")

    lines.append("")
    lines.append("Registered Non-Scalar Keys:")
    lines.append(f"- Count: {len(registered_non_scalar_keys)}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- Main Outputs must only contain scalar engineering values.")
    lines.append("- Validation, diagnostics, recommendations, reports, and audit evidence must remain outside Main Outputs.")
    lines.append("- This audit protects LEAF's report ownership and output ownership architecture.")

    return "\n".join(lines)