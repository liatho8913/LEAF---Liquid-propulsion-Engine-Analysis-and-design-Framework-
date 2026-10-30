from material_completion_audit import (
    attach_material_completion_audit,
    build_material_completion_audit,
)


def _complete_material_results():
    return {
        "phase_9a_material_property_interpolation_owner_complete": True,
        "phase_9b_material_source_provenance_owner_complete": True,
        "phase_9c_material_source_quality_ranking_owner_complete": True,
        "phase_9d_material_validation_owner_complete": True,
        "material_property_interpolation_owner_status": "PASS_MATERIAL_PROPERTY_INTERPOLATION_OWNER",
        "material_source_provenance_owner_status": "PASS_MATERIAL_SOURCE_PROVENANCE_OWNER",
        "material_source_quality_ranking_owner_status": "PASS_MATERIAL_SOURCE_QUALITY_RANKING_OWNER",
        "material_validation_owner_status": "PASS_MATERIAL_VALIDATION_OWNER",
        "material_validation_pass": True,
    }


def test_phase_9e_completion_audit_passes_when_material_stack_complete():
    audit = build_material_completion_audit(_complete_material_results())

    assert audit["material_completion_audit_status"] == "PASS_MATERIAL_COMPLETION_AUDIT"
    assert audit["material_completion_audit_complete"] is True
    assert audit["phase_9e_material_completion_audit_complete"] is True
    assert audit["stage_9_material_foundation_complete"] is True


def test_phase_9e_completion_audit_fails_when_phase_missing():
    results = _complete_material_results()
    results["phase_9c_material_source_quality_ranking_owner_complete"] = False

    audit = build_material_completion_audit(results)

    assert audit["material_completion_audit_status"] == "FAIL_MATERIAL_COMPLETION_AUDIT"
    assert audit["material_completion_audit_complete"] is False
    assert "Material Source Quality Ranking Owner" in audit["material_completion_audit_missing_phases"]


def test_phase_9e_completion_audit_fails_when_material_validation_not_passing():
    results = _complete_material_results()
    results["material_validation_pass"] = False

    audit = build_material_completion_audit(results)

    assert audit["material_completion_audit_status"] == "FAIL_MATERIAL_COMPLETION_AUDIT"
    assert audit["material_completion_audit_complete"] is False
    assert any(
        "Material validation is not passing" in blocker
        for blocker in audit["material_completion_audit_blockers"]
    )


def test_phase_9e_completion_audit_fails_when_status_unknown():
    results = _complete_material_results()
    results["material_validation_owner_status"] = "UNKNOWN"

    audit = build_material_completion_audit(results)

    assert audit["material_completion_audit_complete"] is False
    assert any(
        "material validation status" in blocker.lower()
        for blocker in audit["material_completion_audit_blockers"]
    )


def test_phase_9e_attach_preserves_existing_results():
    results = _complete_material_results()
    results["thrust"] = 1000

    updated = attach_material_completion_audit(results)

    assert updated is results
    assert updated["thrust"] == 1000
    assert updated["phase_9e_material_completion_audit_complete"] is True
    assert "material_completion_audit_text" in updated