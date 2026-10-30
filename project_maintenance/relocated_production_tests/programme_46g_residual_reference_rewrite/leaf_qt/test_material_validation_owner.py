from material_validation_owner import (
    attach_material_validation_owner,
    build_material_validation_owner,
)


def _fully_sourced_valid_results():
    return {
        "phase_9a_material_property_interpolation_owner_complete": True,
        "phase_9b_material_source_provenance_owner_complete": True,
        "phase_9c_material_source_quality_ranking_owner_complete": True,
        "material_property_interpolation_material": "TestMaterial",
        "material_property_interpolation_mode": "SOURCED_VALIDATION_MODE",
        "material_property_interpolation_query_temperature": 700.0,
        "material_property_interpolation_results": {
            "max_service_temperature": {
                "value": 1000.0,
            }
        },
        "material_source_provenance_placeholder_count": 0,
        "material_source_quality_ranking_placeholder_count": 0,
        "material_source_provenance_average_confidence": 0.95,
        "material_source_quality_ranking_average_score": 0.90,
        "material_source_quality_ranking_top_source": {
            "source_rank_score": 0.95,
        },
    }


def test_phase_9d_passes_fully_sourced_valid_material():
    validation = build_material_validation_owner(_fully_sourced_valid_results())

    assert validation["material_validation_owner_status"] == "PASS_MATERIAL_VALIDATION_OWNER"
    assert validation["material_validation_pass"] is True
    assert validation["phase_9d_material_validation_owner_complete"] is True
    assert validation["material_validation_blocking_rule_count"] == 0


def test_phase_9d_blocks_placeholder_or_partial_mode():
    results = _fully_sourced_valid_results()
    results["material_property_interpolation_mode"] = "PARTIAL_SOURCE_MODE"

    validation = build_material_validation_owner(results)

    assert validation["material_validation_owner_status"] == "FAIL_MATERIAL_VALIDATION_OWNER"
    assert validation["material_validation_pass"] is False
    assert validation["material_validation_blocking_rule_count"] > 0


def test_phase_9d_blocks_placeholder_sources():
    results = _fully_sourced_valid_results()
    results["material_source_provenance_placeholder_count"] = 1

    validation = build_material_validation_owner(results)

    assert validation["material_validation_pass"] is False
    assert any(
        rule["rule_id"] == "MAT-VAL-NO-PLACEHOLDER-SOURCES"
        for rule in validation["material_validation_blocking_rules"]
    )


def test_phase_9d_blocks_low_confidence_sources():
    results = _fully_sourced_valid_results()
    results["material_source_provenance_average_confidence"] = 0.4

    validation = build_material_validation_owner(results)

    assert validation["material_validation_pass"] is False
    assert any(
        rule["rule_id"] == "MAT-VAL-SOURCE-CONFIDENCE"
        for rule in validation["material_validation_blocking_rules"]
    )


def test_phase_9d_blocks_overheated_material():
    results = _fully_sourced_valid_results()
    results["material_property_interpolation_query_temperature"] = 1200.0

    validation = build_material_validation_owner(results)

    assert validation["material_validation_pass"] is False
    assert validation["material_validation_temperature_margin"] == -200.0
    assert any(
        rule["rule_id"] == "MAT-VAL-TEMPERATURE-MARGIN"
        for rule in validation["material_validation_blocking_rules"]
    )


def test_phase_9d_warns_on_low_positive_temperature_margin():
    results = _fully_sourced_valid_results()
    results["material_property_interpolation_query_temperature"] = 930.0

    validation = build_material_validation_owner(results)

    assert validation["material_validation_pass"] is True
    assert validation["material_validation_warning_rule_count"] == 1
    assert any(
        rule["rule_id"] == "MAT-VAL-TEMPERATURE-MARGIN-WARNING"
        for rule in validation["material_validation_warning_rules"]
    )


def test_phase_9d_attach_preserves_existing_results():
    results = _fully_sourced_valid_results()
    results["thrust"] = 1000

    updated = attach_material_validation_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_9d_material_validation_owner_complete"] is True
    assert "material_validation_text" in updated