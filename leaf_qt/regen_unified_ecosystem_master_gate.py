OWNER_NAME = "REGEN_UNIFIED_ECOSYSTEM_MASTER_GATE"
PHASE = "16A"

PASS_STATUS = "PASS_REGEN_UNIFIED_ECOSYSTEM_MASTER_GATE_PHASE_16A"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_ECOSYSTEM_MASTER_GATE_PHASE_16A"


def attach_regen_unified_ecosystem_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_ecosystem_completion_audit_ready") is not True:
        blockers.append("16A unified ecosystem completion audit is not ready.")

    if results.get("regen_unified_ecosystem_completion_audit_status") != "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A":
        blockers.append("16A unified ecosystem completion audit has not passed.")

    if results.get("phase_16b_viewer_integration_allowed") is not True:
        blockers.append("Phase 16B viewer integration was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_ecosystem_master_gate_complete": True,
        "phase_16a_unified_ecosystem_master_gate_complete": True,
        "regen_unified_ecosystem_master_gate_passed": ready,
        "regen_unified_ecosystem_master_gate_status": status,
        "regen_unified_ecosystem_master_gate_blockers": blockers,

        "phase_16a_complete": ready,
        "phase_16a_status": (
            "PASS_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"
            if ready else
            "FAIL_REGEN_UNIFIED_ECOSYSTEM_REGISTRY_PHASE_16A"
        ),

        "phase_16b_viewer_integration_allowed": ready,
    })

    return results
