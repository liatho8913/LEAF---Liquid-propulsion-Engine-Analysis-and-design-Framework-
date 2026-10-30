from regen_source_validation_gate import attach_regen_source_validation_gate
from regen_provenance_report_owner import attach_regen_provenance_report
from regen_property_table_owner import attach_regen_property_table_owner
from regen_validation_master_gate import attach_regen_validation_master_gate
from regen_completion_audit import attach_regen_completion_audit


def run_stage_u_pipeline(results):
    results = dict(results)
    results = attach_regen_source_validation_gate(results)
    results = attach_regen_provenance_report(results)
    results = attach_regen_property_table_owner(results)
    results = attach_regen_validation_master_gate(results)
    results = attach_regen_completion_audit(results)
    return results


def base_valid_case():
    return {
        "material_name": "GRCop-42",
        "coating_name": "NONE",

        "material_source_validation_mode": "SOURCED_VALIDATION_MODE",
        "material_source_validation_score": 95,
        "material_source_is_placeholder": False,

        "material_temperature_table_status": "VALID",
        "material_property_interpolation_status": "VALID",
        "material_table_min_temperature": 300,
        "material_table_max_temperature": 1200,

        "hot_gas_side_wall_temperature": 850,
        "material_max_wall_temperature": 900,

        "full_engine_regen_geometry_status": "PASS_FULL_ENGINE_REGEN_GEOMETRY",
        "regen_validation_status": "PASS_REGEN_VALIDATION",
    }


def assert_case(name, results, expected_complete):
    actual = bool(results.get("stage_u_regen_validation_complete"))

    if actual != expected_complete:
        raise AssertionError(
            f"{name} failed: expected stage_u_regen_validation_complete="
            f"{expected_complete}, got {actual}\n\n"
            f"Completion audit:\n{results.get('regen_completion_audit_text')}\n\n"
            f"Master gate:\n{results.get('regen_validation_master_gate_text')}\n\n"
            f"Property table report:\n{results.get('regen_property_table_owner_text')}\n\n"
            f"Source validation report:\n{results.get('regen_source_validation_text')}"
        )

    print(f"PASS: {name}")


def main():
    valid = run_stage_u_pipeline(base_valid_case())
    assert_case("Sourced valid no-coating case may complete Stage U", valid, True)

    placeholder = base_valid_case()
    placeholder["material_source_validation_mode"] = "PLACEHOLDER_MODE"
    placeholder["material_source_is_placeholder"] = True
    placeholder = run_stage_u_pipeline(placeholder)
    assert_case("Placeholder mode must not complete Stage U", placeholder, False)

    partial = base_valid_case()
    partial["material_source_validation_mode"] = "PARTIAL_SOURCE_MODE"
    partial = run_stage_u_pipeline(partial)
    assert_case("Partial source mode must not complete Stage U", partial, False)

    missing_table = base_valid_case()
    missing_table["material_temperature_table_status"] = "MISSING"
    missing_table = run_stage_u_pipeline(missing_table)
    assert_case("Missing material table must not complete Stage U", missing_table, False)

    overheated = base_valid_case()
    overheated["hot_gas_side_wall_temperature"] = 1000
    overheated = run_stage_u_pipeline(overheated)
    assert_case("Wall temperature above material limit must not complete Stage U", overheated, False)

    coating_missing = base_valid_case()
    coating_missing["coating_name"] = "TBC"
    coating_missing["coating_source_validation_mode"] = "SOURCED_VALIDATION_MODE"
    coating_missing["coating_source_validation_score"] = 95
    coating_missing["coating_temperature_table_status"] = "MISSING"
    coating_missing["coating_property_interpolation_status"] = "UNKNOWN"
    coating_missing = run_stage_u_pipeline(coating_missing)
    assert_case("Selected coating with missing table must not complete Stage U", coating_missing, False)

    print("")
    print("STAGE U SELF-TEST COMPLETE")


if __name__ == "__main__":
    main()