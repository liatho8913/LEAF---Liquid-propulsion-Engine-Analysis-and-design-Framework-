"""
LEAF Regen Candidate Application Owner
=====================================

PHASE 11B.1F

Builds a safe geometry application patch from the recommended regen candidate.

This module DOES:
- consume the recommended regen candidate
- build a geometry patch
- compare original values to recommended values
- validate patch completeness
- publish application readiness

This module DOES NOT:
- overwrite active engine inputs
- mutate manual geometry
- re-run the solver
- claim the applied geometry is final
"""


REQUIRED_PATCH_KEYS = [
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
]


def attach_regen_candidate_application_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_application_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_application_owner(results):
    requested_candidate_id = results.get(
        "regen_candidate_selector_requested_candidate_id"
    )

    user_selected_candidate = results.get(
        "regen_candidate_selector_user_selected_candidate"
    )

    recommendation = results.get(
        "regen_candidate_recommendation"
    )

    blocking_reasons = []

    application_candidate = None
    selection_source = None

    if requested_candidate_id:
        if not isinstance(
            user_selected_candidate,
            dict,
        ) or not user_selected_candidate:
            blocking_reasons.append(
                "An explicit Generated Design was requested, "
                "but the canonical selector did not authorise it."
            )

        elif (
            str(
                user_selected_candidate.get(
                    "candidate_id"
                )
            )
            !=
            str(
                requested_candidate_id
            )
        ):
            blocking_reasons.append(
                "Canonical selector candidate ID does not match "
                "the requested Generated Design."
            )

        elif (
            user_selected_candidate.get(
                "validation_status"
            )
            !=
            "PASS_CANDIDATE_VALIDATION"
        ):
            blocking_reasons.append(
                "Explicit Generated Design is not marked as "
                "canonically validated."
            )

        else:
            application_candidate = (
                user_selected_candidate
            )

            selection_source = (
                "EXPLICIT_QUALIFIED_GENERATED_DESIGN"
            )

    else:
        if recommendation:
            application_candidate = (
                recommendation
            )

            selection_source = (
                "CANONICAL_RECOMMENDATION"
            )
        else:
            blocking_reasons.append(
                "No regen candidate recommendation is available."
            )

    patch = None

    if application_candidate:
        patch = build_application_patch(
            results,
            application_candidate,
        )

        blocking_reasons.extend(
            validate_application_patch(
                patch
            )
        )

    if blocking_reasons:
        status = "FAIL_REGEN_CANDIDATE_APPLICATION_BLOCKED"
        ready = False
    else:
        status = "PASS_REGEN_CANDIDATE_APPLICATION_PATCH_READY"
        ready = True

    report = build_application_report(
        status=status,
        ready=ready,
        patch=patch,
        blocking_reasons=blocking_reasons,
        recommendation=application_candidate,
    )

    return {
        "regen_candidate_application_owner_complete": True,
        "phase_11b_1f_regen_candidate_application_owner_complete": True,
        "regen_candidate_application_owner_status": status,
        "regen_candidate_application_ready": ready,
        "regen_candidate_application_blocking_reasons": blocking_reasons,
        "regen_candidate_application_selection_source": selection_source,
        "regen_candidate_application_candidate_id": (
            application_candidate.get(
                "candidate_id"
            )
            if isinstance(
                application_candidate,
                dict,
            )
            else None
        ),
        "regen_candidate_application_patch": patch,
        "regen_candidate_application_patch_keys": (
            list((patch or {}).get("patch_values", {}).keys()) if patch else []
        ),
        "regen_candidate_application_report": report,

        # Explicit safety locks.
        "regen_candidate_geometry_application_allowed": ready,
        "regen_candidate_geometry_applied": False,
        "regen_candidate_manual_overwrite_allowed": False,
        "regen_candidate_requires_user_apply_action": True,

        # Compatibility aliases.
        "recommended_regen_geometry_patch": patch,
        "recommended_regen_geometry_patch_ready": ready,
        "recommended_regen_geometry_patch_report": report,
    }



def _optional_material_patch_keys():
    return (
        "selected_material",
        "selected_material_name",
        "material_name",
        "hot_gas_liner",
        "selected_material_max_temperature",
        "material_max_wall_temperature",
        "wall_thermal_conductivity",
        "material_yield_strength",
        "material_density",
        "material_source_validation_mode",
        "material_source_validation_score",
        "material_source_has_citation",
        "material_source_has_temperature_table",
        "material_source_is_placeholder",
        "material_source_quality",
        "_leaf_candidate_material_search_active",
    )


