try:
    from project_maintenance.production_historical_artifacts.leaf_qt.regen_thermal_geometry_coupling_master_gate import (
        run_regen_thermal_geometry_coupling_master_gate,
        flatten_regen_thermal_geometry_coupling_master_gate_result,
    )
except Exception:
    from project_maintenance.production_historical_artifacts.leaf_qt.regen_thermal_geometry_coupling_master_gate import (
        run_regen_thermal_geometry_coupling_master_gate,
        flatten_regen_thermal_geometry_coupling_master_gate_result,
    )


PASS_STATUS = (
    "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_COMPLETION_AUDIT"
)

FAIL_STATUS = (
    "FAIL_REGEN_THERMAL_GEOMETRY_COUPLING_COMPLETION_AUDIT"
)


def run_regen_thermal_geometry_coupling_completion_audit():
    errors = []
    warnings = []

    gate_result = (
        run_regen_thermal_geometry_coupling_master_gate()
    )

    flat = (
        flatten_regen_thermal_geometry_coupling_master_gate_result(
            gate_result
        )
    )

    required_keys = [
        "recommended_regen_thermal_geometry_coupling_master_gate_status",
        "recommended_regen_thermal_geometry_coupling_master_gate_pass",
        "recommended_regen_thermal_geometry_coupling_phase_5_trusted",
        "recommended_regen_thermal_geometry_coupling_completion_audit_allowed",
    ]

    for key in required_keys:
        if key not in flat:
            errors.append(
                f"Missing flattened output key: {key}"
            )

    if not gate_result.get(
        "regen_thermal_geometry_coupling_master_gate_pass",
        False,
    ):
        errors.append(
            "Thermal geometry coupling master gate failed."
        )

    completion_pass = len(errors) == 0

    return {
        "regen_thermal_geometry_coupling_completion_audit_status": (
            PASS_STATUS
            if completion_pass
            else FAIL_STATUS
        ),
        "regen_thermal_geometry_coupling_completion_audit_pass": (
            completion_pass
        ),
        "phase_5_thermal_geometry_coupling_complete": (
            completion_pass
        ),
        "phase_5_ready_for_scalability_testing": (
            completion_pass
        ),
        "phase_5_ready_for_real_engine_validation": (
            completion_pass
        ),
        "errors": errors,
        "warnings": warnings,
        "gate_result": gate_result,
        "audit_statement": (
            "THERMAL GEOMETRY COUPLING ARCHITECTURE COMPLETE"
            if completion_pass
            else
            "THERMAL GEOMETRY COUPLING ARCHITECTURE INCOMPLETE"
        ),
    }


def flatten_regen_thermal_geometry_coupling_completion_audit_result(
    result,
    prefix="recommended",
):
    return {
        f"{prefix}_regen_thermal_geometry_coupling_completion_audit_status":
            result.get(
                "regen_thermal_geometry_coupling_completion_audit_status"
            ),

        f"{prefix}_regen_thermal_geometry_coupling_completion_audit_pass":
            (
                1.0
                if result.get(
                    "regen_thermal_geometry_coupling_completion_audit_pass"
                )
                else 0.0
            ),

        f"{prefix}_phase_5_thermal_geometry_coupling_complete":
            (
                1.0
                if result.get(
                    "phase_5_thermal_geometry_coupling_complete"
                )
                else 0.0
            ),

        f"{prefix}_phase_5_ready_for_scalability_testing":
            (
                1.0
                if result.get(
                    "phase_5_ready_for_scalability_testing"
                )
                else 0.0
            ),

        f"{prefix}_phase_5_ready_for_real_engine_validation":
            (
                1.0
                if result.get(
                    "phase_5_ready_for_real_engine_validation"
                )
                else 0.0
            ),
    }