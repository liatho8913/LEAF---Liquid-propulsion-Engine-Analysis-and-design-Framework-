from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.repository_ownership_graph_phase_17f import (
    build_repository_ownership_graph,
)

SCHEMA = "LEAF_UNIVERSAL_REPOSITORY_INDEX_PHASE_17G_V1"


def _tokens(*values: Any) -> list[str]:
    found: set[str] = set()

    for value in values:
        if value is None:
            continue

        text = str(value).replace("/", " ").replace("_", " ").replace("-", " ").replace(".", " ")
        for part in text.split():
            cleaned = part.strip().lower()
            if cleaned:
                found.add(cleaned)

    return sorted(found)


def _add(index: dict[str, list[str]], key: str | None, path: str) -> None:
    if not key:
        key = "unclassified"
    index.setdefault(str(key), []).append(path)


def _sorted_unique_index(index: dict[str, list[str]]) -> dict[str, list[str]]:
    return {key: sorted(set(values)) for key, values in sorted(index.items())}


def build_universal_repository_index(root: str | Path = ".") -> dict[str, Any]:
    graph = build_repository_ownership_graph(root)
    files = graph["files"]

    entries: dict[str, dict[str, Any]] = {}

    by_owner: dict[str, list[str]] = {}
    by_subsystem: dict[str, list[str]] = {}
    by_audience: dict[str, list[str]] = {}
    by_visibility: dict[str, list[str]] = {}
    by_lifecycle: dict[str, list[str]] = {}
    by_authority: dict[str, list[str]] = {}
    by_root: dict[str, list[str]] = {}
    by_role: dict[str, list[str]] = {}
    by_status: dict[str, list[str]] = {}
    by_layer: dict[str, list[str]] = {}
    by_canonical_location: dict[str, list[str]] = {}
    token_index: dict[str, list[str]] = {}

    inbound_dependencies: dict[str, list[str]] = {path: [] for path in files}
    outbound_dependencies: dict[str, list[str]] = {path: [] for path in files}

    for edge in graph.get("dependency_edges", []):
        source = edge.get("from")
        target = edge.get("to")
        if source in outbound_dependencies and target:
            outbound_dependencies[source].append(target)
        if target in inbound_dependencies and source:
            inbound_dependencies[target].append(source)

    for path, meta in files.items():
        entry_tokens = _tokens(
            path,
            meta.get("owner"),
            meta.get("subsystem"),
            meta.get("role"),
            meta.get("layer"),
            meta.get("status"),
            meta.get("audience"),
            meta.get("visibility"),
            meta.get("lifecycle"),
            meta.get("authority"),
            meta.get("canonical_location"),
            meta.get("top_level_root"),
        )

        entries[path] = {
            "path": path,
            "owner": meta.get("owner"),
            "subsystem": meta.get("subsystem"),
            "role": meta.get("role"),
            "layer": meta.get("layer"),
            "status": meta.get("status"),
            "audience": meta.get("audience"),
            "visibility": meta.get("visibility"),
            "lifecycle": meta.get("lifecycle"),
            "authority": meta.get("authority"),
            "top_level_root": meta.get("top_level_root"),
            "canonical_location": meta.get("canonical_location"),
            "public_api_candidate": meta.get("public_api_candidate"),
            "inbound_dependency_count": len(set(inbound_dependencies.get(path, []))),
            "outbound_dependency_count": len(set(outbound_dependencies.get(path, []))),
            "inbound_dependencies": sorted(set(inbound_dependencies.get(path, []))),
            "outbound_dependencies": sorted(set(outbound_dependencies.get(path, []))),
            "search_tokens": entry_tokens,
        }

        _add(by_owner, meta.get("owner"), path)
        _add(by_subsystem, meta.get("subsystem"), path)
        _add(by_audience, meta.get("audience"), path)
        _add(by_visibility, meta.get("visibility"), path)
        _add(by_lifecycle, meta.get("lifecycle"), path)
        _add(by_authority, meta.get("authority"), path)
        _add(by_root, meta.get("top_level_root"), path)
        _add(by_role, meta.get("role"), path)
        _add(by_status, meta.get("status"), path)
        _add(by_layer, meta.get("layer"), path)
        _add(by_canonical_location, meta.get("canonical_location"), path)

        for token in entry_tokens:
            _add(token_index, token, path)

    lookup_tables = {
        "by_owner": _sorted_unique_index(by_owner),
        "by_subsystem": _sorted_unique_index(by_subsystem),
        "by_audience": _sorted_unique_index(by_audience),
        "by_visibility": _sorted_unique_index(by_visibility),
        "by_lifecycle": _sorted_unique_index(by_lifecycle),
        "by_authority": _sorted_unique_index(by_authority),
        "by_root": _sorted_unique_index(by_root),
        "by_role": _sorted_unique_index(by_role),
        "by_status": _sorted_unique_index(by_status),
        "by_layer": _sorted_unique_index(by_layer),
        "by_canonical_location": _sorted_unique_index(by_canonical_location),
        "by_token": _sorted_unique_index(token_index),
    }

    return {
        "schema": SCHEMA,
        "phase": "17G",
        "feature": "UNIVERSAL_REPOSITORY_INDEX",
        "source_graph_schema": graph["schema"],
        "design_principle": "The repository ownership graph is the source of truth; the universal index is a searchable access layer, not a second scanner.",
        "summary": {
            "indexed_files": len(entries),
            "lookup_tables": len(lookup_tables),
            "owners_indexed": len(lookup_tables["by_owner"]),
            "subsystems_indexed": len(lookup_tables["by_subsystem"]),
            "audiences_indexed": len(lookup_tables["by_audience"]),
            "roots_indexed": len(lookup_tables["by_root"]),
            "tokens_indexed": len(lookup_tables["by_token"]),
            "dependency_enabled": True,
            "user_resource_layer_enabled": "engineer_user" in lookup_tables["by_audience"],
            "developer_layer_enabled": "developer" in lookup_tables["by_audience"],
        },
        "entries": dict(sorted(entries.items())),
        "lookup_tables": lookup_tables,
        "resource_roots": graph.get("resource_roots", {}),
        "user_resource_ownership_layer": graph.get("user_resource_ownership_layer", {}),
    }


