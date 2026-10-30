from coating_validation_owner import (
    attach_coating_validation_owner,
    build_coating_validation_owner,
)


def _valid_sourced_coating_results():
    return {
        "phase_9f_coating_source_provenance_owner_complete": True,
        "coating_source_provenance_coating": "TestCoating",
        "coating_source_provenance_no_coating_selected": False,
        "coating_source_provenance_mode": "SOURCED_VALIDATION_MODE",
        "coating_source_provenance_placeholder_count": 0,
        "coating_source_provenance_average_confidence": 0.95,
        "coating_source_provenance_conservative_pass_allowed": True,
        "coating_query_temperature": 1200.0,
        "coating_service_temperature": 1600.0,
    }


def test_phase_9g_no_coating_selected_passes_structurally():
    validation = build_coating_validation_owner({
        "phase_9f_coating_source_provenance_owner_complete": True,
        "coating_source_provenance_coating": "None",
        "coating_source_provenance_no_coating_selected": True,
        "coating_source_provenance_mode": "NO_COATING_MODE",
    })

    assert validation["coating_validation_owner_status"] == "PASS_COATING_VALIDATION_OWNER"
    assert validation["coating_validation_pass"] is True
    assert validation["phase_9g_coating_validation_owner_complete"] is True
    assert validation["coating_validation_no_coating_selected"] is True


def test_phase_9g_valid_sourced_coating_passes():
    validation = build_coating_validation_owner(_valid_sourced_coating_results())

    assert validation["coating_validation_owner_status"] == "PASS_COATING_VALIDATION_OWNER"
    assert validation["coating_validation_pass"] is True
    assert validation["coating_validation_blocking_rule_count"] == 0


def test_phase_9g_blocks_placeholder_coating_mode():
    results = _valid_sourced_coating_results()
    results["coating_source_provenance_mode"] = "PLACEHOLDER_MODE"

    validation = build_coating_validation_owner(results)

    assert validation["coating_validation_pass"] is False
    assert any(
        rule["rule_id"] == "COAT-VAL-SOURCED-MODE"
        for rule in validation["coating_validation_blocking_rules"]
    )


def test_phase_9g_blocks_placeholder_sources():
    results = _valid_sourced_coating_results()
    results["coating_source_provenance_placeholder_count"] = 1

    validation = build_coating_validation_owner(results)

    assert validation["coating_validation_pass"] is False
    assert any(
        rule["rule_id"] == "COAT-VAL-NO-PLACEHOLDER-SOURCES"
        for rule in validation["coating_validation_blocking_rules"]
    )


def test_phase_9g_blocks_low_confidence_source():
    results = _valid_sourced_coating_results()
    results["coating_source_provenance_average_confidence"] = 0.4

    validation = build_coating_validation_owner(results)

    assert validation["coating_validation_pass"] is False
    assert any(
        rule["rule_id"] == "COAT-VAL-SOURCE-CONFIDENCE"
        for rule in validation["coating_validation_blocking_rules"]
    )


def test_phase_9g_blocks_overheated_coating():
    results = _valid_sourced_coating_results()
    results["coating_query_temperature"] = 1800.0

    validation = build_coating_validation_owner(results)

    assert validation["coating_validation_pass"] is False
    assert validation["coating_validation_temperature_margin"] == -200.0
    assert any(
        rule["rule_id"] == "COAT-VAL-TEMPERATURE-MARGIN"
        for rule in validation["coating_validation_blocking_rules"]
    )


def test_phase_9g_warns_on_low_positive_temperature_margin():
    results = _valid_sourced_coating_results()
    results["coating_query_temperature"] = 1500.0

    validation = build_coating_validation_owner(results)

    assert validation["coating_validation_pass"] is True
    assert validation["coating_validation_warning_rule_count"] == 1
    assert any(
        rule["rule_id"] == "COAT-VAL-TEMPERATURE-MARGIN-WARNING"
        for rule in validation["coating_validation_warning_rules"]
    )


def test_phase_9g_attach_preserves_existing_results():
    results = _valid_sourced_coating_results()
    results["thrust"] = 1000

    updated = attach_coating_validation_owner(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_9g_coating_validation_owner_complete"] is True
    assert "coating_validation_text" in updated