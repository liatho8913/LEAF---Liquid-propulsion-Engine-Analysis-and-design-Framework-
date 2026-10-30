from material_source_provenance_owner import (
    attach_material_source_provenance_owner,
    build_material_source_provenance_owner,
)


def test_phase_9b_default_placeholder_source_passes_but_blocks_conservative_validation():
    owner = build_material_source_provenance_owner({
        "selected_material": "GRCop-42",
    })

    assert owner["material_source_provenance_owner_status"] == (
        "PASS_MATERIAL_SOURCE_PROVENANCE_OWNER"
    )
    assert owner["phase_9b_material_source_provenance_owner_complete"] is True
    assert owner["material_source_provenance_source_count"] == 1
    assert owner["material_source_provenance_placeholder_count"] == 1
    assert owner["material_source_provenance_conservative_pass_allowed"] is False


def test_phase_9b_missing_source_record_fails_cleanly():
    owner = build_material_source_provenance_owner({
        "selected_material": "Unobtainium",
    })

    assert owner["material_source_provenance_owner_status"] == (
        "FAIL_MATERIAL_SOURCE_PROVENANCE_OWNER"
    )
    assert owner["phase_9b_material_source_provenance_owner_complete"] is False
    assert owner["material_source_provenance_blockers"]


def test_phase_9b_fully_sourced_record_allows_conservative_pass():
    owner = build_material_source_provenance_owner({
        "selected_material": "TestMaterial",
        "material_source_records": {
            "TestMaterial": {
                "material": "TestMaterial",
                "mode": "SOURCED_VALIDATION_MODE",
                "source_quality": "FULLY_SOURCED",
                "sources": [
                    {
                        "source_id": "TEST_SOURCE_001",
                        "source_type": "manufacturer_datasheet",
                        "title": "Test Material Datasheet",
                        "citation": "Test Citation",
                        "confidence": 0.95,
                        "properties_covered": [
                            "thermal_conductivity",
                            "density",
                        ],
                        "is_placeholder": False,
                    }
                ],
            }
        },
    })

    assert owner["material_source_provenance_owner_complete"] is True
    assert owner["material_source_provenance_conservative_pass_allowed"] is True
    assert owner["material_source_provenance_placeholder_count"] == 0
    assert owner["material_source_provenance_average_confidence"] == 0.95


def test_phase_9b_low_confidence_sourced_record_blocks_conservative_pass():
    owner = build_material_source_provenance_owner({
        "selected_material": "TestMaterial",
        "material_source_records": {
            "TestMaterial": {
                "material": "TestMaterial",
                "mode": "SOURCED_VALIDATION_MODE",
                "source_quality": "FULLY_SOURCED",
                "sources": [
                    {
                        "source_id": "TEST_SOURCE_LOW",
                        "source_type": "unknown",
                        "title": "Weak Source",
                        "citation": "Weak Citation",
                        "confidence": 0.4,
                        "properties_covered": ["thermal_conductivity"],
                        "is_placeholder": False,
                    }
                ],
            }
        },
    })

    assert owner["material_source_provenance_owner_complete"] is True
    assert owner["material_source_provenance_conservative_pass_allowed"] is False


def test_phase_9b_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
        "selected_material": "GRCop-42",
    }

    updated = attach_material_source_provenance_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_9b_material_source_provenance_owner_complete"] is True
    assert "material_source_provenance_text" in updated