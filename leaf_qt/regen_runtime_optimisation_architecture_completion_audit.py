from __future__ import annotations

OWNER_NAME = "REGEN_RUNTIME_OPTIMISATION_ARCHITECTURE_COMPLETION_AUDIT"

PASS_STATUS = (
    "PASS_REGEN_RUNTIME_OPTIMISATION_COMPLETION_AUDIT_PHASE_11D5"
)

BLOCK_STATUS = (
    "BLOCK_REGEN_RUNTIME_OPTIMISATION_COMPLETION_AUDIT_PHASE_11D5"
)


def _blocked_payload():
    return {
        "phase_11d_5_regen_runtime_optimisation_completion_audit_complete": False,
        "regen_runtime_optimisation_completion_audit_ready": False,
        "regen_runtime_optimisation_completion_audit_status": BLOCK_STATUS,
        "phase_11d_complete": False,
        "regen_runtime_optimisation_architecture_complete": False,
        "phase_11e_runtime_execution_architecture_allowed": False,
        "regen_runtime_execution_architecture_allowed": False,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def build_regen_runtime_optimisation_architecture_completion_audit(results):
    if not isinstance(results, dict):
        return _blocked_payload()

    required_boolean_inputs = {
        "phase_11d_5_runtime_completion_audit_allowed": True,
        "regen_runtime_optimisation_completion_audit_allowed": True,
        "regen_runtime_optimisation_registration_owner_ready": True,
    }

    for key, expected in required_boolean_inputs.items():
        if results.get(key) is not expected:
            return _blocked_payload()

    required_presence_inputs = (
        "regen_runtime_optimisation_registration_owner_status",
        "regen_runtime_optimisation_registry",
    )

    for key in required_presence_inputs:
        if key not in results:
            return _blocked_payload()

    if results.get("regen_runtime_optimisation_registry") is None:
        return _blocked_payload()

    return {
        "phase_11d_5_regen_runtime_optimisation_completion_audit_complete": True,
        "regen_runtime_optimisation_completion_audit_ready": True,
        "regen_runtime_optimisation_completion_audit_status": PASS_STATUS,
        "phase_11d_complete": True,
        "regen_runtime_optimisation_architecture_complete": True,
        "phase_11e_runtime_execution_architecture_allowed": True,
        "regen_runtime_execution_architecture_allowed": True,
        "regen_optimisation_runtime_execution_allowed": False,
        "regen_optimisation_generation_advance_allowed": False,
        "regen_optimisation_mutation_execution_allowed": False,
        "regen_optimisation_candidate_acceptance_allowed": False,
        "regen_optimisation_live_geometry_commit_allowed": False,
    }


def attach_regen_runtime_optimisation_architecture_completion_audit(results):
    if not isinstance(results, dict):
        results = {}

    results.update(
        build_regen_runtime_optimisation_architecture_completion_audit(
            results
        )
    )

    return results
