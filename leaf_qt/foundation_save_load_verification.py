import json
from copy import deepcopy
from core.architecture.io import read_json_artifact, write_json_artifact


REQUIRED_KEY_GROUPS = {
    "stage_u_completion": [
        "stage_u_regen_validation_complete",
    ],
    "stage_v_completion": [
        "stage_v_scalability_complete",
        "stage_v_complete",
        "stage_v_regen_scalability_complete",
        "stage_v_regen_scalability_completion_audit_complete",
        "stage_v5_regen_scalability_completion_audit_complete",
    ],
    "stage_w_completion": [
        "stage_w_real_engine_benchmarking_complete",
        "stage_w_real_engine_benchmark_complete",
        "stage_w_complete",
        "stage_w5_real_engine_benchmark_completion_audit_complete",
        "stage_w6_real_engine_benchmark_completion_audit_complete",
    ],
    "stage_u_status": [
        "regen_completion_audit_status",
    ],
    "stage_v_status": [
        "regen_scalability_completion_audit_status",
    ],
    "stage_w_status": [
        "real_engine_benchmark_completion_audit_status",
    ],
    "stage_w1_framework_status": [
        "real_engine_benchmarking_framework_status",
    ],
    "stage_w2_source_owner_status": [
        "real_engine_benchmark_source_owner_status",
    ],
    "stage_w3_band_owner_status": [
        "real_engine_benchmark_band_owner_status",
    ],
    "stage_w4_failure_owner_status": [
        "real_engine_benchmark_failure_owner_status",
    ],
    "stage_w5_master_gate_status": [
        "real_engine_benchmark_master_gate_status",
    ],
    "foundation_attachment_status": [
        "foundation_attachment_pipeline_status",
    ],
    "result_key_audit_status": [
        "foundation_result_key_audit_status",
    ],
    "stage_u_report": [
        "regen_completion_audit_text",
    ],
    "stage_v_report": [
        "regen_scalability_completion_audit_text",
    ],
    "stage_w_report": [
        "real_engine_benchmark_completion_audit_text",
    ],
    "stage_w1_framework_report": [
        "real_engine_benchmarking_framework_text",
    ],
    "stage_w2_source_owner_report": [
        "real_engine_benchmark_source_owner_text",
    ],
    "stage_w3_band_owner_report": [
        "real_engine_benchmark_band_owner_text",
    ],
    "stage_w4_failure_owner_report": [
        "real_engine_benchmark_failure_owner_text",
    ],
    "stage_w5_master_gate_report": [
        "real_engine_benchmark_master_gate_text",
    ],
}


OPTIONAL_PRESERVED_KEYS = [
    "regen_scalability_completion_audit_blocking_reasons",
    "real_engine_benchmark_completion_audit_blocking_reasons",
    "regen_scalability_completion_audit_warning_reasons",
    "real_engine_benchmark_completion_audit_warning_reasons",
    "real_engine_benchmarking_framework_blocking_reasons",
    "real_engine_benchmark_source_owner_blocking_reasons",
    "real_engine_benchmark_band_owner_blocking_reasons",
    "real_engine_benchmark_master_gate_blocking_reasons",

    "real_engine_benchmarking_framework_warning_reasons",
    "real_engine_benchmark_source_owner_warning_reasons",
    "real_engine_benchmark_band_owner_warning_reasons",
    "real_engine_benchmark_master_gate_warning_reasons",

    "real_engine_benchmark_reference_engine",
    "real_engine_benchmark_reference_data",
    "real_engine_benchmark_comparison",
    "real_engine_benchmark_source_owner_snapshot",
    "real_engine_benchmark_band_owner_rows",
    "real_engine_benchmark_master_gate_owner_summary",
    "real_engine_benchmark_completion_audit_checks",
]


