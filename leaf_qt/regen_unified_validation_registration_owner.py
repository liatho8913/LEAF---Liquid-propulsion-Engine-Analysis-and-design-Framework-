OWNER_NAME = "REGEN_UNIFIED_VALIDATION_REGISTRATION_OWNER"
PHASE = "16A"

PASS_STATUS = "PASS_REGEN_UNIFIED_VALIDATION_REGISTRATION_OWNER_PHASE_16A"
FAIL_STATUS = "FAIL_REGEN_UNIFIED_VALIDATION_REGISTRATION_OWNER_PHASE_16A"


def attach_regen_unified_validation_registration_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("regen_unified_report_registration_owner_ready") is not True:
        blockers.append("Unified report registration owner is not ready.")

    validations = [
        ("material_validation_pass", "MATERIAL_VALIDATION"),
        ("coating_validation_pass", "COATING_VALIDATION"),
        ("regen_runtime_convergence_validation", "RUNTIME_CONVERGENCE_VALIDATION"),
        ("regen_runtime_optimisation_completion_validation", "RUNTIME_OPTIMISATION_COMPLETION_VALIDATION"),
        ("regen_optimisation_report_backend_completion_audit_ready", "OPTIMISATION_REPORT_BACKEND_AUDIT"),
    ]

    registered = []

    for key, validation_id in validations:
        exists = results.get(key) is not None
        registered.append({
            "validation_id": validation_id,
            "source_key": key,
            "registered": exists,
            "displayed": False,
        })

    missing = [v["validation_id"] for v in registered if v.get("registered") is not True]
    if missing:
        blockers.append("Validation backend registrations missing: " + ", ".join(missing))

    ready = len(blockers) == 0
    status = PASS_STATUS if ready else FAIL_STATUS

    results.update({
        "regen_unified_validation_registration_owner_complete": True,
        "phase_16a_unified_validation_registration_owner_complete": True,
        "regen_unified_validation_registration_owner_ready": ready,
        "regen_unified_validation_registration_owner_status": status,
        "regen_unified_validation_registration_owner_blockers": blockers,

        "unified_regen_registered_validations": registered if ready else [],
        "unified_regen_registered_validation_count": len(registered) if ready else 0,
        "unified_regen_validation_view_created": False,
    })

    return results
