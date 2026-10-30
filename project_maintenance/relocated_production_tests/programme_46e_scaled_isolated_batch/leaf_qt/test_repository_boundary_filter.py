from pathlib import Path
import tempfile

from repository_architecture_index import build_repository_architecture_index


def test_repository_boundary_filter_excludes_uploaded_and_packaged_trees():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        (root / "leaf_qt").mkdir()
        (root / "LEAF_UPLOAD" / "leaf_qt").mkdir(parents=True)
        (root / "LEAF_Minimal_Source" / "leaf_qt").mkdir(parents=True)
        (root / "artifacts").mkdir()

        (root / "leaf_qt" / "engine_solver.py").write_text(
            "def live_solver():\n"
            "    return True\n",
            encoding="utf-8",
        )

        (root / "LEAF_UPLOAD" / "leaf_qt" / "engine_solver.py").write_text(
            "def copied_solver():\n"
            "    return False\n",
            encoding="utf-8",
        )

        (root / "LEAF_Minimal_Source" / "leaf_qt" / "regen_solver.py").write_text(
            "def packaged_solver():\n"
            "    return False\n",
            encoding="utf-8",
        )

        (root / "artifacts" / "generated.py").write_text(
            "def generated():\n"
            "    return False\n",
            encoding="utf-8",
        )

        index = build_repository_architecture_index(root)
        paths = {entry["path"] for entry in index["files"]}

        assert "leaf_qt/engine_solver.py" in paths
        assert "LEAF_UPLOAD/leaf_qt/engine_solver.py" not in paths
        assert "LEAF_Minimal_Source/leaf_qt/regen_solver.py" not in paths
        assert "artifacts/generated.py" not in paths
        assert index["summary"]["python_files"] == 1


if __name__ == "__main__":
    test_repository_boundary_filter_excludes_uploaded_and_packaged_trees()
    print("PASS_REPOSITORY_BOUNDARY_FILTER_TEST")
