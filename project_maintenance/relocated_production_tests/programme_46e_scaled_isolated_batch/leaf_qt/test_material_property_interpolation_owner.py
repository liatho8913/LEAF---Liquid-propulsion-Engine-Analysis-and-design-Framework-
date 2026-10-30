from material_property_interpolation_owner import (
    attach_material_property_interpolation_owner,
    build_material_property_interpolation_owner,
    interpolate_property_table,
)


def test_phase_9a_interpolates_between_two_points():
    result = interpolate_property_table(
        points=[
            {"T": 300.0, "value": 100.0},
            {"T": 500.0, "value": 200.0},
        ],
        temperature=400.0,
    )

    assert result["status"] == "PASS_INTERPOLATION"
    assert result["value"] == 150.0
    assert result["within_table_range"] is True


def test_phase_9a_interpolates_material_table():
    results = {
        "selected_material": "GRCop-42",
        "material_property_query_temperature": 600.0,
    }

    owner = build_material_property_interpolation_owner(results)

    assert owner["material_property_interpolation_owner_status"] == (
        "PASS_MATERIAL_PROPERTY_INTERPOLATION_OWNER"
    )
    assert owner["phase_9a_material_property_interpolation_owner_complete"] is True
    assert "thermal_conductivity" in owner["material_property_interpolation_results"]
    assert owner["material_property_interpolation_results"]["thermal_conductivity"]["value"] == 285.0


def test_phase_9a_missing_material_table_fails_cleanly():
    results = {
        "selected_material": "Unobtainium",
        "material_property_query_temperature": 600.0,
    }

    owner = build_material_property_interpolation_owner(results)

    assert owner["material_property_interpolation_owner_status"] == (
        "FAIL_MATERIAL_PROPERTY_INTERPOLATION_OWNER"
    )
    assert owner["phase_9a_material_property_interpolation_owner_complete"] is False
    assert owner["material_property_interpolation_blockers"]


def test_phase_9a_placeholder_data_never_allows_conservative_pass():
    owner = build_material_property_interpolation_owner({
        "selected_material": "GRCop-42",
        "material_property_query_temperature": 600.0,
    })

    assert owner["material_property_interpolation_owner_complete"] is True
    assert owner["material_property_interpolation_conservative_pass_allowed"] is False
    assert owner["material_property_interpolation_mode"] == "PARTIAL_SOURCE_MODE"


def test_phase_9a_sourced_table_allows_conservative_pass():
    owner = build_material_property_interpolation_owner({
        "selected_material": "TestMaterial",
        "material_property_query_temperature": 400.0,
        "material_property_tables": {
            "TestMaterial": {
                "mode": "SOURCED_VALIDATION_MODE",
                "source_quality": "FULLY_SOURCED",
                "temperature_unit": "K",
                "properties": {
                    "thermal_conductivity": [
                        {"T": 300.0, "value": 100.0},
                        {"T": 500.0, "value": 200.0},
                    ],
                },
            }
        },
    })

    assert owner["material_property_interpolation_owner_complete"] is True
    assert owner["material_property_interpolation_conservative_pass_allowed"] is True


def test_phase_9a_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
        "selected_material": "GRCop-42",
        "material_property_query_temperature": 600.0,
    }

    updated = attach_material_property_interpolation_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_9a_material_property_interpolation_owner_complete"] is True
    assert "material_property_interpolation_text" in updated