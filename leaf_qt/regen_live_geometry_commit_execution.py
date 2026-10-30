"""
PHASE 16J.4C — Live Geometry Commit Execution

Purpose:
- Consume the 16J.4B commit approval payload.
- Apply accepted geometry into the active results/input dictionary.
- Record before/after commit audit.
- Mark live geometry commit as executed.

This is the first controlled live-geometry commit phase.
"""

import copy
from datetime import datetime, timezone

PASS_STATUS = "PASS_REGEN_LIVE_GEOMETRY_COMMIT_EXECUTION_PHASE_16J4C"
FAIL_STATUS = "FAIL_REGEN_LIVE_GEOMETRY_COMMIT_EXECUTION_PHASE_16J4C"

COMMITTABLE_GEOMETRY_KEYS = (
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
    "outer_wall_thickness",
    "coating_thickness",
    "bond_coat_thickness",
    "coolant_channel_aspect_ratio",
)


def attach_regen_live_geometry_commit_execution(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    approval = results.get("regen_pending_geometry_commit_approval_payload")

    if results.get("phase_16j4b_complete") is not True:
        blockers.append("Phase 16J.4B pending geometry commit validation has not passed.")

    if not isinstance(approval, dict) or not approval:
        blockers.append("Commit approval payload is missing.")

    accepted_geometry = {}
    previous_geometry = {}

    if isinstance(approval, dict):
        if approval.get("commit_readiness") != "READY_FOR_EXPLICIT_COMMIT":
            blockers.append("Commit approval payload is not READY_FOR_EXPLICIT_COMMIT.")

        if approval.get("live_commit_executed") is not False:
            blockers.append("Commit approval payload already indicates a live commit.")

        accepted_geometry = approval.get("accepted_geometry") or {}
        previous_geometry = approval.get("previous_geometry") or {}

    if not isinstance(accepted_geometry, dict) or not accepted_geometry:
        blockers.append("Accepted geometry is missing from commit approval payload.")

    committed_keys = []
    before_after = []

    if not blockers:
        for key in COMMITTABLE_GEOMETRY_KEYS:
            if key not in accepted_geometry:
                continue

            before = copy.deepcopy(results.get(key))
            after = copy.deepcopy(accepted_geometry[key])

            results[key] = after
            committed_keys.append(key)

            before_after.append({
                "key": key,
                "before": before,
                "after": after,
                "changed": before != after,
            })

        results["regen_geometry_active_source"] = "ACCEPTED_RECOMMENDED_CANDIDATE"
        results["regen_geometry_active_candidate_id"] = approval.get("candidate_id")
        results["regen_geometry_last_commit_phase"] = "16J.4C"

    status = PASS_STATUS if not blockers else FAIL_STATUS

    audit_record = None
    if status == PASS_STATUS:
        audit_record = {
            "event_type": "REGEN_LIVE_GEOMETRY_COMMIT_EXECUTED",
            "phase": "16J.4C",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "candidate_id": approval.get("candidate_id"),
            "committed_keys": committed_keys,
            "before_after": before_after,
            "previous_geometry_snapshot": previous_geometry,
            "accepted_geometry_snapshot": accepted_geometry,
        }

    report = _build_report(status, blockers, approval, committed_keys, before_after)

    results["regen_live_geometry_commit_execution_complete"] = True
    results["phase_16j4c_complete"] = status == PASS_STATUS
    results["regen_live_geometry_commit_execution_status"] = status
    results["phase_16j4c_status"] = status
    results["regen_live_geometry_commit_execution_blockers"] = blockers
    results["regen_live_geometry_commit_audit_record"] = audit_record
    results["regen_live_geometry_commit_report"] = report

    results["regen_candidate_live_geometry_commit_executed"] = status == PASS_STATUS
    results["regen_candidate_manual_overwrite_allowed"] = False
    results["regen_candidate_geometry_application_allowed"] = status == PASS_STATUS

    results["phase_16j4d_solver_regeneration_after_commit_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, approval, committed_keys, before_after):
    candidate_id = approval.get("candidate_id") if isinstance(approval, dict) else None

    lines = [
        "LEAF PHASE 16J.4C LIVE GEOMETRY COMMIT EXECUTION",
        "===================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Applies validated accepted candidate geometry into active geometry keys.",
        "- Records before/after commit audit.",
        "- Marks live geometry commit as executed.",
        "- Does not regenerate solver outputs yet.",
        "",
        f"Candidate ID: {candidate_id}",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Committed Keys:")

    if committed_keys:
        for key in committed_keys:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Before/After:")

    if before_after:
        for change in before_after:
            lines.append(
                f"- {change['key']}: {change['before']} -> {change['after']}"
            )
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Safety State:",
        "- Live geometry commit: EXECUTED" if committed_keys and not blockers else "- Live geometry commit: NOT EXECUTED",
        "- Manual overwrite: LOCKED",
        "",
        "Next Required Phase:",
        "- 16J.4D Solver Regeneration After Commit.",
    ])

    return "\n".join(lines)
