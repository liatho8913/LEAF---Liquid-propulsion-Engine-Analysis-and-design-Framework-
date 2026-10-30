from pathlib import Path

from project_maintenance.production_historical_artifacts.leaf_qt.contract_adoption_audit import build_contract_adoption_audit, build_text_report
from core.architecture.io import write_json_artifact, write_text_artifact, read_json_artifact


def test_contract_adoption_audit_can_use_shared_architecture_io(tmp_path):
    index = {
        "schema": "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1",
        "files": [
            {
                "path": "leaf_qt/engine_solver.py",
                "subsystem": "SOLVER",
                "role": "SOLVER",
                "line_count": 20784,
                "classes": ["EngineSolver"],
                "functions": ["solve_engine"],
            }
        ],
    }

    audit = build_contract_adoption_audit(index)
    text = build_text_report(audit)

    json_path = tmp_path / "artifacts" / "contract_adoption.json"
    txt_path = tmp_path / "artifacts" / "contract_adoption.txt"

    write_json_artifact(audit, json_path)
    write_text_artifact(text, txt_path)

    loaded = read_json_artifact(json_path)

    assert loaded["schema"] == "LEAF_CONTRACT_ADOPTION_AUDIT_V1"
    assert loaded["summary"]["candidates"] == 1
    assert txt_path.exists()
    assert "LEAF CONTRACT ADOPTION AUDIT" in txt_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        test_contract_adoption_audit_can_use_shared_architecture_io(Path(tmp))

    print("PASS_CONTRACT_ADOPTION_AUDIT_ARCHITECTURE_CORE_MIGRATION_TEST")
