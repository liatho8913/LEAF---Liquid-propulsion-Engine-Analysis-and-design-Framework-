from pathlib import Path
import tempfile

from project_maintenance.production_historical_artifacts.leaf_qt.repository_source_truth_audit import write_repository_source_truth_audit


def test_source_truth_audit_uses_shared_artifact_io_successfully():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "leaf_qt").mkdir()
        (root / "leaf_qt" / "engine_solver.py").write_text(
            "def solve_engine(inputs):\n"
            "    return inputs\n",
            encoding="utf-8",
        )

        json_path = root / "artifacts" / "source_truth.json"
        txt_path = root / "artifacts" / "source_truth.txt"

        audit = write_repository_source_truth_audit(
            root=root,
            json_path=json_path,
            txt_path=txt_path,
        )

        assert audit["passed"] is True
        assert json_path.exists()
        assert txt_path.exists()
        assert "LEAF REPOSITORY SOURCE TRUTH AUDIT" in txt_path.read_text(encoding="utf-8")
        assert "LEAF_REPOSITORY_SOURCE_TRUTH_AUDIT_V1" in json_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    test_source_truth_audit_uses_shared_artifact_io_successfully()
    print("PASS_SOURCE_TRUTH_AUDIT_ARCHITECTURE_CORE_MIGRATION_TEST")
