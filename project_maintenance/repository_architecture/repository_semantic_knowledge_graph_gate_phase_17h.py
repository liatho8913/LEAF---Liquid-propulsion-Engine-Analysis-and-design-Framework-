from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_semantic_knowledge_graph_phase_17h import (
    SCHEMA,
    build_repository_semantic_knowledge_graph,
)
from project_maintenance.repository_architecture.roadmap_status_artifact_owner import RoadmapStatusArtifactOwner

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17h"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "repository_architecture" / "universal_repository_index_phase_17g.py",
    ROOT / "project_maintenance" / "repository_architecture" / "repository_semantic_knowledge_graph_phase_17h.py",
    ROOT / "project_maintenance" / "repository_architecture" / "repository_semantic_knowledge_graph_gate_phase_17h.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    try:
        graph = build_repository_semantic_knowledge_graph(ROOT)
    except Exception as exc:
        graph = {
            "schema": SCHEMA,
            "summary": {},
            "source_index_schema": None,
            "semantic_domains": {},
            "architectural_findings": [],
            "nodes": {},
            "edges": [],
        }
        failures.append(f"semantic_graph_build_failure={exc!r}")

    summary = graph.get("summary", {})
    domains = graph.get("semantic_domains", {})
    nodes = graph.get("nodes", {})
    edges = graph.get("edges", [])

    if graph.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if graph.get("source_index_schema") != "LEAF_UNIVERSAL_REPOSITORY_INDEX_PHASE_17G_V1":
        failures.append("source_index_schema_invalid")

    if summary.get("semantic_nodes", 0) <= 0:
        failures.append("no_semantic_nodes")

    if summary.get("semantic_edges", 0) <= 0:
        failures.append("no_semantic_edges")

    if summary.get("indexed_files", 0) <= 0:
        failures.append("no_indexed_files")

    if summary.get("semantic_domains", 0) <= 0:
        failures.append("no_semantic_domains")

    if summary.get("duplicate_scanner_created") is not False:
        failures.append("duplicate_scanner_created")

    if not summary.get("user_resource_domain_enabled"):
        failures.append("user_resource_domain_not_enabled")

    if "semantic_domain:user_resource_domain" not in nodes:
        failures.append("user_resource_domain_node_missing")

    if not any(edge.get("relation") == "depends_on" for edge in edges):
        failures.append("file_dependency_edges_missing")

    if not any(edge.get("relation") == "owned_by" for edge in edges):
        failures.append("ownership_edges_missing")

    if not any(edge.get("relation") == "targets_audience" for edge in edges):
        failures.append("audience_edges_missing")

    if not domains:
        failures.append("semantic_domains_empty")

    graph_path = OUT / "repository_semantic_knowledge_graph_phase_17h.json"
    gate_json = OUT / "repository_semantic_knowledge_graph_gate_phase_17h.json"
    gate_txt = OUT / "repository_semantic_knowledge_graph_gate_phase_17h.txt"

    graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    roadmap_paths = {"json": "", "report": ""}

    if not failures:
        owner = RoadmapStatusArtifactOwner(ROOT)
        roadmap_status = owner.build_status(
            current_major_feature="Repository Semantic Knowledge Graph",
            current_phase="17H",
            previous_completed_feature="17G Universal Repository Index",
            current_goal="Complete a semantic repository knowledge graph that explains ownership, audience, dependency, lifecycle, and user-resource meaning.",
            completed=[
                "17A Repository Discovery",
                "17B Repository Classification",
                "17C Shared Snapshot Architecture",
                "17D Repository Intelligence Consolidation",
                "17E Repository Roadmap Visibility System",
                "17F Repository Ownership Graph",
                "17G Universal Repository Index",
                "17H Repository Semantic Knowledge Graph",
            ],
            active_constraints=[
                "No automatic delete, archive, or relocation execution.",
                "The semantic graph must reuse the 17G universal index.",
                "Developer-facing and user-facing architecture remain separate semantic domains.",
                "Semantic meaning must be layered on existing metadata instead of duplicating filesystem scans.",
            ],
            remaining_work=[
                "17I Intelligent Repository Relocation",
                "17J Repository Health Monitor",
                "17K Repository Architecture Completion",
            ],
            next_phase="17I_INTELLIGENT_REPOSITORY_RELOCATION",
            safety_locks={
                "move_allowed": False,
                "archive_allowed": False,
                "delete_allowed": False,
                "automatic_delete_allowed": False,
                "deletion_started": False,
            },
            metrics={
                "semantic_nodes": summary.get("semantic_nodes", 0),
                "semantic_edges": summary.get("semantic_edges", 0),
                "semantic_domains": summary.get("semantic_domains", 0),
                "indexed_files": summary.get("indexed_files", 0),
                "owner_dependency_edges": summary.get("owner_dependency_edges", 0),
                "subsystem_dependency_edges": summary.get("subsystem_dependency_edges", 0),
                "domain_dependency_edges": summary.get("domain_dependency_edges", 0),
            },
        )
        roadmap_paths = owner.write_status(roadmap_status)

    result = {
        "phase": "17H",
        "feature": "REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": graph.get("schema"),
        "source_index_schema": graph.get("source_index_schema"),
        "summary": summary,
        "semantic_domains": domains,
        "architectural_findings": graph.get("architectural_findings", []),
        "failures": failures,
        "semantic_graph_json": graph_path.relative_to(ROOT).as_posix(),
        "roadmap_json": roadmap_paths["json"],
        "roadmap_report": roadmap_paths["report"],
        "completion_notice": "PHASE_17H_COMPLETE_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH_ESTABLISHED" if not failures else "PHASE_17H_BLOCKED",
        "next_phase": "17I_INTELLIGENT_REPOSITORY_RELOCATION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 17H REPOSITORY SEMANTIC KNOWLEDGE GRAPH",
        "====================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_index_schema={result['source_index_schema']}",
        f"semantic_nodes={summary.get('semantic_nodes', 0)}",
        f"semantic_edges={summary.get('semantic_edges', 0)}",
        f"indexed_files={summary.get('indexed_files', 0)}",
        f"semantic_domains={summary.get('semantic_domains', 0)}",
        f"owner_dependency_edges={summary.get('owner_dependency_edges', 0)}",
        f"subsystem_dependency_edges={summary.get('subsystem_dependency_edges', 0)}",
        f"domain_dependency_edges={summary.get('domain_dependency_edges', 0)}",
        f"user_resource_domain_enabled={summary.get('user_resource_domain_enabled')}",
        f"developer_infrastructure_domain_enabled={summary.get('developer_infrastructure_domain_enabled')}",
        f"duplicate_scanner_created={summary.get('duplicate_scanner_created')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"semantic_graph_json={result['semantic_graph_json']}",
        f"roadmap_json={result['roadmap_json']}",
        f"roadmap_report={result['roadmap_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_17H_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH" if result["passed"] else "FAIL_PHASE_17H_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH")
    print(f"schema={result['schema']}")
    print(f"source_index_schema={result['source_index_schema']}")
    print(f"semantic_nodes={summary.get('semantic_nodes', 0)}")
    print(f"semantic_edges={summary.get('semantic_edges', 0)}")
    print(f"indexed_files={summary.get('indexed_files', 0)}")
    print(f"semantic_domains={summary.get('semantic_domains', 0)}")
    print(f"owner_dependency_edges={summary.get('owner_dependency_edges', 0)}")
    print(f"subsystem_dependency_edges={summary.get('subsystem_dependency_edges', 0)}")
    print(f"domain_dependency_edges={summary.get('domain_dependency_edges', 0)}")
    print(f"user_resource_domain_enabled={summary.get('user_resource_domain_enabled')}")
    print(f"developer_infrastructure_domain_enabled={summary.get('developer_infrastructure_domain_enabled')}")
    print(f"duplicate_scanner_created={summary.get('duplicate_scanner_created')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"semantic_graph_json={result['semantic_graph_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"roadmap_report={result['roadmap_report']}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
