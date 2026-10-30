from project_maintenance.production_historical_artifacts.leaf_qt.contract_adoption_audit import build_contract_adoption_audit, build_text_report


def test_contract_adoption_audit_recommends_solver_contract():
    index = {
        "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
        "files": [
            {
                "path": "leaf_qt/engine_solver.py",
                "subsystem": "SOLVER",
                "role": "SOLVER",
                "line_count": 20000,
                "classes": ["EngineSolver"],
                "functions": ["solve_engine"],
            }
        ],
    }

    audit = build_contract_adoption_audit(index)

    assert audit["schema"] == "LEAF_CONTRACT_ADOPTION_AUDIT_V1"
    assert audit["summary"]["candidates"] == 1
    assert audit["candidates"][0]["recommended_contract"] == "SolverContract"
    assert audit["candidates"][0]["priority"] == "FIRST_WAVE"


def test_contract_adoption_audit_recommends_ui_contract():
    index = {
        "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
        "files": [
            {
                "path": "leaf_qt/regen_cross_section_viewer.py",
                "subsystem": "UI_VIEWER",
                "role": "UI_VIEWER",
                "line_count": 12000,
                "classes": ["RegenCrossSectionViewer"],
                "functions": ["refresh_viewer"],
            }
        ],
    }

    audit = build_contract_adoption_audit(index)

    assert audit["summary"]["candidates"] == 1
    assert audit["candidates"][0]["recommended_contract"] == "UIPanelContract"
    assert audit["candidates"][0]["priority"] == "FIRST_WAVE"


def test_contract_adoption_audit_deprioritises_tests_and_phase_files():
    index = {
        "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
        "files": [
            {
                "path": "project_maintenance/phase_16u_solver_patch.py",
                "subsystem": "SOLVER",
                "role": "SOLVER",
                "line_count": 100,
                "classes": [],
                "functions": ["solve_patch"],
            }
        ],
    }

    audit = build_contract_adoption_audit(index)

    assert audit["summary"]["candidates"] == 1
    assert audit["candidates"][0]["adoption_score"] < 80


def test_contract_adoption_report_contains_first_wave():
    audit = build_contract_adoption_audit(
        {
            "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
            "files": [
                {
                    "path": "leaf_qt/report_ownership.py",
                    "subsystem": "REPORTING",
                    "role": "REPORT_OWNER",
                    "line_count": 1000,
                    "classes": ["ReportOwner"],
                    "functions": ["build_report"],
                }
            ],
        }
    )

    report = build_text_report(audit)

    assert "LEAF CONTRACT ADOPTION AUDIT" in report
    assert "ReportingContract" in report
    assert "FIRST WAVE" in report


if __name__ == "__main__":
    test_contract_adoption_audit_recommends_solver_contract()
    test_contract_adoption_audit_recommends_ui_contract()
    test_contract_adoption_audit_deprioritises_tests_and_phase_files()
    test_contract_adoption_report_contains_first_wave()
    print("PASS_CONTRACT_ADOPTION_AUDIT_TEST")
