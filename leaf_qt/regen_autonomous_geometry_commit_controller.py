"""
PHASE 11B.2K
Regen Autonomous Geometry Commit Controller

Reviews autonomous geometry rewrite patches and decides whether they are
safe to stage for commit.

Does NOT:
- run solver
- directly modify live geometry
- permanently commit geometry
"""


ALLOWED_PATCH_KEYS = {
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
    "inner_wall_thickness",
    "channel_count",
    "number_of_channels",
    "number_of_coolant_channels",
    "coolant_flow_fraction",
}


MIN_FEATURE_SIZE_M = 2.5e-4
MAX_RELATIVE_CHANGE = 0.35


def attach_regen_autonomous_geometry_commit_controller(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_autonomous_geometry_commit_controller(results)
    results.update(payload)
    return results


def build_regen_autonomous_geometry_commit_controller(results):
    blockers = []

    base_geometry = _extract_base_geometry(
        results
    )


    application_allowed = bool(
        results.get(
            "regen_candidate_geometry_application_allowed"
        )
    )


    patch = _extract_patch_from_results(
        results
    )


    if not application_allowed:

        blockers.append(
            "Canonical candidate application owner has not authorised "
            "automatic geometry staging."
        )


    if not patch:

        blockers.append(
            "No authoritative candidate application patch is available."
        )


    commit_review = review_geometry_commit_patch(
        patch=patch,
        base_geometry=base_geometry,
    )


    if blockers:

        status = (
            "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_BLOCKED"
        )

        ready = False

        reason = (
            "Autonomous geometry commit controller is blocked."
        )


    elif not commit_review[
        "safe_to_stage"
    ]:

        status = (
            "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_REVIEW_FAILED"
        )

        ready = False

        reason = commit_review[
            "reason"
        ]


    else:

        status = (
            "PASS_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_READY"
        )

        ready = True

        reason = commit_review[
            "reason"
        ]


    staged_candidate = build_staged_candidate(
        patch=patch,
        base_geometry=base_geometry,
        commit_review=commit_review,
        ready=ready,
    )


    report = build_geometry_commit_report(
        status=status,
        ready=ready,
        blockers=blockers,
        commit_review=commit_review,
        staged_candidate=staged_candidate,
    )


    return {
        "regen_autonomous_geometry_commit_complete": True,
        "phase_11b_2k_regen_autonomous_geometry_commit_complete": True,
        "regen_autonomous_geometry_commit_status": status,
        "regen_autonomous_geometry_commit_ready": ready,
        "regen_autonomous_geometry_commit_reason": reason,
        "regen_autonomous_geometry_commit_blockers": blockers,
        "regen_autonomous_geometry_commit_review": commit_review,
        "regen_autonomous_geometry_staged_candidate": staged_candidate,
        "regen_autonomous_geometry_commit_report": report,

        "regen_geometry_commit_candidate_ready": ready,
        "regen_geometry_commit_candidate_patch": (
            patch
            if ready
            else {}
        ),
        "regen_geometry_commit_staged_geometry": (
            staged_candidate.get(
                "staged_geometry",
                {},
            )
        ),
        "regen_geometry_commit_decision": (
            commit_review[
                "decision"
            ]
        ),
        "regen_geometry_commit_requires_user_acceptance": ready,

        "regen_autonomous_geometry_commit_solver_executed": False,
        "regen_autonomous_geometry_commit_live_geometry_modified": False,
        "regen_autonomous_geometry_commit_candidate_committed": False,
    }



def _extract_ranked_candidate(results):
    candidate_keys = [
        "regen_selected_ranked_candidate",
        "regen_selected_candidate",
        "regen_candidate_ranking_selected_candidate",
        "regen_candidate_ranking_winner",
        "regen_candidate_ranking_best_candidate",
        "regen_best_ranked_candidate",
        "regen_best_candidate",
        "regen_autonomous_geometry_best_candidate",
    ]

    for key in candidate_keys:
        value = results.get(key)
        if isinstance(value, dict) and value:
            return value

    list_keys = [
        "regen_candidate_ranking",
        "regen_candidate_rankings",
        "regen_ranked_candidates",
        "regen_geometry_candidates",
        "regen_candidate_population",
    ]

    for key in list_keys:
        value = results.get(key)
        if isinstance(value, list) and value:
            for item in value:
                if isinstance(item, dict) and item:
                    return item

    return {}


def _extract_base_geometry(results):
    application_patch = (
        results.get("regen_candidate_application_patch")
        or results.get("recommended_regen_geometry_patch")
        or {}
    )

    original_values = (
        application_patch.get("original_values", {})
        if isinstance(application_patch, dict)
        else {}
    )

    base_geometry = (
        original_values
        or results.get("regen_manual_geometry")
        or results.get("regen_current_geometry")
        or results.get("regen_geometry_current")
        or results.get("regen_geometry_baseline")
        or {}
    )

    return dict(base_geometry) if isinstance(base_geometry, dict) else {}


def _extract_patch_from_results(results):
    """
    Resolve only the canonical application-authorised final patch.

    Autonomous rewrite state and ranked-candidate state are not final
    user-facing staging authority.
    """

    if not bool(
        results.get(
            "regen_candidate_geometry_application_allowed"
        )
    ):
        return {}


    application_patch = (
        results.get(
            "regen_candidate_application_patch"
        )
        or results.get(
            "recommended_regen_geometry_patch"
        )
        or
        {}
    )


    if not isinstance(
        application_patch,
        dict,
    ):
        return {}


    patch_values = (
        application_patch.get(
            "patch_values"
        )
        or
        {}
    )


    return _filter_geometry_payload(
        patch_values
    )


def _extract_patch_from_ranked_candidate(candidate):
    for key in [
        "staged_geometry",
        "geometry",
        "candidate_geometry",
        "patch",
        "recommended_geometry",
        "regen_geometry",
    ]:
        value = candidate.get(key)
        filtered = _filter_geometry_payload(value)
        if filtered:
            return filtered

    return _filter_geometry_payload(candidate)


def _extract_base_geometry_from_ranked_candidate(candidate):
    for key in [
        "base_geometry",
        "manual_geometry",
        "rollback_geometry",
        "current_geometry",
    ]:
        value = candidate.get(key)
        if isinstance(value, dict) and value:
            return dict(value)

    return {}


def _filter_geometry_payload(payload):
    if not isinstance(payload, dict):
        return {}

    filtered = {}

    alias_map = {
        "number_of_coolant_channels": "number_of_coolant_channels",
        "number_of_channels": "number_of_coolant_channels",
        "channel_count": "number_of_coolant_channels",
    }

    for key, value in payload.items():
        mapped_key = alias_map.get(key, key)

        if mapped_key not in ALLOWED_PATCH_KEYS:
            continue

        numeric = _num(value, None)
        if numeric is None:
            continue

        filtered[mapped_key] = numeric

    return filtered

def review_geometry_commit_patch(patch, base_geometry):
    issues = []
    warnings = []

    if not patch:
        issues.append("Rewrite patch is empty.")

    for key, value in patch.items():
        if key not in ALLOWED_PATCH_KEYS:
            issues.append(f"Patch key is not allowed: {key}")
            continue

        numeric = _num(value, None)
        if numeric is None:
            issues.append(f"Patch value is not numeric: {key}={value}")
            continue

        if key in {"channel_count", "number_of_channels"}:
            if numeric < 1:
                issues.append(f"Channel count must be >= 1: {key}={value}")
        else:
            if numeric < MIN_FEATURE_SIZE_M:
                issues.append(
                    f"Feature below minimum size: {key}={value}"
                )

        base_value = _num(base_geometry.get(key), None)

        if base_value is not None and base_value > 0.0:
            relative_change = abs(numeric - base_value) / base_value

            if relative_change > MAX_RELATIVE_CHANGE:
                issues.append(
                    f"Patch change too large for safe staging: "
                    f"{key} relative_change={relative_change:.3f}"
                )
            elif relative_change > 0.20:
                warnings.append(
                    f"Patch change is large but stageable: "
                    f"{key} relative_change={relative_change:.3f}"
                )

    if issues:
        decision = "BLOCK_COMMIT"
        safe_to_stage = False
        reason = "Autonomous geometry commit review failed."
    else:
        decision = "STAGE_FOR_USER_ACCEPTANCE"
        safe_to_stage = True
        reason = "Autonomous geometry patch is safe to stage."

    return {
        "decision": decision,
        "safe_to_stage": safe_to_stage,
        "reason": reason,
        "issues": issues,
        "warnings": warnings,
        "patch_keys": sorted(patch.keys()),
    }


def build_staged_candidate(patch, base_geometry, commit_review, ready):
    staged_geometry = dict(base_geometry)

    if ready:
        staged_geometry.update(patch)

    return {
        "ready": ready,
        "decision": commit_review["decision"],
        "base_geometry": dict(base_geometry),
        "patch": dict(patch) if ready else {},
        "staged_geometry": staged_geometry if ready else {},
        "rollback_geometry": dict(base_geometry),
        "requires_user_acceptance": ready,
        "committed": False,
    }


def build_geometry_commit_report(
        status,
        ready,
        blockers,
        commit_review,
        staged_candidate,
):
    lines = [
        "LEAF PHASE 11B.2K REGEN AUTONOMOUS GEOMETRY COMMIT CONTROLLER",
        "==============================================================",
        "",
        f"Status: {status}",
        f"Ready: {ready}",
        f"Decision: {commit_review.get('decision')}",
        "",
        "Reason:",
        f"- {commit_review.get('reason')}",
        "",
        "Patch Keys:",
    ]

    for key in commit_review.get("patch_keys", []) or []:
        lines.append(f"- {key}")

    lines.extend(["", "Issues:"])

    if commit_review.get("issues"):
        for issue in commit_review.get("issues"):
            lines.append(f"- {issue}")
    else:
        lines.append("- None.")

    lines.extend(["", "Warnings:"])

    if commit_review.get("warnings"):
        for warning in commit_review.get("warnings"):
            lines.append(f"- {warning}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Staged Candidate:",
        f"- Ready: {staged_candidate.get('ready')}",
        f"- Requires user acceptance: "
        f"{staged_candidate.get('requires_user_acceptance')}",
        f"- Committed: {staged_candidate.get('committed')}",
        "",
        "Blockers:",
    ])

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Safety State:",
        "- Solver executed: False",
        "- Live geometry modified: False",
        "- Candidate committed: False",
    ])

    return "\n".join(lines)


def _num(value, default):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default