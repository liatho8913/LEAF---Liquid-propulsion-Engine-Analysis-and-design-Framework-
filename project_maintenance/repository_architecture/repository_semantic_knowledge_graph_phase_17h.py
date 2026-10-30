from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.universal_repository_index_phase_17g import (
    build_universal_repository_index,
)

SCHEMA = "LEAF_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH_PHASE_17H_V1"


def _node_id(kind: str, value: str) -> str:
    safe = str(value).strip().replace("/", "::")
    return f"{kind}:{safe}"


def _add_node(nodes: dict[str, dict[str, Any]], node_id: str, kind: str, label: str, **attrs: Any) -> None:
    nodes[node_id] = {
        "id": node_id,
        "kind": kind,
        "label": label,
        **attrs,
    }


def _add_edge(edges: list[dict[str, Any]], source: str, target: str, relation: str, **attrs: Any) -> None:
    edges.append({
        "source": source,
        "target": target,
        "relation": relation,
        **attrs,
    })


def _semantic_domain(entry: dict[str, Any]) -> str:
    audience = entry.get("audience")
    role = str(entry.get("role") or "").lower()
    path = entry.get("path", "")

    if audience == "engineer_user":
        return "user_resource_domain"
    if audience == "developer":
        if "gate" in role or "validation" in role or "test" in path:
            return "validation_and_gate_domain"
        if "owner" in role:
            return "ownership_domain"
        if "controller" in role:
            return "controller_domain"
        if "report" in role:
            return "reporting_domain"
        return "developer_infrastructure_domain"
    if audience == "generated":
        return "generated_evidence_domain"
    if audience == "repository_history":
        return "historical_recovery_domain"
    return "unclassified_semantic_domain"


