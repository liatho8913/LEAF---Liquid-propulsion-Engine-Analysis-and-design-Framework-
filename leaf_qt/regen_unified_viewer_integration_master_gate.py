OWNER_NAME = "REGEN_UNIFIED_VIEWER_INTEGRATION_MASTER_GATE"
PHASE = "16B"

PASS_STATUS = "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_MASTER_GATE_PHASE_16B"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VIEWER_INTEGRATION_MASTER_GATE_PHASE_16B"


def attach_regen_unified_viewer_integration_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_viewer_integration_completion_audit_ready") is not True:
        blockers.append("16B unified viewer integration completion audit is not ready.")

    if results.get("regen_unified_viewer_integration_completion_audit_status") != "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B":
        blockers.append("16B unified viewer integration completion audit has not passed.")

    if results.get("phase_16c_report_integration_allowed") is not True:
        blockers.append("Phase 16C report integration was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_viewer_integration_master_gate_complete": True,
        "phase_16b_unified_viewer_integration_master_gate_complete": True,
        "regen_unified_viewer_integration_master_gate_passed": ready,
        "regen_unified_viewer_integration_master_gate_status": status,
        "regen_unified_viewer_integration_master_gate_blockers": blockers,

        "phase_16b_complete": ready,
        "phase_16b_status": (
            "PASS_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B"
            if ready else
            "FAIL_REGEN_UNIFIED_VIEWER_INTEGRATION_PHASE_16B"
        ),

        "phase_16c_report_integration_allowed": ready,
    })

    return results
