OWNER_NAME = "REGEN_UNIFIED_ECOSYSTEM_REGISTRY"
PHASE = "16A"

PASS_STATUS = "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"


def attach_regen_unified_ecosystem_registry(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    allowed = results.get("phase_16_unified_regen_ecosystem_allowed") is True
    phase_15d_complete = (
        results.get("phase_15d_complete") is True
        or results.get("phase_15d_status") == "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D"
    )

    if not allowed:
        blockers.append("Phase 16 has not been unlocked by Phase 15D.")

    if not phase_15d_complete:
        blockers.append("Phase 15D optimisation report backend is not complete.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_ecosystem_registry_complete": True,
        "phase_16a_unified_ecosystem_registry_complete": True,
        "regen_unified_ecosystem_registry_ready": ready,
        "regen_unified_ecosystem_registry_status": status,
        "regen_unified_ecosystem_registry_blockers": blockers,
        "regen_unified_ecosystem_registry": {
            "owner": OWNER_NAME,
            "phase": PHASE,
            "status": status,
            "ready": ready,
            "viewer_registration_allowed": ready,
            "report_registration_allowed": ready,
            "validation_registration_allowed": ready,
            "ecosystem_state_allowed": ready,
            "qt_window_allowed": False,
            "rendering_allowed": False,
            "phase_16b_viewer_integration_allowed_next": ready,
        } if ready else None,
    })

    return results
