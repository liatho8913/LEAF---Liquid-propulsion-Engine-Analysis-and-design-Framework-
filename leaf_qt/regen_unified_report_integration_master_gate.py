OWNER_NAME = "REGEN_UNIFIED_REPORT_INTEGRATION_MASTER_GATE"
PHASE = "16C"

PASS_STATUS = "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_MASTER_GATE_PHASE_16C"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_REPORT_INTEGRATION_MASTER_GATE_PHASE_16C"


def attach_regen_unified_report_integration_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_report_integration_completion_audit_ready") is not True:
        blockers.append("16C unified report integration completion audit is not ready.")

    if results.get("regen_unified_report_integration_completion_audit_status") != "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C":
        blockers.append("16C unified report integration completion audit has not passed.")

    if results.get("phase_16d_validation_integration_allowed") is not True:
        blockers.append("Phase 16D validation integration was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_report_integration_master_gate_complete": True,
        "phase_16c_unified_report_integration_master_gate_complete": True,
        "regen_unified_report_integration_master_gate_passed": ready,
        "regen_unified_report_integration_master_gate_status": status,
        "regen_unified_report_integration_master_gate_blockers": blockers,

        "phase_16c_complete": ready,
        "phase_16c_status": (
            "PASS_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C"
            if ready else
            "FAIL_REGEN_UNIFIED_REPORT_INTEGRATION_PHASE_16C"
        ),

        "phase_16d_validation_integration_allowed": ready,
    })

    return results
