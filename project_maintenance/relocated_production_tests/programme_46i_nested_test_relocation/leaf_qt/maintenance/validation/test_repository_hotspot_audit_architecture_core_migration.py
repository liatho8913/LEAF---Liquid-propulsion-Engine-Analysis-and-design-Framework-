from pathlib import Path

from project_maintenance.production_historical_artifacts.leaf_qt.repository_hotspot_audit import (
    build_repository_hotspot_audit,
    build_text_report,
)
from core.architecture.io import write_json_artifact, write_text_artifact, read_json_artifact


def test_hotspot_audit_can_use_shared_architecture_io(tmp_path):
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
            }
        ],
    }

    audit = build_repository_hotspot_audit(manifest)
    text = build_text_report(audit)

    json_path = tmp_path / "artifacts" / "hotspot.json"
    txt_path = tmp_path / "artifacts" / "hotspot.txt"

    write_json_artifact(audit, json_path)
    write_text_artifact(text, txt_path)

    loaded = read_json_artifact(json_path)

    assert loaded["schema"] == "LEAF_REPOSITORY_HOTSPOT_AUDIT_V1"
    assert loaded["summary"]["hotspots"] == 1
    assert txt_path.exists()
    assert "LEAF REPOSITORY HOTSPOT AUDIT" in txt_path.read_text(encoding="utf-8")


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        test_hotspot_audit_can_use_shared_architecture_io(Path(tmp))

    print("PASS_HOTSPOT_AUDIT_ARCHITECTURE_CORE_MIGRATION_TEST")
