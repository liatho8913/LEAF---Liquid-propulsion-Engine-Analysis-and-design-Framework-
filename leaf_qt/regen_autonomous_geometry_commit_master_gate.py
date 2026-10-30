"""
PHASE 11B.2K
Regen Autonomous Geometry Commit Master Gate
"""


def attach_regen_autonomous_geometry_commit_master_gate(results):
    if not isinstance(results, dict):
        return results

    controller_complete = bool(
        results.get("regen_autonomous_geometry_commit_complete")
    )
    history_complete = bool(
        results.get("regen_autonomous_geometry_commit_history_complete")
    )
    report_complete = bool(
        results.get("regen_autonomous_geometry_commit_report_complete")
    )
    controller_ready = bool(
        results.get("regen_autonomous_geometry_commit_ready")
    )

    review = results.get("regen_autonomous_geometry_commit_review")
    if not isinstance(review, dict):
        review = {}

    staged = results.get("regen_autonomous_geometry_staged_candidate")
    if not isinstance(staged, dict):
        staged = {}

    decision = review.get("decision")
    patch = staged.get("patch")
    staged_geometry = staged.get("staged_geometry")
    rollback_geometry = staged.get("rollback_geometry")

    solver_executed = bool(
        results.get("regen_autonomous_geometry_commit_solver_executed")
    )
    live_modified = bool(
        results.get("regen_autonomous_geometry_commit_live_geometry_modified")
    )
    committed = bool(
        results.get("regen_autonomous_geometry_commit_candidate_committed")
    )

    if not controller_complete:
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_CONTROLLER_INCOMPLETE"
        ready = False
        reason = "Autonomous geometry commit controller has not completed."
    elif not history_complete:
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_HISTORY_INCOMPLETE"
        ready = False
        reason = "Autonomous geometry commit history owner has not completed."
    elif not report_complete:
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_REPORT_INCOMPLETE"
        ready = False
        reason = "Autonomous geometry commit report owner has not completed."
    elif not controller_ready:
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_NOT_READY"
        ready = False
        reason = "Autonomous geometry commit controller is not ready."
    elif decision != "STAGE_FOR_USER_ACCEPTANCE":
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_INVALID_DECISION"
        ready = False
        reason = f"Invalid commit decision: {decision}"
    elif not isinstance(patch, dict) or not patch:
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_EMPTY_PATCH"
        ready = False
        reason = "No patch exists to stage."
    elif not isinstance(staged_geometry, dict) or not staged_geometry:
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_EMPTY_STAGED_GEOMETRY"
        ready = False
        reason = "No staged geometry exists."
    elif not isinstance(rollback_geometry, dict) or not rollback_geometry:
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_EMPTY_ROLLBACK"
        ready = False
        reason = "No rollback geometry exists."
    elif solver_executed or live_modified or committed:
        status = "FAIL_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_SAFETY_LOCK_VIOLATION"
        ready = False
        reason = "Autonomous geometry commit violated passive safety locks."
    else:
        status = "PASS_REGEN_AUTONOMOUS_GEOMETRY_COMMIT_GATE_READY"
        ready = True
        reason = "Autonomous geometry commit candidate is safely staged."

    results.update({
        "regen_autonomous_geometry_commit_master_gate_complete": True,
        "phase_11b_2k_regen_autonomous_geometry_commit_master_gate_complete": True,
        "regen_autonomous_geometry_commit_master_gate_status": status,
        "regen_autonomous_geometry_commit_master_gate_ready": ready,
        "regen_autonomous_geometry_commit_master_gate_reason": reason,
    })

    return results