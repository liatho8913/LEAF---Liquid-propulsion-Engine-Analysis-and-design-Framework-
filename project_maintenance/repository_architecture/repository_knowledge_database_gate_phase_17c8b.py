from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_knowledge_database import (
    SCHEMA,
    RepositoryKnowledgeQuery,
    build_repository_knowledge_database,
    query_database,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c8b"
OUT_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_MODULE = ROOT / "project_maintenance" / "repository_architecture" / "repository_knowledge_database.py"


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(DATABASE_MODULE), doraise=True)
    except Exception as exc:
        failures.append(f"repository_knowledge_database_compile_failure={exc!r}")

    database = build_repository_knowledge_database(ROOT)

    if database["schema"] != SCHEMA:
        failures.append("database_schema_invalid")

    if database["metadata_schema"] != "LEAF_REPOSITORY_METADATA_V1":
        failures.append("metadata_schema_invalid")

    if len(database["files"]) <= 0:
        failures.append("no_files_in_database")

    if len(database["files"]) != database["summary"]["supported_files"]:
        failures.append("file_count_does_not_match_metadata_summary")

    required_indexes = [
        "by_layer",
        "by_subsystem",
        "by_role",
        "by_status",
        "by_import",
        "by_class",
        "by_function",
    ]

    for index_name in required_indexes:
        if index_name not in database["indexes"]:
            failures.append(f"missing_index={index_name}")

    if "runtime" not in database["indexes"]["by_layer"]:
        failures.append("runtime_index_missing")

    if "development" not in database["indexes"]["by_layer"]:
        failures.append("development_index_missing")

    runtime_results = query_database(database, RepositoryKnowledgeQuery(layer="runtime"))
    development_results = query_database(database, RepositoryKnowledgeQuery(layer="development"))

    if not runtime_results:
        failures.append("runtime_query_returned_empty")

    if not development_results:
        failures.append("development_query_returned_empty")

    db_path = OUT_DIR / "repository_knowledge_database_v1.json"
    gate_json = OUT_DIR / "repository_knowledge_database_gate_phase_17c8b.json"
    gate_txt = OUT_DIR / "repository_knowledge_database_gate_phase_17c8b.txt"

    db_path.write_text(json.dumps(database, indent=2), encoding="utf-8")

    result = {
        "phase": "17C.8B",
        "feature": "REPOSITORY_KNOWLEDGE_DATABASE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": database["schema"],
        "metadata_schema": database["metadata_schema"],
        "file_count": len(database["files"]),
        "index_counts": {
            name: len(index)
            for name, index in database["indexes"].items()
        },
        "runtime_query_count": len(runtime_results),
        "development_query_count": len(development_results),
        "failures": failures,
        "database_json": db_path.relative_to(ROOT).as_posix(),
        "completion_notice": (
            "PHASE_17C8B_COMPLETE_REPOSITORY_KNOWLEDGE_DATABASE_ESTABLISHED"
            if not failures
            else "PHASE_17C8B_BLOCKED"
        ),
        "next_phase": "17C.8C_DEPENDENCY_AND_OWNERSHIP_GRAPH",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.8B REPOSITORY KNOWLEDGE DATABASE",
            "================================================",
            f"passed={result['passed']}",
            f"schema={result['schema']}",
            f"metadata_schema={result['metadata_schema']}",
            f"file_count={result['file_count']}",
            f"runtime_query_count={result['runtime_query_count']}",
            f"development_query_count={result['development_query_count']}",
            f"by_layer_indexes={result['index_counts'].get('by_layer', 0)}",
            f"by_subsystem_indexes={result['index_counts'].get('by_subsystem', 0)}",
            f"by_role_indexes={result['index_counts'].get('by_role', 0)}",
            f"by_import_indexes={result['index_counts'].get('by_import', 0)}",
            f"by_class_indexes={result['index_counts'].get('by_class', 0)}",
            f"by_function_indexes={result['index_counts'].get('by_function', 0)}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"database_json={db_path.relative_to(ROOT)}",
            f"gate_json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C8B_REPOSITORY_KNOWLEDGE_DATABASE" if result["passed"] else "FAIL_PHASE_17C8B_REPOSITORY_KNOWLEDGE_DATABASE")
    print(f"schema={result['schema']}")
    print(f"metadata_schema={result['metadata_schema']}")
    print(f"file_count={result['file_count']}")
    print(f"runtime_query_count={result['runtime_query_count']}")
    print(f"development_query_count={result['development_query_count']}")
    print(f"database_json={db_path.relative_to(ROOT)}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
