from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leaf_qt.core.architecture.repository_metadata import (
    build_repository_metadata,
)


SCHEMA = "LEAF_REPOSITORY_KNOWLEDGE_DATABASE_V1"


@dataclass(frozen=True)
class RepositoryKnowledgeQuery:
    layer: str | None = None
    subsystem: str | None = None
    role: str | None = None
    status: str | None = None
    public_api_candidate: bool | None = None


def build_indexes(files: list[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    indexes: dict[str, dict[str, list[str]]] = {
        "by_layer": {},
        "by_subsystem": {},
        "by_role": {},
        "by_status": {},
        "by_import": {},
        "by_class": {},
        "by_function": {},
    }

    for item in files:
        path = item["path"]

        for key, index_name in [
            ("layer", "by_layer"),
            ("subsystem", "by_subsystem"),
            ("role", "by_role"),
            ("status", "by_status"),
        ]:
            value = item.get(key) or "unknown"
            indexes[index_name].setdefault(value, []).append(path)

        for imported in item.get("imports", []):
            indexes["by_import"].setdefault(imported, []).append(path)

        for class_name in item.get("classes", []):
            indexes["by_class"].setdefault(class_name, []).append(path)

        for function_name in item.get("functions", []):
            indexes["by_function"].setdefault(function_name, []).append(path)

    for index in indexes.values():
        for key in list(index):
            index[key] = sorted(set(index[key]))

    return indexes


def build_file_lookup(files: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["path"]: item for item in files}


def build_repository_knowledge_database(root: str | Path = ".") -> dict[str, Any]:
    metadata = build_repository_metadata(root)
    files = metadata["files"]

    return {
        "schema": SCHEMA,
        "metadata_schema": metadata["schema"],
        "root": metadata["root"],
        "summary": metadata["summary"],
        "indexes": build_indexes(files),
        "files": build_file_lookup(files),
    }


def write_repository_knowledge_database(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/repository_knowledge_database_v1.json",
) -> dict[str, Any]:
    database = build_repository_knowledge_database(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(database, indent=2), encoding="utf-8")
    return database


def query_database(database: dict[str, Any], query: RepositoryKnowledgeQuery) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for item in database["files"].values():
        if query.layer is not None and item.get("layer") != query.layer:
            continue
        if query.subsystem is not None and item.get("subsystem") != query.subsystem:
            continue
        if query.role is not None and item.get("role") != query.role:
            continue
        if query.status is not None and item.get("status") != query.status:
            continue
        if query.public_api_candidate is not None and item.get("public_api_candidate") != query.public_api_candidate:
            continue
        results.append(item)

    return sorted(results, key=lambda item: item["path"])


if __name__ == "__main__":
    db = write_repository_knowledge_database(".")
    print("LEAF_REPOSITORY_KNOWLEDGE_DATABASE")
    print(f"schema={db['schema']}")
    print(f"metadata_schema={db['metadata_schema']}")
    print(f"files={len(db['files'])}")
    print(f"layers={len(db['indexes']['by_layer'])}")
    print(f"subsystems={len(db['indexes']['by_subsystem'])}")
    print(f"roles={len(db['indexes']['by_role'])}")
    print(f"imports={len(db['indexes']['by_import'])}")
    print(f"classes={len(db['indexes']['by_class'])}")
    print(f"functions={len(db['indexes']['by_function'])}")
