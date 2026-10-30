try:
    from foundation_dynamic_registry_seed_phase_16o2 import classify_dynamic_key
except Exception:
    classify_dynamic_key = None

from variable_registry import (
    VARIABLES,
    get_output_visibility,
    OUTPUT_VISIBILITY_SCALAR,
)


BAD_MAIN_OUTPUT_FRAGMENTS = (
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
)


def attach_output_ownership_audit(results):
    if not isinstance(results, dict):
        return results

    scalar_keys = []
    non_scalar_registered_keys = []
    unregistered_keys = []
    suspected_pollution_keys = []

    for key, value in sorted(results.items()):
        if value is None:
            continue

        visibility = get_output_visibility(key)

        if key not in VARIABLES:
            dynamic_seed = None
            if classify_dynamic_key is not None:
                dynamic_seed = classify_dynamic_key(key, value)

            if dynamic_seed is not None:
                non_scalar_registered_keys.append(key)
            else:
                unregistered_keys.append(key)
            continue

        if visibility == OUTPUT_VISIBILITY_SCALAR:
            scalar_keys.append(key)

            if _looks_like_non_scalar_output(key, value):
                suspected_pollution_keys.append(key)
        else:
            non_scalar_registered_keys.append(key)

    status = "PASS"

    if suspected_pollution_keys:
        status = "FAIL_MAIN_OUTPUT_POLLUTION"
    elif unregistered_keys:
        status = "WARN_UNREGISTERED_KEYS"

    results["output_ownership_audit_status"] = status
    results["output_ownership_scalar_key_count"] = len(scalar_keys)
    results["output_ownership_non_scalar_registered_key_count"] = len(non_scalar_registered_keys)
    results["output_ownership_unregistered_key_count"] = len(unregistered_keys)
    results["output_ownership_suspected_pollution_keys"] = suspected_pollution_keys
    results["output_ownership_unregistered_keys"] = unregistered_keys
    results["output_ownership_audit_text"] = build_output_ownership_audit_text(
        status=status,
        scalar_keys=scalar_keys,
        non_scalar_registered_keys=non_scalar_registered_keys,
        unregistered_keys=unregistered_keys,
        suspected_pollution_keys=suspected_pollution_keys,
    )

    return results


def _looks_like_non_scalar_output(key, value):
    key_l = str(key).lower()

    if any(fragment in key_l for fragment in BAD_MAIN_OUTPUT_FRAGMENTS):
        return True

    if isinstance(value, (dict, list, tuple)):
        return True

    if isinstance(value, str) and len(value) > 80:
        return True

    return False


def build_output_ownership_audit_text(
        status,
        scalar_keys,
        non_scalar_registered_keys,
        unregistered_keys,
        suspected_pollution_keys,
):
    lines = []
    lines.append("LEAF OUTPUT OWNERSHIP AUDIT")
    lines.append("===========================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Scalar output keys: {len(scalar_keys)}")
    lines.append(f"Registered non-scalar keys: {len(non_scalar_registered_keys)}")
    lines.append(f"Unregistered keys: {len(unregistered_keys)}")
    lines.append(f"Suspected Main Output pollution keys: {len(suspected_pollution_keys)}")
    lines.append("")

    lines.append("Suspected Main Output pollution:")
    if suspected_pollution_keys:
        for key in suspected_pollution_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.append("Unregistered keys:")
    if unregistered_keys:
        for key in unregistered_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None detected.")
    lines.append("")

    lines.append("Interpretation:")
    lines.append("- Main Outputs should contain scalar engineering values only.")
    lines.append("- Reports, diagnostics, validation, recommendations, audit data, and evidence belong outside Main Outputs.")
    lines.append("- This audit checks output ownership hygiene, not physical correctness.")

    return "\n".join(lines)