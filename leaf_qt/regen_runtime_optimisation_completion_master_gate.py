OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_COMPLETION_MASTER_GATE"
PHASE = "14F"

PASS_STATUS = "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_PHASE_14F"
FAIL_STATUS = "FAIL_REGEN_RUNTIME_OPTIMISATION_COMPLETION_PHASE_14F"


def attach_regen_runtime_optimisation_completion_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    requirements = {
        "regen_runtime_optimisation_completion_registry_ready": "Completion registry is not ready.",
        "regen_runtime_optimisation_completion_audit_ready": "Completion audit is not ready.",
        "regen_runtime_optimisation_completion_validation_owner_ready": "Completion validation owner is not ready.",
        "regen_runtime_optimisation_completion_history_owner_ready": "Completion history owner is not ready.",
        "regen_runtime_optimisation_completion_report_owner_ready": "Completion report owner is not ready.",
    }

    for key, message in requirements.items():
        if results.get(key) is not True:
            blockers.append(message)

    if results.get("regen_runtime_final_live_geometry_committed") is not False:
        blockers.append("Live geometry commit occurred during Phase 14F.")

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_runtime_optimisation_completion_master_gate_complete": True,
        "phase_14f_runtime_optimisation_completion_master_gate_complete": True,
        "regen_runtime_optimisation_completion_master_gate_passed": ready,
        "regen_runtime_optimisation_completion_master_gate_status": status,
        "regen_runtime_optimisation_completion_master_gate_blockers": blockers,

        "phase_14f_complete": ready,
        "phase_14f_status": status,

        "phase_14_runtime_backend_complete": ready,
        "regen_runtime_optimisation_backend_complete": ready,

        "phase_15a_optimisation_viewer_backend_allowed": ready,
        "phase_14_runtime_optimisation_allowed": False,
    })

    return results
