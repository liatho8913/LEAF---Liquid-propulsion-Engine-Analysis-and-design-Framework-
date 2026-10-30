OWNER_NAME = "REGEN_UNIFIED_ECOSYSTEM_STATE_OWNER"
PHASE = "16A"

PASS_STATUS = "PASS_REGEN_UNIFIED_ECOSYSTEM_STATE_OWNER_PHASE_16A"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_ECOSYSTEM_STATE_OWNER_PHASE_16A"


def attach_regen_unified_ecosystem_state_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_validation_registration_owner_ready") is not True:
        blockers.append("Unified validation registration owner is not ready.")

    state = {
        "owner": OWNER_NAME,
        "phase": PHASE,
        "viewer_count": results.get("unified_regen_registered_viewer_count", 0),
        "report_count": results.get("unified_regen_registered_report_count", 0),
        "validation_count": results.get("unified_regen_registered_validation_count", 0),
        "optimisation_backend_complete": results.get("phase_14_runtime_backend_complete"),
        "viewer_backend_complete": results.get("phase_15a_complete"),
        "candidate_comparison_backend_complete": results.get("phase_15b_complete"),
        "evolution_tree_backend_complete": results.get("phase_15c_complete"),
        "optimisation_report_backend_complete": results.get("phase_15d_complete"),
        "ui_created": False,
        "rendering_performed": False,
        "ecosystem_integrated": True,
    }

    if state["viewer_count"] <= 0:
        blockers.append("No unified viewers registered.")

    if state["report_count"] <= 0:
        blockers.append("No unified reports registered.")

    if state["validation_count"] <= 0:
        blockers.append("No unified validations registered.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS
    state["status"] = status
    state["ready"] = ready

    results.update({
        "regen_unified_ecosystem_state_owner_complete": True,
        "phase_16a_unified_ecosystem_state_owner_complete": True,
        "regen_unified_ecosystem_state_owner_ready": ready,
        "regen_unified_ecosystem_state_owner_status": status,
        "regen_unified_ecosystem_state_owner_blockers": blockers,

        "unified_regen_ecosystem_state": state if ready else {},
        "unified_regen_ecosystem_integrated": ready,
    })

    return results
