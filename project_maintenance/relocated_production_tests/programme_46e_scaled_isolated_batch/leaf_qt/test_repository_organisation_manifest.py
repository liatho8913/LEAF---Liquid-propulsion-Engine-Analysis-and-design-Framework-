from repository_organisation_manifest import (
    build_repository_organisation_manifest,
    build_text_report,
)


def test_repository_organisation_manifest_classifies_files():
    index = {
        "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
        "files": [
            {
                "path": "leaf_qt/regen_solver.py",
                "subsystem": "REGEN",
                "role": "SOLVER",
                "line_count": 100,
                "classes": ["RegenSolver"],
                "functions": ["solve"],
                "imports": [],
                "from_imports": [],
            },
            {
                "path": "leaf_qt/test_regen_solver.py",
                "subsystem": "REGEN",
                "role": "TEST_CODE",
                "line_count": 20,
                "classes": [],
                "functions": ["test_solver"],
                "imports": [],
                "from_imports": [],
            },
            {
                "path": "leaf_qt/phase_16u_patch.py",
                "subsystem": "UNCLASSIFIED",
                "role": "PHASE_ARTIFACT",
                "line_count": 10,
                "classes": [],
                "functions": [],
                "imports": [],
                "from_imports": [],
            },
        ],
    }

    manifest = build_repository_organisation_manifest(index)

    assert manifest["schema"] == "LEAF_REPOSITORY_ORGANISATION_MANIFEST_V1"
    assert manifest["summary"]["files_classified"] == 3
    assert manifest["safe_to_apply_moves"] is False

    files = {item["path"]: item for item in manifest["files"]}

    assert files["leaf_qt/regen_solver.py"]["recommended_folder"] == "leaf_qt/modules/regen"
    assert files["leaf_qt/regen_solver.py"]["recommended_action"] == "PROPOSE_MOVE"

    assert files["leaf_qt/test_regen_solver.py"]["permanence"] == "TEST_INFRASTRUCTURE"

    assert files["leaf_qt/phase_16u_patch.py"]["permanence"] == "TEMPORARY_OR_MIGRATION_REVIEW"


def test_repository_organisation_manifest_report():
    manifest = build_repository_organisation_manifest(
        {
            "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
            "files": [],
        }
    )

    report = build_text_report(manifest)

    assert "LEAF REPOSITORY ORGANISATION MANIFEST" in report
    assert "safe_to_apply_moves=False" in report


if __name__ == "__main__":
    test_repository_organisation_manifest_classifies_files()
    test_repository_organisation_manifest_report()
    print("PASS_REPOSITORY_ORGANISATION_MANIFEST_TEST")
