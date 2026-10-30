OWNER_NAME = "REGEN_OPTIMISATION_REPORT_BACKEND_MASTER_GATE"
PHASE = "15D"

PASS_STATUS = "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_MASTER_GATE_PHASE_15D"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_REPORT_BACKEND_MASTER_GATE_PHASE_15D"


def attach_regen_optimisation_report_backend_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_optimisation_report_backend_completion_audit_ready") is not True:
        blockers.append("15D optimisation report backend completion audit is not ready.")

    if results.get("regen_optimisation_report_backend_completion_audit_status") != "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D":
        blockers.append("15D optimisation report backend completion audit has not passed.")

    if results.get("phase_16_unified_regen_ecosystem_allowed") is not True:
        blockers.append("Phase 16 unified regen ecosystem was not unlocked.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_optimisation_report_backend_master_gate_complete": True,
        "phase_15d_optimisation_report_backend_master_gate_complete": True,
        "regen_optimisation_report_backend_master_gate_passed": ready,
        "regen_optimisation_report_backend_master_gate_status": status,
        "regen_optimisation_report_backend_master_gate_blockers": blockers,

        "phase_15d_complete": ready,
        "phase_15d_status": (
            "PASS_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D"
            if ready else
            "FAIL_REGEN_OPTIMISATION_REPORT_BACKEND_PHASE_15D"
        ),

        "phase_16_unified_regen_ecosystem_allowed": ready,
    })

    return results
