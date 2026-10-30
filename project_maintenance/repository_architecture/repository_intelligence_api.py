from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leaf_qt.core.architecture.repository_metadata import (
    build_repository_metadata,
)
from project_maintenance.repository_architecture.repository_knowledge_database import (
    RepositoryKnowledgeQuery,
    build_repository_knowledge_database,
    query_database,
)
from project_maintenance.repository_architecture.repository_dependency_ownership_graph import (
    build_dependency_ownership_graph,
)
from project_maintenance.repository_architecture.repository_architecture_validator import (
    build_architecture_validation,
)
from project_maintenance.repository_architecture.repository_semantic_classification_engine import (
    build_semantic_classification,
)

SCHEMA = "LEAF_REPOSITORY_INTELLIGENCE_API_V1"


@dataclass(frozen=True)
class RepositoryIntelligenceSnapshot:
    schema: str
    root: str
    metadata: dict[str, Any]
    database: dict[str, Any]
    graph: dict[str, Any]
    validation: dict[str, Any]
    semantic: dict[str, Any]


class RepositoryIntelligenceAPI:
    def __init__(self, root: str | Path = ".") -> None:
        self.root = Path(root).resolve()
        self._metadata: dict[str, Any] | None = None
        self._database: dict[str, Any] | None = None
        self._graph: dict[str, Any] | None = None
        self._validation: dict[str, Any] | None = None
        self._semantic: dict[str, Any] | None = None

    def metadata(self) -> dict[str, Any]:
        if self._metadata is None:
            self._metadata = build_repository_metadata(self.root)
        return self._metadata

    def database(self) -> dict[str, Any]:
        if self._database is None:
            self._database = build_repository_knowledge_database(self.root)
        return self._database

    def graph(self) -> dict[str, Any]:
        if self._graph is None:
            self._graph = build_dependency_ownership_graph(self.root)
        return self._graph

    def validation(self) -> dict[str, Any]:
        if self._validation is None:
            self._validation = build_architecture_validation(self.root)
        return self._validation

    def semantic(self) -> dict[str, Any]:
        if self._semantic is None:
            self._semantic = build_semantic_classification(self.root)
        return self._semantic

    def snapshot(self) -> RepositoryIntelligenceSnapshot:
        return RepositoryIntelligenceSnapshot(
            schema=SCHEMA,
            root=str(self.root),
            metadata=self.metadata(),
            database=self.database(),
            graph=self.graph(),
            validation=self.validation(),
            semantic=self.semantic(),
        )

    def file(self, relative_path: str) -> dict[str, Any] | None:
        db_file = self.database()["files"].get(relative_path)
        semantic_file = self.semantic()["files"].get(relative_path)

        if db_file is None and semantic_file is None:
            return None

        return {
            "path": relative_path,
            "metadata": db_file,
            "semantic": semantic_file,
            "graph": self.graph()["files"].get(relative_path),
        }

    def files_by_layer(self, layer: str) -> list[dict[str, Any]]:
        return query_database(self.database(), RepositoryKnowledgeQuery(layer=layer))

    def files_by_subsystem(self, subsystem: str) -> list[dict[str, Any]]:
        return query_database(self.database(), RepositoryKnowledgeQuery(subsystem=subsystem))

    def files_by_role(self, role: str) -> list[dict[str, Any]]:
        return query_database(self.database(), RepositoryKnowledgeQuery(role=role))

    def architectural_ownership(self) -> dict[str, Any]:
        graph = self.graph()

        return {
            "schema": graph["schema"],
            "responsibilities": graph.get(
                "architectural_responsibilities",
                {},
            ),
            "ambiguous": graph.get(
                "ambiguous_architectural_responsibilities",
                [],
            ),
            "unresolved": graph.get(
                "unresolved_architectural_responsibilities",
                [],
            ),
        }

    def owner_files(self, owner: str) -> list[str]:
        return self.graph()["owners"].get(owner, {}).get("files", [])

    def subsystem_files(self, subsystem: str) -> list[str]:
        return self.graph()["subsystems"].get(subsystem, {}).get("files", [])

    def file_dependencies(self, relative_path: str) -> list[dict[str, str]]:
        return [
            edge for edge in self.graph()["dependency_edges"]
            if edge["from"] == relative_path
        ]

    def file_dependents(self, relative_path: str) -> list[dict[str, str]]:
        return [
            edge for edge in self.graph()["dependency_edges"]
            if edge["to"] == relative_path
        ]

    def architecture_errors(self) -> list[dict[str, Any]]:
        return [
            issue for issue in self.validation()["issues"]
            if issue.get("severity") == "ERROR"
        ]

    def architecture_warnings(self) -> list[dict[str, Any]]:
        return [
            issue for issue in self.validation()["issues"]
            if issue.get("severity") == "WARN"
        ]

    def architecture_audit(self) -> dict[str, Any]:
        """Return one canonical, metadata-backed architecture audit view."""
        files = [
            item for item in self.metadata()["files"]
            if item.get("suffix") == ".py"
            and item.get("source_class") != "non_operational"
        ]

        source_class_counts: dict[str, int] = {}
        role_counts: dict[str, int] = {}
        legacy_or_phase_files: list[str] = []
        dead_candidates: list[str] = []

        for item in files:
            source_class = str(item.get("source_class", "support"))
            role = str(item.get("role", "unclassified"))

            source_class_counts[source_class] = (
                source_class_counts.get(source_class, 0) + 1
            )

            role_counts[role] = role_counts.get(role, 0) + 1

            path = str(item.get("path", ""))
            lowered = path.lower()
            name = Path(path).name.lower()

            if (
                "legacy" in lowered
                or "old" in lowered
                or "backup" in lowered
                or name.startswith("phase_")
                or "_phase_" in name
            ):
                legacy_or_phase_files.append(path)

            if name != "__init__.py" and (
                (
                    int(item.get("line_count", 0)) <= 5
                    and not item.get("classes")
                    and not item.get("functions")
                )
                or "unused" in name
                or "deprecated" in name
                or "orphan" in name
            ):
                dead_candidates.append(path)

        largest = sorted(
            (
                {
                    "path": str(item.get("path", "")),
                    "line_count": int(item.get("line_count", 0)),
                }
                for item in files
            ),
            key=lambda item: item["line_count"],
            reverse=True,
        )[:25]

        return {
            "schema": "LEAF_REPOSITORY_ARCHITECTURE_AUDIT_V1",
            "operational_python_files": len(files),
            "operational_python_lines": sum(
                int(item.get("line_count", 0))
                for item in files
            ),
            "source_class_counts": dict(
                sorted(source_class_counts.items())
            ),
            "role_counts": dict(sorted(role_counts.items())),
            "legacy_or_phase_file_count": len(
                legacy_or_phase_files
            ),
            "dead_candidate_count": len(dead_candidates),
            "largest_operational_python_files": largest,
            "legacy_or_phase_files": sorted(
                legacy_or_phase_files
            ),
            "dead_candidates": sorted(dead_candidates),

            # Duplicate ownership requires graph-aware analysis.
            # The old 38A path/name heuristic is intentionally
            # not preserved.
            "duplicate_ownership_assessment": (
                "DEFERRED_TO_CANONICAL_OWNER_ANALYSIS"
            ),
        }

    def summary(self) -> dict[str, Any]:
        metadata_summary = self.metadata()["summary"]
        graph_summary = self.graph()["summary"]
        validation_summary = self.validation()["summary"]
        semantic_summary = self.semantic()["summary"]
        architecture_audit = self.architecture_audit()

        return {
            "schema": SCHEMA,
            "root": str(self.root),
            "supported_files": metadata_summary["supported_files"],
            "python_files": metadata_summary["python_files"],
            "source_class_counts": metadata_summary.get("source_class_counts", {}),
            "excluded_non_operational_roots": metadata_summary.get("excluded_non_operational_roots", []),
            "file_nodes": graph_summary["file_nodes"],
            "owner_nodes": graph_summary["owner_nodes"],
            "subsystem_nodes": graph_summary["subsystem_nodes"],
            "architectural_responsibilities": graph_summary.get(
                "architectural_responsibilities",
                0,
            ),
            "ambiguous_architectural_responsibilities": (
                graph_summary.get(
                    "ambiguous_architectural_responsibilities",
                    0,
                )
            ),
            "unresolved_architectural_responsibilities": (
                graph_summary.get(
                    "unresolved_architectural_responsibilities",
                    0,
                )
            ),
            "resolved_dependency_edges": graph_summary["resolved_dependency_edges"],
            "architecture_errors": validation_summary["error_count"],
            "architecture_warnings": validation_summary["warning_count"],
            "semantic_enriched_files": semantic_summary["semantic_enriched_files"],
            "semantic_signal_count": semantic_summary["signal_count"],
            "operational_python_files": architecture_audit["operational_python_files"],
            "operational_python_lines": architecture_audit["operational_python_lines"],
            "legacy_or_phase_file_count": architecture_audit["legacy_or_phase_file_count"],
            "dead_candidate_count": architecture_audit["dead_candidate_count"],
        }

    def explain_file(self, relative_path: str) -> dict[str, Any]:
        file_payload = self.file(relative_path)
        if file_payload is None:
            return {
                "schema": SCHEMA,
                "path": relative_path,
                "found": False,
                "explanation": "File is not present in the repository intelligence database.",
            }

        metadata = file_payload["metadata"] or {}
        semantic = file_payload["semantic"] or {}
        graph = file_payload["graph"] or {}

        return {
            "schema": SCHEMA,
            "path": relative_path,
            "found": True,
            "layer": metadata.get("layer"),
            "source_class": metadata.get("source_class"),
            "metadata_subsystem": metadata.get("subsystem"),
            "metadata_role": metadata.get("role"),
            "semantic_subsystem": semantic.get("semantic_subsystem"),
            "semantic_role": semantic.get("semantic_role"),
            "semantic_owner": semantic.get("semantic_owner"),
            "owner": graph.get("owner"),
            "confidence": semantic.get("semantic_confidence", metadata.get("confidence")),
            "dominant_signal": semantic.get("dominant_signal"),
            "classification_reason": semantic.get("classification_reason"),
            "dependencies": self.file_dependencies(relative_path),
            "dependents": self.file_dependents(relative_path),
        }


def build_repository_intelligence_snapshot(root: str | Path = ".") -> dict[str, Any]:
    api = RepositoryIntelligenceAPI(root)
    snapshot = api.snapshot()

    return {
        "schema": snapshot.schema,
        "root": snapshot.root,
        "summary": api.summary(),
        "metadata_schema": snapshot.metadata["schema"],
        "database_schema": snapshot.database["schema"],
        "graph_schema": snapshot.graph["schema"],
        "validation_schema": snapshot.validation["schema"],
        "semantic_schema": snapshot.semantic["schema"],
        "architecture_audit": api.architecture_audit(),
    }


def write_repository_intelligence_snapshot(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/repository_intelligence_api_snapshot_v1.json",
) -> dict[str, Any]:
    snapshot = build_repository_intelligence_snapshot(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


if __name__ == "__main__":
    snapshot = write_repository_intelligence_snapshot(".")
    summary = snapshot["summary"]

    print("LEAF_REPOSITORY_INTELLIGENCE_API")
    print(f"schema={snapshot['schema']}")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"resolved_dependency_edges={summary['resolved_dependency_edges']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"architecture_warnings={summary['architecture_warnings']}")
    print(f"semantic_enriched_files={summary['semantic_enriched_files']}")
