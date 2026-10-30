"""
PHASE 11A.8
Regen Geometry Candidate Acceptance Owner

Purpose:
    Build a safe acceptance package for candidate regen geometry.

Rules:
    - Does not silently overwrite solver/user inputs.
    - Builds a patch that the UI can explicitly apply later.
    - Records before/after geometry.
    - Produces design-history-ready event data.
"""

REQUIRED_REGEN_PATCH_KEYS = [
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
]


def enforce_non_empty_regen_acceptance_patch(results, patch):
    if patch is None:
        patch = {}

    if not isinstance(patch, dict):
        patch = {}

    fallback_sources = [
        "recommended_regen_candidate_inputs",
        "regen_candidate_recommendation_inputs",
        "recommended_full_engine_regen_candidate_inputs",
        "recommended_regen_geometry_patch",
    ]

    for source_key in fallback_sources:
        source = results.get(source_key)

        if isinstance(source, dict):
            values = source.get("patch_values") if "patch_values" in source else source

            if isinstance(values, dict):
                for key in REQUIRED_REGEN_PATCH_KEYS:
                    if key not in patch and values.get(key) is not None:
                        patch[key] = values.get(key)

    patch_keys = [key for key in REQUIRED_REGEN_PATCH_KEYS if patch.get(key) is not None]

    results["regen_geometry_acceptance_patch_keys"] = patch_keys
    results["regen_geometry_acceptance_patch_key_count"] = len(patch_keys)

    if len(patch_keys) == 0:
        results["regen_geometry_candidate_acceptance_status"] = (
            "FAIL_REGEN_GEOMETRY_EMPTY_ACCEPTANCE_PATCH"
        )
        results["regen_geometry_candidate_acceptance_complete"] = True
        results["regen_geometry_candidate_acceptance_reason"] = (
            "Candidate acceptance owner ran, but no geometry patch keys were available. "
            "This prevents the viewer or solver from showing geometry changes."
        )
    else:
        results["regen_geometry_candidate_acceptance_status"] = (
            "PASS_REGEN_GEOMETRY_ACCEPTANCE_PATCH_READY"
        )
        results["regen_geometry_candidate_acceptance_complete"] = True
        results["regen_geometry_candidate_acceptance_reason"] = (
            f"Candidate acceptance patch contains {len(patch_keys)} geometry keys."
        )

    return patch

def attach_regen_geometry_candidate_acceptance_owner(results):
    if not isinstance(results, dict):
        return results

    audit = build_regen_geometry_candidate_acceptance(results)
    results.update(audit)
    return results


def build_regen_geometry_candidate_acceptance(results):
    results = results if isinstance(results, dict) else {}

    candidate = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry",
        {},
    )

    baseline = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_baseline_geometry",
        {},
    )

    improvement = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_improvement",
        {},
    )

    recommendations = results.get(
        "phase_11a4_regen_geometry_recommendation_engine_owner_recommendations",
        [],
    )

    if not isinstance(candidate, dict):
        candidate = {}

    if not isinstance(baseline, dict):
        baseline = {}

    if not isinstance(improvement, dict):
        improvement = {}

    if not isinstance(recommendations, list):
        recommendations = []

    results[
        "phase_11a8_candidate_geometry_debug_keys"
    ] = sorted(candidate.keys())

    input_patch = _build_input_patch(candidate)

    if not input_patch:
        input_patch = _build_input_patch_from_phase_11a5_candidate(results)

    input_patch = enforce_non_empty_regen_acceptance_patch(results, input_patch)

    changed_keys = improvement.get("changed_keys", [])
    if not isinstance(changed_keys, list):
        changed_keys = []

    patch_key_count = len([
        key for key in REQUIRED_REGEN_PATCH_KEYS
        if input_patch.get(key) is not None
    ])

    acceptance_ready = patch_key_count > 0

    if acceptance_ready:
        engineering_status = "WARN_REGEN_GEOMETRY_CANDIDATE_READY_FOR_USER_ACCEPTANCE"
    elif recommendations:
        engineering_status = "FAIL_REGEN_GEOMETRY_RECOMMENDATION_WITH_EMPTY_ACCEPTANCE_PATCH"
    else:
        engineering_status = "PASS_REGEN_GEOMETRY_NO_CANDIDATE_ACCEPTANCE_REQUIRED"

    owner_status = "PASS_PHASE_11A8_REGEN_GEOMETRY_CANDIDATE_ACCEPTANCE_OWNER"

    acceptance_record = {
        "acceptance_ready": acceptance_ready,
        "input_patch": input_patch,
        "baseline_geometry": baseline,
        "candidate_geometry": candidate,
        "changed_keys": changed_keys,
        "recommendation_count": len(recommendations),
        "source_recommendations": [
            item.get("recommendation_id")
            for item in recommendations
            if isinstance(item, dict)
        ],
        "design_history_event_type": "REGEN_GEOMETRY_CANDIDATE_ACCEPTANCE",
        "design_history_summary": (
            "Candidate regen geometry is ready for explicit user acceptance."
            if acceptance_ready
            else "No candidate geometry changes require acceptance."
        ),
    }

    text = build_regen_geometry_candidate_acceptance_text(
        owner_status=owner_status,
        engineering_status=engineering_status,
        acceptance_record=acceptance_record,
    )

    return {
        "phase_11a8_regen_geometry_candidate_acceptance_owner_complete": True,
        "phase_11a8_regen_geometry_candidate_acceptance_owner_status": owner_status,
        "phase_11a8_regen_geometry_candidate_acceptance_owner_engineering_status": engineering_status,
        "phase_11a8_regen_geometry_candidate_acceptance_owner_ready": acceptance_ready,
        "phase_11a8_regen_geometry_candidate_acceptance_owner_input_patch": input_patch,
        "phase_11a8_regen_geometry_candidate_acceptance_owner_record": acceptance_record,
        "phase_11a8_regen_geometry_candidate_acceptance_owner_text": text,
        "stage_11a_regen_geometry_candidate_acceptance_complete": True,
        "stage_11a_regen_geometry_candidate_acceptance_status": owner_status,
        "stage_11a_regen_geometry_candidate_acceptance_engineering_status": engineering_status,
        "regen_geometry_acceptance_patch_keys": results.get("regen_geometry_acceptance_patch_keys", []),
        "regen_geometry_acceptance_patch_key_count": results.get("regen_geometry_acceptance_patch_key_count", 0),
        "regen_geometry_candidate_acceptance_status": results.get(
            "regen_geometry_candidate_acceptance_status",
            engineering_status,
        ),
        "regen_geometry_candidate_acceptance_complete": True,
        "regen_geometry_candidate_acceptance_reason": results.get(
            "regen_geometry_candidate_acceptance_reason",
            "Candidate acceptance owner completed.",
        ),
        "phase_11a8_candidate_geometry_debug_keys":
            results.get(
                "phase_11a8_candidate_geometry_debug_keys",
                [],
            ),
    }