def build_repository_semantic_knowledge_graph(root: str | Path = ".") -> dict[str, Any]:
    index = build_universal_repository_index(root)
    entries = index["entries"]

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    _add_node(nodes, "platform:LEAF", "platform", "LEAF Engineering Platform")

    for concept in [
        "developer_architecture",
        "user_architecture",
        "canonical_location",
        "ownership",
        "dependency",
        "validation",
        "repository_visibility",
        "sustainability",
    ]:
        _add_node(nodes, _node_id("concept", concept), "concept", concept)
        _add_edge(edges, "platform:LEAF", _node_id("concept", concept), "has_architectural_concept")

    semantic_domains: dict[str, list[str]] = {}

    for path, entry in entries.items():
        file_id = _node_id("file", path)
        domain = _semantic_domain(entry)
        semantic_domains.setdefault(domain, []).append(path)

        _add_node(
            nodes,
            file_id,
            "file",
            path,
            owner=entry.get("owner"),
            subsystem=entry.get("subsystem"),
            audience=entry.get("audience"),
            visibility=entry.get("visibility"),
            lifecycle=entry.get("lifecycle"),
            authority=entry.get("authority"),
            semantic_domain=domain,
            canonical_location=entry.get("canonical_location"),
        )

        domain_id = _node_id("semantic_domain", domain)
        if domain_id not in nodes:
            _add_node(nodes, domain_id, "semantic_domain", domain)
            _add_edge(edges, "platform:LEAF", domain_id, "contains_semantic_domain")

        _add_edge(edges, file_id, domain_id, "belongs_to_semantic_domain")

        for kind, key, relation in [
            ("owner", entry.get("owner"), "owned_by"),
            ("subsystem", entry.get("subsystem"), "belongs_to_subsystem"),
            ("audience", entry.get("audience"), "targets_audience"),
            ("visibility", entry.get("visibility"), "has_visibility"),
            ("lifecycle", entry.get("lifecycle"), "has_lifecycle"),
            ("authority", entry.get("authority"), "has_authority"),
            ("root", entry.get("top_level_root"), "located_under_root"),
            ("canonical_location", entry.get("canonical_location"), "has_canonical_location"),
            ("role", entry.get("role"), "has_role"),
        ]:
            if key:
                nid = _node_id(kind, key)
                if nid not in nodes:
                    _add_node(nodes, nid, kind, str(key))
                _add_edge(edges, file_id, nid, relation)

        for dependency in entry.get("outbound_dependencies", []):
            if dependency in entries:
                _add_edge(edges, file_id, _node_id("file", dependency), "depends_on")

    owner_dependency_edges: set[tuple[str, str]] = set()
    subsystem_dependency_edges: set[tuple[str, str]] = set()
    domain_dependency_edges: set[tuple[str, str]] = set()

    for path, entry in entries.items():
        source_owner = entry.get("owner")
        source_subsystem = entry.get("subsystem")
        source_domain = _semantic_domain(entry)

        for dependency in entry.get("outbound_dependencies", []):
            target = entries.get(dependency)
            if not target:
                continue

            target_owner = target.get("owner")
            target_subsystem = target.get("subsystem")
            target_domain = _semantic_domain(target)

            if source_owner and target_owner and source_owner != target_owner:
                owner_dependency_edges.add((source_owner, target_owner))

            if source_subsystem and target_subsystem and source_subsystem != target_subsystem:
                subsystem_dependency_edges.add((source_subsystem, target_subsystem))

            if source_domain and target_domain and source_domain != target_domain:
                domain_dependency_edges.add((source_domain, target_domain))

    for source, target in sorted(owner_dependency_edges):
        _add_edge(edges, _node_id("owner", source), _node_id("owner", target), "owner_depends_on_owner")

    for source, target in sorted(subsystem_dependency_edges):
        _add_edge(edges, _node_id("subsystem", source), _node_id("subsystem", target), "subsystem_depends_on_subsystem")

    for source, target in sorted(domain_dependency_edges):
        _add_edge(edges, _node_id("semantic_domain", source), _node_id("semantic_domain", target), "semantic_domain_depends_on_domain")

    architectural_findings = []

    if "user_resource_domain" in semantic_domains:
        architectural_findings.append({
            "finding": "user_resource_domain_detected",
            "meaning": "LEAF now distinguishes engineer-facing resources from developer-facing infrastructure.",
            "file_count": len(semantic_domains["user_resource_domain"]),
        })

    if "developer_infrastructure_domain" in semantic_domains:
        architectural_findings.append({
            "finding": "developer_infrastructure_domain_detected",
            "meaning": "Developer infrastructure is indexed as a separate semantic domain.",
            "file_count": len(semantic_domains["developer_infrastructure_domain"]),
        })

    architectural_findings.append({
        "finding": "semantic_graph_uses_universal_index",
        "meaning": "17H reuses the 17G index and does not create another repository scanner.",
        "source_schema": index["schema"],
    })

    return {
        "schema": SCHEMA,
        "phase": "17H",
        "feature": "REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH",
        "source_index_schema": index["schema"],
        "design_principle": "Semantic architecture should explain what repository objects mean, not merely where they are.",
        "summary": {
            "semantic_nodes": len(nodes),
            "semantic_edges": len(edges),
            "indexed_files": len(entries),
            "semantic_domains": len(semantic_domains),
            "owner_dependency_edges": len(owner_dependency_edges),
            "subsystem_dependency_edges": len(subsystem_dependency_edges),
            "domain_dependency_edges": len(domain_dependency_edges),
            "user_resource_domain_enabled": "user_resource_domain" in semantic_domains,
            "developer_infrastructure_domain_enabled": any(
                key.endswith("_domain") for key in semantic_domains
            ),
            "duplicate_scanner_created": False,
        },
        "semantic_domains": {
            key: {
                "file_count": len(value),
                "sample_files": sorted(value)[:50],
            }
            for key, value in sorted(semantic_domains.items())
        },
        "architectural_findings": architectural_findings,
        "nodes": dict(sorted(nodes.items())),
        "edges": edges,
        "resource_roots": index.get("resource_roots", {}),
        "user_resource_ownership_layer": index.get("user_resource_ownership_layer", {}),
    }


def write_repository_semantic_knowledge_graph(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/phase_17h/repository_semantic_knowledge_graph_phase_17h.json",
) -> dict[str, Any]:
    graph = build_repository_semantic_knowledge_graph(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return graph


if __name__ == "__main__":
    graph = write_repository_semantic_knowledge_graph(".")
    summary = graph["summary"]

    print("LEAF_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH_PHASE_17H")
    print(f"schema={graph['schema']}")
    print(f"source_index_schema={graph['source_index_schema']}")
    print(f"semantic_nodes={summary['semantic_nodes']}")
    print(f"semantic_edges={summary['semantic_edges']}")
    print(f"semantic_domains={summary['semantic_domains']}")
    print(f"user_resource_domain_enabled={summary['user_resource_domain_enabled']}")
    print(f"duplicate_scanner_created={summary['duplicate_scanner_created']}")
