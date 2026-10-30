from material_source_quality_ranking_owner import (
    attach_material_source_quality_ranking_owner,
    build_material_source_quality_ranking_owner,
    rank_material_sources,
)


def test_phase_9c_ranks_strong_source_above_placeholder():
    ranked = rank_material_sources([
        {
            "source_id": "PLACEHOLDER",
            "source_type": "engineering_placeholder",
            "confidence": 0.25,
            "properties_covered": ["thermal_conductivity"],
            "is_placeholder": True,
        },
        {
            "source_id": "DATASHEET",
            "source_type": "manufacturer_datasheet",
            "confidence": 0.95,
            "properties_covered": [
                "thermal_conductivity",
                "density",
                "specific_heat",
                "max_service_temperature",
            ],
            "is_placeholder": False,
        },
    ])

    assert ranked[0]["source_id"] == "DATASHEET"
    assert ranked[0]["source_quality_rank"] == 1
    assert ranked[0]["source_rank_score"] > ranked[1]["source_rank_score"]


def test_phase_9c_default_placeholder_source_ranks_but_blocks_conservative_pass():
    owner = build_material_source_quality_ranking_owner({
        "phase_9b_material_source_provenance_owner_complete": True,
        "material_source_provenance_material": "GRCop-42",
        "material_source_provenance_sources": [
            {
                "source_id": "GRCOP42_PLACEHOLDER_001",
                "source_type": "engineering_placeholder",
                "confidence": 0.25,
                "properties_covered": [
                    "thermal_conductivity",
                    "density",
                    "specific_heat",
                    "max_service_temperature",
                ],
                "is_placeholder": True,
            }
        ],
    })

    assert owner["material_source_quality_ranking_owner_status"] == (
        "PASS_MATERIAL_SOURCE_QUALITY_RANKING_OWNER"
    )
    assert owner["phase_9c_material_source_quality_ranking_owner_complete"] is True
    assert owner["material_source_quality_ranking_placeholder_count"] == 1
    assert owner["material_source_quality_ranking_conservative_pass_allowed"] is False


def test_phase_9c_fully_sourced_high_quality_source_allows_conservative_pass():
    owner = build_material_source_quality_ranking_owner({
        "phase_9b_material_source_provenance_owner_complete": True,
        "material_source_provenance_material": "TestMaterial",
        "material_source_provenance_sources": [
            {
                "source_id": "TEST_SOURCE_001",
                "source_type": "manufacturer_datasheet",
                "confidence": 0.95,
                "properties_covered": [
                    "thermal_conductivity",
                    "density",
                    "specific_heat",
                    "max_service_temperature",
                ],
                "is_placeholder": False,
            }
        ],
    })

    assert owner["material_source_quality_ranking_owner_complete"] is True
    assert owner["material_source_quality_ranking_conservative_pass_allowed"] is True
    assert owner["material_source_quality_ranking_top_source"]["source_id"] == "TEST_SOURCE_001"


def test_phase_9c_fails_if_provenance_incomplete():
    owner = build_material_source_quality_ranking_owner({
        "phase_9b_material_source_provenance_owner_complete": False,
        "material_source_provenance_sources": [
            {
                "source_id": "TEST_SOURCE_001",
                "source_type": "manufacturer_datasheet",
                "confidence": 0.95,
                "properties_covered": ["thermal_conductivity"],
                "is_placeholder": False,
            }
        ],
    })

    assert owner["material_source_quality_ranking_owner_status"] == (
        "FAIL_MATERIAL_SOURCE_QUALITY_RANKING_OWNER"
    )
    assert owner["phase_9c_material_source_quality_ranking_owner_complete"] is False
    assert owner["material_source_quality_ranking_blockers"]


def test_phase_9c_attach_preserves_existing_results():
    results = {
        "thrust": 1000,
        "phase_9b_material_source_provenance_owner_complete": True,
        "material_source_provenance_sources": [
            {
                "source_id": "TEST_SOURCE_001",
                "source_type": "manufacturer_datasheet",
                "confidence": 0.95,
                "properties_covered": [
                    "thermal_conductivity",
                    "density",
                    "specific_heat",
                    "max_service_temperature",
                ],
                "is_placeholder": False,
            }
        ],
    }

    updated = attach_material_source_quality_ranking_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_9c_material_source_quality_ranking_owner_complete"] is True
    assert "material_source_quality_ranking_text" in updated