def _build_input_patch(candidate):
    patch = {}

    mapping = {
        "channel_count": "number_of_coolant_channels",
        "number_of_coolant_channels": "number_of_coolant_channels",

        "channel_width": "coolant_channel_width",
        "coolant_channel_width": "coolant_channel_width",

        "channel_height": "coolant_channel_height",
        "coolant_channel_height": "coolant_channel_height",

        "rib_width": "rib_width",

        "wall_thickness": "hot_gas_wall_thickness",
        "hot_gas_wall_thickness": "hot_gas_wall_thickness",
    }

    for candidate_key, input_key in mapping.items():
        value = candidate.get(candidate_key)

        if value is None:
            continue

        if input_key == "number_of_coolant_channels":
            try:
                value = int(round(float(value)))
            except Exception:
                continue
        else:
            try:
                value = float(value)
            except Exception:
                continue

        patch[input_key] = value

    return patch

def _build_input_patch_from_phase_11a5_candidate(results):
    candidate = results.get(
        "phase_11a5_regen_geometry_apply_recommendation_owner_candidate_geometry",
        {},
    )

    if not isinstance(candidate, dict):
        return {}

    patch = {}

    source_mapping = {
        "channel_count": "number_of_coolant_channels",
        "number_of_coolant_channels": "number_of_coolant_channels",
        "channel_width": "coolant_channel_width",
        "coolant_channel_width": "coolant_channel_width",
        "channel_height": "coolant_channel_height",
        "coolant_channel_height": "coolant_channel_height",
        "rib_width": "rib_width",
        "hot_gas_wall_thickness": "hot_gas_wall_thickness",
        "wall_thickness": "hot_gas_wall_thickness",
    }

    for source_key, patch_key in source_mapping.items():
        value = candidate.get(source_key)

        if value is None:
            continue

        try:
            if patch_key == "number_of_coolant_channels":
                patch[patch_key] = int(round(float(value)))
            else:
                patch[patch_key] = float(value)
        except Exception:
            continue

    return patch

def build_regen_geometry_candidate_acceptance_text(
        owner_status,
        engineering_status,
        acceptance_record,
):
    lines = []
    lines.append("PHASE 11A.8 — REGEN GEOMETRY CANDIDATE ACCEPTANCE OWNER")
    lines.append("=======================================================")
    lines.append("")
    lines.append(f"Owner Status: {owner_status}")
    lines.append(f"Engineering Status: {engineering_status}")
    lines.append("")
    lines.append("Purpose:")
    lines.append("- Build an explicit user-acceptance package for candidate regen geometry.")
    lines.append("- This stage does not silently overwrite solver inputs.")
    lines.append("")
    lines.append(f"Acceptance Ready: {acceptance_record.get('acceptance_ready')}")
    lines.append("")
    lines.append("Input Patch:")
    patch = acceptance_record.get("input_patch", {})
    if patch:
        for key, value in sorted(patch.items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("Changed Keys:")
    changed = acceptance_record.get("changed_keys", [])
    if changed:
        for key in changed:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("Conclusion:")
    lines.append(
        "Candidate geometry can now be safely handed to a future explicit UI apply button."
    )

    return "\n".join(lines)