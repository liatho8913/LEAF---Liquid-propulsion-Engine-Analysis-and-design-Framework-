"""
PHASE 11B.2K
Regen Autonomous Geometry Commit History Owner
"""


def attach_regen_autonomous_geometry_commit_history_owner(results):
    if not isinstance(results, dict):
        return results

    history = results.get("regen_autonomous_geometry_commit_history", [])

    if not isinstance(history, list):
        history = []

    review = results.get("regen_autonomous_geometry_commit_review", {})
    if not isinstance(review, dict):
        review = {}

    staged = results.get("regen_autonomous_geometry_staged_candidate", {})
    if not isinstance(staged, dict):
        staged = {}

    history.append({
        "status": results.get("regen_autonomous_geometry_commit_status"),
        "ready": results.get("regen_autonomous_geometry_commit_ready"),
        "decision": review.get("decision"),
        "safe_to_stage": review.get("safe_to_stage"),
        "patch_keys": review.get("patch_keys"),
        "issues": review.get("issues"),
        "warnings": review.get("warnings"),
        "requires_user_acceptance": staged.get("requires_user_acceptance"),
        "committed": staged.get("committed"),
    })

    results.update({
        "regen_autonomous_geometry_commit_history_complete": True,
        "phase_11b_2k_regen_autonomous_geometry_commit_history_complete": True,
        "regen_autonomous_geometry_commit_history_status": (
            "PASS_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_HISTORY_STORED"
        ),
        "regen_autonomous_geometry_commit_history": history,
        "regen_autonomous_geometry_commit_history_count": len(history),
    })

    return results