from project_maintenance.production_historical_artifacts.leaf_qt.contract_adoption_audit import build_contract_adoption_audit


def test_contract_adoption_audit_ignores_empty_init_files():
    index = {
        "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
        "files": [
            {
                "path": "leaf_qt/core/solver_adapters/__init__.py",
                "subsystem": "SOLVER",
                "role": "SOLVER",
                "line_count": 0,
                "classes": [],
                "functions": [],
            },
            {
                "path": "leaf_qt/engine_solver.py",
                "subsystem": "SOLVER",
                "role": "SOLVER",
                "line_count": 20784,
                "classes": ["EngineSolver"],
                "functions": ["solve_engine"],
            },
        ],
    }

    audit = build_contract_adoption_audit(index)
    paths = {item["path"] for item in audit["candidates"]}

    assert "leaf_qt/core/solver_adapters/__init__.py" not in paths
    assert "leaf_qt/engine_solver.py" in paths


def test_contract_adoption_audit_ignores_contract_infrastructure():
    index = {
        "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
        "files": [
            {
                "path": "leaf_qt/core/contracts/base_contracts.py",
                "subsystem": "UNCLASSIFIED",
                "role": "MODULE_CODE",
                "line_count": 100,
                "classes": ["SolverContract"],
                "functions": ["validate_contract_metadata"],
            }
        ],
    }

    audit = build_contract_adoption_audit(index)

    assert audit["summary"]["candidates"] == 0


def test_contract_adoption_audit_ignores_adapter_infrastructure():
    index = {
        "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
        "files": [
            {
                "path": "leaf_qt/core/solver_adapters/engine_solver_adapter.py",
                "subsystem": "SOLVER",
                "role": "SOLVER",
                "line_count": 52,
                "classes": ["EngineSolverReadOnlyAdapter"],
                "functions": ["make_engine_solver_read_only_adapter"],
            }
        ],
    }

    audit = build_contract_adoption_audit(index)

    assert audit["summary"]["candidates"] == 0


if __name__ == "__main__":
    test_contract_adoption_audit_ignores_empty_init_files()
    test_contract_adoption_audit_ignores_contract_infrastructure()
    test_contract_adoption_audit_ignores_adapter_infrastructure()
    print("PASS_CONTRACT_ADOPTION_AUDIT_REFINEMENT_TEST")