def build_application_patch(results, recommendation):
    inputs = recommendation.get("inputs") or {}

    patch_values = {}

    for key in (
        tuple(
            REQUIRED_PATCH_KEYS
        )
        +
        _optional_material_patch_keys()
    ):
        if key in inputs:
            patch_values[key] = inputs.get(key)

    original_values = {
        "number_of_coolant_channels": _first_existing(
            results,
            ["number_of_coolant_channels", "coolant_channel_count"],
        ),
        "coolant_channel_width": _first_existing(
            results,
            ["coolant_channel_width", "regen_channel_width"],
        ),
        "coolant_channel_height": _first_existing(
            results,
            ["coolant_channel_height", "regen_channel_height"],
        ),
        "rib_width": _first_existing(
            results,
            ["rib_width", "regen_rib_width"],
        ),
        "hot_gas_wall_thickness": _first_existing(
            results,
            ["hot_gas_wall_thickness", "regen_wall_thickness"],
        ),
    }

    for key in (
        _optional_material_patch_keys()
    ):
        original_values[key] = (
            results.get(
                key
            )
        )

    changes = {}

    for key, new_value in patch_values.items():
        old_value = original_values.get(key)
        changes[key] = {
            "old": old_value,
            "new": new_value,
            "changed": old_value != new_value,
            "ratio": _ratio(new_value, old_value),
        }

    return {
        "source": "regen_candidate_application_owner.py",
        "phase": "PHASE_11B_1F",
        "candidate_id": recommendation.get("candidate_id"),
        "patch_status": "PATCH_BUILT_REQUIRES_USER_APPLICATION",
        "patch_values": patch_values,
        "original_values": original_values,
        "changes": changes,
        "application_mode": "NON_DESTRUCTIVE_PATCH_ONLY",
        "requires_user_action": True,
        "geometry_applied": False,
    }


def validate_application_patch(patch):
    reasons = []

    if not patch:
        reasons.append("Application patch was not built.")
        return reasons

    patch_values = patch.get("patch_values") or {}

    for key in REQUIRED_PATCH_KEYS:
        value = patch_values.get(key)

        if value is None:
            reasons.append(f"Patch missing required key: {key}.")
        elif _num(value) is None:
            reasons.append(f"Patch value is not numeric: {key}.")
        elif _num(value) <= 0:
            reasons.append(f"Patch value must be positive: {key}={value}.")

    material_search_active = (
        patch_values.get(
            "_leaf_candidate_material_search_active"
        )
        is True
    )

    if material_search_active:
        required_material_identity = (
            "selected_material",
            "selected_material_name",
            "material_name",
            "hot_gas_liner",
        )

        for key in (
            required_material_identity
        ):
            value = patch_values.get(
                key
            )

            if not str(
                value
                or ""
            ).strip():
                reasons.append(
                    f"Material patch missing "
                    f"identity key: {key}."
                )

        selected = str(
            patch_values.get(
                "selected_material"
            )
            or ""
        ).strip()

        for alias_key in (
            "selected_material_name",
            "material_name",
            "hot_gas_liner",
        ):
            alias = str(
                patch_values.get(
                    alias_key
                )
                or ""
            ).strip()

            if (
                selected
                and alias
                and alias != selected
            ):
                reasons.append(
                    "Material patch identity mismatch: "
                    f"{alias_key}={alias!r}, "
                    f"selected_material={selected!r}."
                )

        for key in (
            "selected_material_max_temperature",
            "material_max_wall_temperature",
            "wall_thermal_conductivity",
            "material_yield_strength",
            "material_density",
        ):
            value = patch_values.get(
                key
            )

            if _num(
                value
            ) is None:
                reasons.append(
                    f"Material patch value is "
                    f"not numeric: {key}."
                )

            elif _num(
                value
            ) <= 0:
                reasons.append(
                    f"Material patch value must "
                    f"be positive: {key}={value}."
                )

        source_mode = str(
            patch_values.get(
                "material_source_validation_mode"
            )
            or ""
        ).strip()

        if not source_mode:
            reasons.append(
                "Material patch has no source "
                "validation mode."
            )

        if not isinstance(
            patch_values.get(
                "material_source_is_placeholder"
            ),
            bool,
        ):
            reasons.append(
                "Material patch placeholder state "
                "must be boolean."
            )

    if not patch.get("candidate_id"):
        reasons.append("Patch missing candidate ID.")

    return reasons


def build_application_report(
        status,
        ready,
        patch,
        blocking_reasons,
        recommendation,
):
    lines = [
        "LEAF PHASE 11B.1F REGEN CANDIDATE APPLICATION OWNER",
        "===================================================",
        "",
        f"Status: {status}",
        f"Application patch ready: {ready}",
        f"Candidate ID: {patch.get('candidate_id') if patch else None}",
        "",
        "Scope:",
        (
            "- Builds a non-destructive design application patch "
            "(geometry plus optional canonical material bundle)."
        ),
        "- Validates patch completeness.",
        "- Does not overwrite manual geometry.",
        "- Does not re-run the solver.",
        "",
        "Blocking Reasons:",
    ]

    if blocking_reasons:
        for reason in blocking_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- None.")

    if patch:
        lines.extend([
            "",
            "Patch Values:",
        ])

        for key, value in (patch.get("patch_values") or {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "Original Values:",
        ])

        for key, value in (patch.get("original_values") or {}).items():
            lines.append(f"- {key}: {value}")

        lines.extend([
            "",
            "Changes:",
        ])

        for key, payload in (patch.get("changes") or {}).items():
            lines.append(
                f"- {key}: old={payload.get('old')}, "
                f"new={payload.get('new')}, "
                f"changed={payload.get('changed')}, "
                f"ratio={payload.get('ratio')}"
            )

    lines.extend([
        "",
        "Safety State:",
        "- Geometry applied: False",
        "- Manual overwrite allowed: False",
        "- Requires explicit future application action: True",
    ])

    return "\n".join(lines)


def _first_existing(results, keys):
    for key in keys:
        if key in results and results.get(key) is not None:
            return results.get(key)
    return None


def _num(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _ratio(new_value, old_value):
    try:
        if old_value in (None, 0):
            return None
        return float(new_value) / float(old_value)
    except Exception:
        return None