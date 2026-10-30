from __future__ import annotations

from leaf_qt.coating_validation_owner import (
    attach_coating_validation_owner,
    build_coating_validation_owner,
)


VALID_RESULTS = {
    "phase_9f_coating_source_provenance_owner_complete": True,
    "coating_source_provenance_no_coating_selected": False,
    "coating_source_provenance_mode": "SOURCED_VALIDATION_MODE",
    "coating_source_provenance_placeholder_count": 0,
    "coating_source_provenance_average_confidence": 0.92,
    "coating_source_provenance_conservative_pass_allowed": True,
    "coating_source_provenance_coating": "Sourced ceramic coating",
    "coating_query_temperature": 1100.0,
    "coating_max_service_temperature": 1500.0,
}


def test_phase_16t3k8_preserves_legacy_pass_contract() -> None:
    payload = build_coating_validation_owner(dict(VALID_RESULTS))

    assert payload["coating_validation_owner_status"] == "PASS_COATING_VALIDATION_OWNER"
    assert payload["coating_validation_owner_complete"] is True
    assert payload["coating_validation_pass"] is True
    assert payload["phase_9g_coating_validation_owner_complete"] is True


def test_phase_16t3k8_adds_structured_findings_and_global_pass() -> None:
    payload = build_coating_validation_owner(dict(VALID_RESULTS))

    assert payload["coating_validation_structured_findings"]
    assert payload["coating_validation_global_status"] == "PASS"
    assert payload["coating_validation_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["coating_validation_text"]


def test_phase_16t3k8_placeholder_sources_block_global_status() -> None:
    data = dict(VALID_RESULTS)
    data["coating_source_provenance_placeholder_count"] = 2

    payload = build_coating_validation_owner(data)

    assert payload["coating_validation_owner_status"] == "FAIL_COATING_VALIDATION_OWNER"
    assert payload["coating_validation_pass"] is False
    assert payload["coating_validation_global_status"] == "BLOCKED"


def test_phase_16t3k8_missing_provenance_blocks_global_status() -> None:
    data = dict(VALID_RESULTS)
    data["phase_9f_coating_source_provenance_owner_complete"] = False

    payload = build_coating_validation_owner(data)

    assert payload["coating_validation_owner_status"] == "FAIL_COATING_VALIDATION_OWNER"
    assert payload["coating_validation_pass"] is False
    assert payload["coating_validation_global_status"] == "BLOCKED"


def test_phase_16t3k8_invalid_temperature_margin_fails_global_status() -> None:
    data = dict(VALID_RESULTS)
    data["coating_query_temperature"] = 1600.0
    data["coating_max_service_temperature"] = 1500.0

    payload = build_coating_validation_owner(data)

    assert payload["coating_validation_owner_status"] == "FAIL_COATING_VALIDATION_OWNER"
    assert payload["coating_validation_pass"] is False
    assert payload["coating_validation_global_status"] == "FAIL"


def test_phase_16t3k8_warning_only_margin_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["coating_query_temperature"] = 1410.0
    data["coating_max_service_temperature"] = 1500.0

    payload = build_coating_validation_owner(data)

    assert payload["coating_validation_owner_status"] == "PASS_COATING_VALIDATION_OWNER"
    assert payload["coating_validation_pass"] is True
    assert payload["coating_validation_warning_rule_count"] == 1
    assert payload["coating_validation_global_status"] == "BLOCKED"


def test_phase_16t3k8_no_coating_selected_remains_valid_when_provenance_complete() -> None:
    data = dict(VALID_RESULTS)
    data["coating_source_provenance_no_coating_selected"] = True
    data["selected_coating"] = "None"

    payload = build_coating_validation_owner(data)

    assert payload["coating_validation_owner_status"] == "PASS_COATING_VALIDATION_OWNER"
    assert payload["coating_validation_pass"] is True
    assert payload["coating_validation_global_status"] == "PASS"


def test_phase_16t3k8_attach_preserves_mutating_contract() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_coating_validation_owner(data)

    assert returned is data
    assert data["coating_validation_owner_status"] == "PASS_COATING_VALIDATION_OWNER"
    assert data["coating_validation_global_status"] == "PASS"
    assert data["phase_16t3k8_status_adapter_complete"] is True
