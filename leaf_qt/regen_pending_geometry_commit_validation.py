"""
PHASE 16J.4B — Pending Geometry Commit Validation

Validates that the accepted pending geometry application payload is complete,
safe, traceable, and ready for a later explicit live commit phase.

This phase does NOT overwrite live geometry.
"""

PASS_STATUS = "PASS_REGEN_PENDING_GEOMETRY_COMMIT_VALIDATION_PHASE_16J4B"
FAIL_STATUS = "FAIL_REGEN_PENDING_GEOMETRY_COMMIT_VALIDATION_PHASE_16J4B"

REQUIRED_GEOMETRY_KEYS = (
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
)


def attach_regen_pending_geometry_commit_validation(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    # Programme 48F canonical qualification hard gate.
    _leaf_48f_qualification_state = str(
        results.get("regen_qualification_state") or ""
    ).upper()
    _leaf_48f_qualification_enforcement_ready = bool(
        results.get("regen_qualification_enforcement_ready")
    )
    if (
        _leaf_48f_qualification_enforcement_ready
        and
        _leaf_48f_qualification_state != "QUALIFIED"
    ):
        blockers.append(
            "Regen qualification state is "
            f"{_leaf_48f_qualification_state or 'UNAVAILABLE'}; "
            "QUALIFIED is required for automatic promotion or commit."
        )

    payload = results.get("regen_candidate_acceptance_pending_application_payload")

    if results.get("phase_16j4_complete") is not True:
        blockers.append("Phase 16J.4 candidate acceptance has not passed.")

    if not isinstance(payload, dict) or not payload:
        blockers.append("Pending geometry application payload is missing.")

    accepted_geometry = {}
    previous_geometry = {}

    if isinstance(payload, dict):
        accepted_geometry = payload.get("accepted_geometry") or {}
        previous_geometry = payload.get("previous_geometry") or {}

        if payload.get("commit_state") != "NOT_COMMITTED":
            blockers.append("Pending payload is not in NOT_COMMITTED state.")

        if payload.get("application_mode") != "PENDING_REVIEW":
            blockers.append("Pending payload is not in PENDING_REVIEW mode.")

    if not isinstance(accepted_geometry, dict) or not accepted_geometry:
        blockers.append("Accepted geometry is missing.")

    if isinstance(accepted_geometry, dict):
        for key in REQUIRED_GEOMETRY_KEYS:
            if key not in accepted_geometry:
                blockers.append(f"Accepted geometry is missing required key: {key}")

        for key, value in accepted_geometry.items():
            if key == "number_of_coolant_channels":
                try:
                    if int(value) <= 0:
                        blockers.append("number_of_coolant_channels must be positive.")
                except Exception:
                    blockers.append("number_of_coolant_channels must be numeric.")
            elif isinstance(value, (int, float)):
                if value <= 0:
                    blockers.append(f"{key} must be positive.")

    approval_payload = None

    if not blockers:
        approval_payload = {
            "candidate_id": payload.get("candidate_id"),
            "previous_geometry": previous_geometry,
            "accepted_geometry": accepted_geometry,
            "commit_readiness": "READY_FOR_EXPLICIT_COMMIT",
            "commit_permission": "VALIDATED_PENDING_USER_OR_UI_TRIGGER",
            "live_commit_executed": False,
            "manual_overwrite_executed": False,
            "required_next_phase": "16J.4C",
            "source": "PHASE_16J4B_PENDING_GEOMETRY_COMMIT_VALIDATION",
        }

    status = PASS_STATUS if not blockers else FAIL_STATUS

    results["regen_pending_geometry_commit_validation_complete"] = True
    results["phase_16j4b_complete"] = status == PASS_STATUS
    results["regen_pending_geometry_commit_validation_status"] = status
    results["phase_16j4b_status"] = status
    results["regen_pending_geometry_commit_validation_blockers"] = blockers
    results["regen_pending_geometry_commit_approval_payload"] = approval_payload
    results["regen_pending_geometry_commit_validation_report"] = _build_report(
        status, blockers, approval_payload, accepted_geometry
    )

    results["regen_candidate_geometry_application_allowed"] = status == PASS_STATUS
    results["regen_candidate_manual_overwrite_allowed"] = False
    results["regen_candidate_live_geometry_commit_executed"] = False
    results["phase_16j4c_live_geometry_commit_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, approval_payload, accepted_geometry):
    lines = [
        "LEAF PHASE 16J.4B PENDING GEOMETRY COMMIT VALIDATION",
        "=======================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Validates pending geometry application payload.",
        "- Checks accepted geometry completeness.",
        "- Checks commit state remains safe.",
        "- Produces explicit commit approval payload.",
        "- Does not overwrite live geometry.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Accepted Geometry:")

    if isinstance(accepted_geometry, dict) and accepted_geometry:
        for key in sorted(accepted_geometry.keys()):
            lines.append(f"- {key}: {accepted_geometry[key]}")
    else:
        lines.append("- Not available.")

    lines.extend([
        "",
        "Safety State:",
        "- Commit approval payload: CREATED" if approval_payload else "- Commit approval payload: NOT CREATED",
        "- Live geometry commit: NOT EXECUTED",
        "- Manual overwrite: LOCKED",
        "",
        "Next Required Phase:",
        "- 16J.4C Live Geometry Commit Execution.",
    ])

    return "\n".join(lines)
