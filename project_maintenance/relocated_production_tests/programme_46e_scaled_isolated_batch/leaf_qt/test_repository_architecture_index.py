from pathlib import Path
import tempfile

from repository_architecture_index import (
    build_repository_architecture_index,
    write_repository_architecture_index,
)


def test_repository_architecture_index_on_synthetic_tree():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "leaf_qt").mkdir()

        (root / "leaf_qt" / "regen_solver.py").write_text(
            "import math\n\n"
            "class RegenSolver:\n"
            "    pass\n\n"
            "def solve_regen():\n"
            "    return math.pi\n",
            encoding="utf-8",
        )

        (root / "leaf_qt" / "test_regen_solver.py").write_text(
            "def test_solver():\n"
            "    assert True\n",
            encoding="utf-8",
        )

        index = build_repository_architecture_index(root)

        assert index["schema"] == "LEAF_REPOSITORY_ARCHITECTURE_INDEX_V1"
        assert index["summary"]["python_files"] == 2
        assert index["summary"]["classes"] == 1
        assert index["summary"]["functions"] == 2
        assert index["summary"]["ast_parse_failures"] == 0
        assert index["summary"]["subsystem_counts"]["REGEN"] == 2
        assert index["summary"]["role_counts"]["TEST_CODE"] == 1


def test_repository_architecture_index_writes_json():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "module.py").write_text(
            "def f():\n"
            "    return 1\n",
            encoding="utf-8",
        )

        output = root / "artifacts" / "repository_architecture_index.json"
        index = write_repository_architecture_index(root, output)

        assert output.exists()
        assert index["summary"]["python_files"] == 1
        assert "module.py" in output.read_text(encoding="utf-8")


if __name__ == "__main__":
    test_repository_architecture_index_on_synthetic_tree()
    test_repository_architecture_index_writes_json()
    print("PASS_REPOSITORY_ARCHITECTURE_INDEX_TEST")
