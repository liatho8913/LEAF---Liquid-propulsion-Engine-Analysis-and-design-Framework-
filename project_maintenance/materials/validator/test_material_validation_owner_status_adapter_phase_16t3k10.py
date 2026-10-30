from __future__ import annotations

from leaf_qt.material_validation_owner import (
    attach_material_validation_owner,
    build_material_validation_owner,
)


VALID_RESULTS = {
    "material_source_provenance_owner_complete": True,
    "material_source_provenance_mode": "SOURCED_VALIDATION_MODE",
    "material_source_provenance_placeholder_count": 0,
    "material_source_provenance_average_confidence": 0.92,
    "material_source_provenance_conservative_pass_allowed": True,
    "material_source_provenance_material": "Sourced copper alloy",
    "material_query_temperature": 900.0,
    "material_max_service_temperature": 1200.0,
}


def test_phase_16t3k10_preserves_legacy_pass_contract() -> None:
    payload = build_material_validation_owner(dict(VALID_RESULTS))

    assert payload["material_validation_owner_status"] == "PASS_MATERIAL_VALIDATION_OWNER"
    assert payload["material_validation_owner_complete"] is True
    assert payload["material_validation_pass"] is True
    assert payload["phase_16t3k10_status_adapter_complete"] is True


def test_phase_16t3k10_adds_structured_findings_and_global_pass() -> None:
    payload = build_material_validation_owner(dict(VALID_RESULTS))

    assert payload["material_validation_structured_findings"]
    assert payload["material_validation_global_status"] == "PASS"
    assert payload["material_validation_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["material_validation_text"]


def test_phase_16t3k10_placeholder_sources_block_global_status() -> None:
    data = dict(VALID_RESULTS)
    data["material_source_provenance_placeholder_count"] = 2

    payload = build_material_validation_owner(data)

    assert payload["material_validation_owner_status"] == "FAIL_MATERIAL_VALIDATION_OWNER"
    assert payload["material_validation_pass"] is False
    assert payload["material_validation_global_status"] == "BLOCKED"


def test_phase_16t3k10_missing_provenance_blocks_global_status() -> None:
    data = dict(VALID_RESULTS)
    data["material_source_provenance_owner_complete"] = False

    payload = build_material_validation_owner(data)

    assert payload["material_validation_owner_status"] == "FAIL_MATERIAL_VALIDATION_OWNER"
    assert payload["material_validation_pass"] is False
    assert payload["material_validation_global_status"] == "BLOCKED"


def test_phase_16t3k10_invalid_temperature_margin_fails_global_status() -> None:
    data = dict(VALID_RESULTS)
    data["material_query_temperature"] = 1300.0
    data["material_max_service_temperature"] = 1200.0

    payload = build_material_validation_owner(data)

    assert payload["material_validation_owner_status"] == "FAIL_MATERIAL_VALIDATION_OWNER"
    assert payload["material_validation_pass"] is False
    assert payload["material_validation_global_status"] == "FAIL"


def test_phase_16t3k10_warning_only_margin_blocks_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["material_query_temperature"] = 1110.0
    data["material_max_service_temperature"] = 1200.0

    payload = build_material_validation_owner(data)

    assert payload["material_validation_owner_status"] == "PASS_MATERIAL_VALIDATION_OWNER"
    assert payload["material_validation_pass"] is True
    assert payload["material_validation_warning_rule_count"] == 1
    assert payload["material_validation_global_status"] == "BLOCKED"


def test_phase_16t3k10_attach_preserves_mutating_contract() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_material_validation_owner(data)

    assert returned is data
    assert data["material_validation_owner_status"] == "PASS_MATERIAL_VALIDATION_OWNER"
    assert data["material_validation_global_status"] == "PASS"
    assert data["phase_16t3k10_status_adapter_complete"] is True


def test_phase_16t3k10_non_dict_attach_preserves_input() -> None:
    assert attach_material_validation_owner(None) is None
