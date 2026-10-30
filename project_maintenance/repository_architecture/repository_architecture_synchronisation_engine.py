from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any

from leaf_qt.core.architecture.repository_metadata import build_repository_metadata
from project_maintenance.repository_architecture.repository_knowledge_database import build_repository_knowledge_database
from project_maintenance.repository_architecture.repository_dependency_ownership_graph import build_dependency_ownership_graph
from project_maintenance.repository_architecture.repository_architecture_validator import build_architecture_validation
from project_maintenance.repository_architecture.repository_semantic_classification_engine import build_semantic_classification
from project_maintenance.repository_architecture.repository_intelligence_api import build_repository_intelligence_snapshot
from project_maintenance.repository_architecture.repository_architecture_visualisation import build_architecture_visualisation

SCHEMA = "LEAF_REPOSITORY_ARCHITECTURE_SYNCHRONISATION_ENGINE_V1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def synchronise_repository_architecture(
    root: str | Path = ".",
    output_dir: str | Path = "_leaf_artifacts/repository_architecture/synchronised",
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    out = root_path / output_dir
    out.mkdir(parents=True, exist_ok=True)

    metadata = build_repository_metadata(root_path)
    database = build_repository_knowledge_database(root_path)
    graph = build_dependency_ownership_graph(root_path)
    validation = build_architecture_validation(root_path)
    semantic = build_semantic_classification(root_path)
    snapshot = build_repository_intelligence_snapshot(root_path)
    visualisation = build_architecture_visualisation(root_path)

    artefacts = {
        "metadata": out / "repository_metadata_v1.json",
        "database": out / "repository_knowledge_database_v1.json",
        "graph": out / "repository_dependency_ownership_graph_v1.json",
        "validation": out / "repository_architecture_validation_v1.json",
        "semantic": out / "repository_semantic_classification_v1.json",
        "snapshot": out / "repository_intelligence_api_snapshot_v1.json",
        "visualisation": out / "repository_architecture_visualisation_v1.json",
        "markdown_map": out / "repository_architecture_map.md",
        "mermaid_map": out / "repository_architecture_map.mmd",
    }

    write_json(artefacts["metadata"], metadata)
    write_json(artefacts["database"], database)
    write_json(artefacts["graph"], graph)
    write_json(artefacts["validation"], validation)
    write_json(artefacts["semantic"], semantic)
    write_json(artefacts["snapshot"], snapshot)
    write_json(artefacts["visualisation"], visualisation)
    artefacts["markdown_map"].write_text(visualisation["markdown"], encoding="utf-8")
    artefacts["mermaid_map"].write_text(visualisation["mermaid"], encoding="utf-8")

    result = {
        "schema": SCHEMA,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": validation["summary"]["error_count"] == 0,
        "summary": {
            "supported_files": metadata["summary"]["supported_files"],
            "python_files": metadata["summary"]["python_files"],
            "file_nodes": graph["summary"]["file_nodes"],
            "owner_nodes": graph["summary"]["owner_nodes"],
            "subsystem_nodes": graph["summary"]["subsystem_nodes"],
            "resolved_dependency_edges": graph["summary"]["resolved_dependency_edges"],
            "architecture_errors": validation["summary"]["error_count"],
            "architecture_warnings": validation["summary"]["warning_count"],
            "semantic_enriched_files": semantic["summary"]["semantic_enriched_files"],
            "artefact_count": len(artefacts),
        },
        "artefacts": {
            name: path.relative_to(root_path).as_posix()
            for name, path in artefacts.items()
        },
    }

    write_json(out / "repository_architecture_synchronisation_result_v1.json", result)
    return result


if __name__ == "__main__":
    result = synchronise_repository_architecture(".")
    summary = result["summary"]

    print("PASS_REPOSITORY_ARCHITECTURE_SYNCHRONISATION_ENGINE" if result["passed"] else "FAIL_REPOSITORY_ARCHITECTURE_SYNCHRONISATION_ENGINE")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"resolved_dependency_edges={summary['resolved_dependency_edges']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"architecture_warnings={summary['architecture_warnings']}")
    print(f"semantic_enriched_files={summary['semantic_enriched_files']}")
    print(f"artefact_count={summary['artefact_count']}")

    if not result["passed"]:
        raise SystemExit(1)