def verify_foundation_save_load_roundtrip(results):
    if not isinstance(results, dict):
        return {
            "foundation_save_load_verification_status": "FAIL_INVALID_RESULTS",
            "foundation_save_load_verified": False,
            "foundation_save_load_verification_text": (
                "Foundation save/load verification requires a result dictionary."
            ),
        }

    before = deepcopy(results)

    try:
        encoded = json.dumps(before, default=str)
        loaded = json.loads(encoded)
    except Exception as exc:
        return {
            "foundation_save_load_verification_status": "FAIL_SERIALISATION_ERROR",
            "foundation_save_load_verified": False,
            "foundation_save_load_verification_error": str(exc),
            "foundation_save_load_verification_text": (
                "Foundation save/load serialisation failed.\n"
                f"Error: {exc}"
            ),
        }

    missing_groups = []
    missing_keys = []
    changed = []
    checked_keys = []

    for group_name, aliases in REQUIRED_KEY_GROUPS.items():
        existing_aliases = [
            key for key in aliases
            if key in before
        ]

        if not existing_aliases:
            missing_groups.append({
                "group": group_name,
                "accepted_keys": aliases,
            })
            continue

        for key in existing_aliases:
            checked_keys.append(key)

            if key not in loaded:
                missing_keys.append(key)
                continue

            if loaded.get(key) != before.get(key):
                changed.append({
                    "key": key,
                    "before": before.get(key),
                    "after": loaded.get(key),
                })

    for key in OPTIONAL_PRESERVED_KEYS:
        if key not in before:
            continue

        checked_keys.append(key)

        if key not in loaded:
            missing_keys.append(key)
            continue

        if loaded.get(key) != before.get(key):
            changed.append({
                "key": key,
                "before": before.get(key),
                "after": loaded.get(key),
            })

    if missing_groups or missing_keys or changed:
        status = "FAIL_FOUNDATION_SAVE_LOAD_VERIFICATION"
        verified = False
    else:
        status = "PASS_FOUNDATION_SAVE_LOAD_VERIFICATION"
        verified = True

    return {
        "foundation_save_load_verification_status": status,
        "foundation_save_load_verified": verified,
        "foundation_save_load_missing_groups": missing_groups,
        "foundation_save_load_missing_keys": missing_keys,
        "foundation_save_load_changed_values": changed,
        "foundation_save_load_checked_keys": checked_keys,
        "foundation_save_load_checked_key_count": len(checked_keys),
        "foundation_save_load_verification_text": build_foundation_save_load_report(
            status=status,
            verified=verified,
            missing_groups=missing_groups,
            missing_keys=missing_keys,
            changed=changed,
            checked_keys=checked_keys,
        ),
    }


def build_foundation_save_load_report(
    status,
    verified,
    missing_groups,
    missing_keys,
    changed,
    checked_keys,
):
    lines = [
        "LEAF FOUNDATION SAVE/LOAD VERIFICATION",
        "======================================",
        "",
        f"Status: {status}",
        f"Foundation save/load verified: {verified}",
        f"Checked key count: {len(checked_keys)}",
        "",
        "Checked Keys:",
    ]

    lines.extend([f"- {key}" for key in checked_keys] or ["- None."])

    lines.append("")
    lines.append("Missing Required Key Groups:")

    if missing_groups:
        for item in missing_groups:
            lines.append(f"- {item['group']}")
            lines.append("  accepted keys:")
            for key in item["accepted_keys"]:
                lines.append(f"  - {key}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Missing Keys:")
    lines.extend([f"- {key}" for key in missing_keys] or ["- None."])

    lines.append("")
    lines.append("Changed Values:")

    if changed:
        for item in changed:
            lines.append(f"- {item['key']}")
            lines.append(f"  before: {item['before']}")
            lines.append(f"  after: {item['after']}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Rule:")
    lines.append("- Foundation state must survive serialisation.")
    lines.append("- Required key groups must have at least one valid alias.")
    lines.append("- Compatibility aliases are accepted, but not all aliases are required.")
    lines.append("- Optional detailed report fields are checked only when present.")

    return "\n".join(lines)
