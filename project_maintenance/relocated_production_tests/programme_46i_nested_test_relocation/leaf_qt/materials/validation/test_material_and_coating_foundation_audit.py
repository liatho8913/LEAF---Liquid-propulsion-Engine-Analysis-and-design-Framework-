from material_and_coating_foundation_audit import (
    attach_material_and_coating_foundation_audit,
    build_material_and_coating_foundation_audit,
)


def _complete_results():
    return {
        "phase_9a_material_property_interpolation_owner_complete": True,
        "phase_9b_material_source_provenance_owner_complete": True,
        "phase_9c_material_source_quality_ranking_owner_complete": True,
        "phase_9d_material_validation_owner_complete": True,
        "phase_9e_material_completion_audit_complete": True,
        "phase_9f_coating_source_provenance_owner_complete": True,
        "phase_9g_coating_validation_owner_complete": True,
        "material_completion_audit_status": "PASS_MATERIAL_COMPLETION_AUDIT",
        "material_validation_owner_status": "PASS_MATERIAL_VALIDATION_OWNER",
        "coating_source_provenance_owner_status": "PASS_COATING_SOURCE_PROVENANCE_OWNER",
        "coating_validation_owner_status": "PASS_COATING_VALIDATION_OWNER",
        "material_validation_pass": True,
        "coating_validation_pass": True,
        "stage_9_material_foundation_complete": True,
    }


def test_phase_9h_passes_when_material_and_coating_foundations_are_complete():
    audit = build_material_and_coating_foundation_audit(_complete_results())

    assert audit["material_and_coating_foundation_audit_status"] == (
        "PASS_MATERIAL_AND_COATING_FOUNDATION_AUDIT"
    )
    assert audit["material_and_coating_foundation_audit_complete"] is True
    assert audit["phase_9h_material_and_coating_foundation_audit_complete"] is True
    assert audit["stage_9_material_and_coating_foundation_complete"] is True


def test_phase_9h_fails_when_material_phase_missing():
    results = _complete_results()
    results["phase_9c_material_source_quality_ranking_owner_complete"] = False

    audit = build_material_and_coating_foundation_audit(results)

    assert audit["material_and_coating_foundation_audit_status"] == (
        "FAIL_MATERIAL_AND_COATING_FOUNDATION_AUDIT"
    )
    assert audit["material_and_coating_foundation_audit_complete"] is False
    assert any(
        "9C Material Source Quality Ranking Owner" in phase
        for phase in audit["material_and_coating_foundation_audit_missing_phases"]
    )


def test_phase_9h_fails_when_coating_validation_not_passing():
    results = _complete_results()
    results["coating_validation_pass"] = False

    audit = build_material_and_coating_foundation_audit(results)

    assert audit["material_and_coating_foundation_audit_complete"] is False
    assert any(
        "Coating validation is not passing" in blocker
        for blocker in audit["material_and_coating_foundation_audit_blockers"]
    )


def test_phase_9h_fails_when_material_foundation_not_complete():
    results = _complete_results()
    results["stage_9_material_foundation_complete"] = False

    audit = build_material_and_coating_foundation_audit(results)

    assert audit["material_and_coating_foundation_audit_complete"] is False
    assert any(
        "Material foundation completion audit is not passing" in blocker
        for blocker in audit["material_and_coating_foundation_audit_blockers"]
    )


def test_phase_9h_fails_when_status_unknown():
    results = _complete_results()
    results["coating_validation_owner_status"] = "UNKNOWN"

    audit = build_material_and_coating_foundation_audit(results)

    assert audit["material_and_coating_foundation_audit_complete"] is False
    assert any(
        "coating validation status" in blocker.lower()
        for blocker in audit["material_and_coating_foundation_audit_blockers"]
    )


def test_phase_9h_attach_preserves_existing_results():
    results = _complete_results()
    results["thrust"] = 1000

    updated = attach_material_and_coating_foundation_audit(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_9h_material_and_coating_foundation_audit_complete"] is True
    assert "material_and_coating_foundation_audit_text" in updated