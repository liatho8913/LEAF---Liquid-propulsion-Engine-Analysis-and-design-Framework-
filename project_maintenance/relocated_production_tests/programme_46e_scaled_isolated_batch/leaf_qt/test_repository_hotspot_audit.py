from project_maintenance.production_historical_artifacts.leaf_qt.repository_hotspot_audit import (
    build_repository_hotspot_audit,
    build_text_report,
)


def test_repository_hotspot_audit_ranks_critical_files():
    manifest = {
        "schema": "LEAF_REPOSITORY_ORGANISATION_MANIFEST_V1",
        "files": [
            {
                "path": "leaf_qt/engine_solver.py",
                "subsystem": "SOLVER",
                "role": "SOLVER",
                "permanence": "PERMANENT_REVIEW",
                "recommended_action": "PROPOSE_MOVE",
                "recommended_folder": "leaf_qt/core/solvers",
                "line_count": 20784,
            },
            {
                "path": "promethean_forge.py",
                "subsystem": "UNCLASSIFIED",
                "role": "MODULE_CODE",
                "permanence": "REVIEW_REQUIRED",
                "recommended_action": "CLASSIFY_MANUALLY",
                "recommended_folder": "project_maintenance/review_required",
                "line_count": 10809,
            },
            {
                "path": "leaf_qt/small_module.py",
                "subsystem": "REGEN",
                "role": "MODULE_CODE",
                "permanence": "PERMANENT_REVIEW",
                "recommended_action": "PROPOSE_MOVE",
                "recommended_folder": "leaf_qt/modules/regen",
                "line_count": 50,
            },
        ],
    }

    audit = build_repository_hotspot_audit(manifest)

    assert audit["schema"] == "LEAF_REPOSITORY_HOTSPOT_AUDIT_V1"
    assert audit["summary"]["hotspots"] == 2
    assert audit["summary"]["critical"] >= 1
    assert audit["top_hotspots"][0]["priority"] == "CRITICAL"
    assert audit["top_hotspots"][0]["next_action"] in {
        "SPLIT_INTO_STABLE_CONTRACTS_AND_SUBMODULES",
        "CLASSIFY_SUBSYSTEM_AND_ASSIGN_OWNER",
    }


def test_repository_hotspot_audit_detects_temporary_phase_artifact():
    manifest = {
        "schema": "LEAF_REPOSITORY_ORGANISATION_MANIFEST_V1",
        "files": [
            {
                "path": "project_maintenance/phase_16u_patch.py",
                "subsystem": "UNCLASSIFIED",
                "role": "PHASE_ARTIFACT",
                "permanence": "TEMPORARY_OR_MIGRATION_REVIEW",
                "recommended_action": "CLASSIFY_MANUALLY",
                "recommended_folder": "project_maintenance/review_required",
                "line_count": 100,
            }
        ],
    }

    audit = build_repository_hotspot_audit(manifest)

    assert audit["summary"]["hotspots"] == 1
    hotspot = audit["hotspots"][0]
    assert "PHASE_NAMED_ARTIFACT" in hotspot["reasons"]
    assert hotspot["next_action"] == "CLASSIFY_SUBSYSTEM_AND_ASSIGN_OWNER"


def test_repository_hotspot_report_contains_top_hotspots():
    audit = build_repository_hotspot_audit(
        {
            "schema": "LEAF_REPOSITORY_ORGANISATION_MANIFEST_V1",
            "files": [
                {
                    "path": "leaf_qt/large_owner.py",
                    "subsystem": "REGEN",
                    "role": "OWNER",
                    "permanence": "PERMANENT_REVIEW",
                    "recommended_action": "PROPOSE_MOVE",
                    "recommended_folder": "leaf_qt/modules/regen",
                    "line_count": 600,
                }
            ],
        }
    )

    report = build_text_report(audit)

    assert "LEAF REPOSITORY HOTSPOT AUDIT" in report
    assert "large_owner.py" in report


if __name__ == "__main__":
    test_repository_hotspot_audit_ranks_critical_files()
    test_repository_hotspot_audit_detects_temporary_phase_artifact()
    test_repository_hotspot_report_contains_top_hotspots()
    print("PASS_REPOSITORY_HOTSPOT_AUDIT_TEST")
