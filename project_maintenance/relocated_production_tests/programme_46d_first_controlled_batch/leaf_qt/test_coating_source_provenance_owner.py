from coating_source_provenance_owner import (
    attach_coating_source_provenance_owner,
    build_coating_source_provenance_owner,
)


def test_phase_9f_no_coating_is_structurally_complete():
    owner = build_coating_source_provenance_owner({
        "selected_coating": "None",
    })

    assert owner["coating_source_provenance_owner_status"] == (
        "PASS_COATING_SOURCE_PROVENANCE_OWNER"
    )
    assert owner["phase_9f_coating_source_provenance_owner_complete"] is True
    assert owner["coating_source_provenance_no_coating_selected"] is True
    assert owner["coating_source_provenance_conservative_pass_allowed"] is True


def test_phase_9f_default_placeholder_coating_passes_but_blocks_conservative_validation():
    owner = build_coating_source_provenance_owner({
        "selected_coating": "Generic TBC",
    })

    assert owner["coating_source_provenance_owner_status"] == (
        "PASS_COATING_SOURCE_PROVENANCE_OWNER"
    )
    assert owner["phase_9f_coating_source_provenance_owner_complete"] is True
    assert owner["coating_source_provenance_source_count"] == 1
    assert owner["coating_source_provenance_placeholder_count"] == 1
    assert owner["coating_source_provenance_conservative_pass_allowed"] is False


def test_phase_9f_missing_coating_source_record_fails_cleanly():
    owner = build_coating_source_provenance_owner({
        "selected_coating": "Unknown Coating",
    })

    assert owner["coating_source_provenance_owner_status"] == (
        "FAIL_COATING_SOURCE_PROVENANCE_OWNER"
    )
    assert owner["phase_9f_coating_source_provenance_owner_complete"] is False
    assert owner["coating_source_provenance_blockers"]


def test_phase_9f_fully_sourced_coating_allows_conservative_pass():
    owner = build_coating_source_provenance_owner({
        "selected_coating": "TestCoating",
        "coating_source_records": {
            "TestCoating": {
                "coating": "TestCoating",
                "mode": "SOURCED_VALIDATION_MODE",
                "source_quality": "FULLY_SOURCED",
                "sources": [
                    {
                        "source_id": "TEST_COATING_SOURCE_001",
                        "source_type": "manufacturer_datasheet",
                        "title": "Test Coating Datasheet",
                        "citation": "Test Coating Citation",
                        "confidence": 0.95,
                        "properties_covered": [
                            "thermal_conductivity",
                            "max_service_temperature",
                            "bond_compatibility",
                            "thickness_range",
                        ],
                        "is_placeholder": False,
                    }
                ],
            }
        },
    })

    assert owner["coating_source_provenance_owner_complete"] is True
    assert owner["coating_source_provenance_conservative_pass_allowed"] is True
    assert owner["coating_source_provenance_placeholder_count"] == 0


def test_phase_9f_low_confidence_source_blocks_conservative_pass():
    owner = build_coating_source_provenance_owner({
        "selected_coating": "TestCoating",
        "coating_source_records": {
            "TestCoating": {
                "coating": "TestCoating",
                "mode": "SOURCED_VALIDATION_MODE",
                "source_quality": "FULLY_SOURCED",
                "sources": [
                    {
                        "source_id": "TEST_COATING_SOURCE_LOW",
                        "source_type": "unknown",
                        "title": "Weak Coating Source",
                        "citation": "Weak Citation",
                        "confidence": 0.4,
                        "properties_covered": ["thermal_conductivity"],
                        "is_placeholder": False,
                    }
                ],
            }
        },
    })

    assert owner["coating_source_provenance_owner_complete"] is True
    assert owner["coating_source_provenance_conservative_pass_allowed"] is False


def test_phase_9f_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
        "selected_coating": "None",
    }

    updated = attach_coating_source_provenance_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_9f_coating_source_provenance_owner_complete"] is True
    assert "coating_source_provenance_text" in updated