def search_index(index: dict[str, Any], query: str, *, limit: int = 50) -> list[dict[str, Any]]:
    tokens = _tokens(query)
    if not tokens:
        return []

    score: dict[str, int] = {}
    token_index = index.get("lookup_tables", {}).get("by_token", {})

    for token in tokens:
        for path in token_index.get(token, []):
            score[path] = score.get(path, 0) + 1

    ranked = sorted(score.items(), key=lambda item: (-item[1], item[0]))
    entries = index.get("entries", {})

    return [
        {
            "path": path,
            "score": value,
            "entry": entries[path],
        }
        for path, value in ranked[:limit]
        if path in entries
    ]


def write_universal_repository_index(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/phase_17g/universal_repository_index_phase_17g.json",
) -> dict[str, Any]:
    index = build_universal_repository_index(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return index


if __name__ == "__main__":
    index = write_universal_repository_index(".")
    summary = index["summary"]

    print("LEAF_UNIVERSAL_REPOSITORY_INDEX_PHASE_17G")
    print(f"schema={index['schema']}")
    print(f"indexed_files={summary['indexed_files']}")
    print(f"lookup_tables={summary['lookup_tables']}")
    print(f"owners_indexed={summary['owners_indexed']}")
    print(f"subsystems_indexed={summary['subsystems_indexed']}")
    print(f"audiences_indexed={summary['audiences_indexed']}")
    print(f"roots_indexed={summary['roots_indexed']}")
    print(f"tokens_indexed={summary['tokens_indexed']}")
