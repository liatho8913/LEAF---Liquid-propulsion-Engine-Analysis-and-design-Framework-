from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_intelligence_api import (
    SCHEMA,
    RepositoryIntelligenceAPI,
    build_repository_intelligence_snapshot,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c8f"
OUT_DIR.mkdir(parents=True, exist_ok=True)

API_MODULE = ROOT / "project_maintenance" / "repository_architecture" / "repository_intelligence_api.py"


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(API_MODULE), doraise=True)
    except Exception as exc:
        failures.append(f"repository_intelligence_api_compile_failure={exc!r}")

    api = RepositoryIntelligenceAPI(ROOT)
    snapshot = build_repository_intelligence_snapshot(ROOT)
    summary = snapshot["summary"]

    if snapshot["schema"] != SCHEMA:
        failures.append("api_schema_invalid")

    required_schemas = {
        "metadata_schema": "LEAF_REPOSITORY_METADATA_V1",
        "database_schema": "LEAF_REPOSITORY_KNOWLEDGE_DATABASE_V1",
        "graph_schema": "LEAF_REPOSITORY_DEPENDENCY_OWNERSHIP_GRAPH_V1",
        "validation_schema": "LEAF_REPOSITORY_ARCHITECTURE_VALIDATION_V1",
        "semantic_schema": "LEAF_REPOSITORY_SEMANTIC_CLASSIFICATION_ENGINE_V1",
    }

    for key, expected in required_schemas.items():
        if snapshot.get(key) != expected:
            failures.append(f"{key}_invalid")

    if summary["supported_files"] <= 0:
        failures.append("no_supported_files")

    if summary["file_nodes"] <= 0:
        failures.append("no_file_nodes")

    if summary["owner_nodes"] <= 0:
        failures.append("no_owner_nodes")

    if summary["subsystem_nodes"] <= 0:
        failures.append("no_subsystem_nodes")

    if summary["architecture_errors"] != 0:
        failures.append("architecture_errors_present")

    runtime_files = api.files_by_layer("runtime")
    development_files = api.files_by_layer("development")

    if not runtime_files:
        failures.append("api_runtime_query_empty")

    if not development_files:
        failures.append("api_development_query_empty")

    explanation = api.explain_file("project_maintenance/repository_architecture/repository_intelligence_api.py")

    if not explanation.get("found"):
        failures.append("api_explain_file_failed")

    snapshot_path = OUT_DIR / "repository_intelligence_api_snapshot_v1.json"
    explanation_path = OUT_DIR / "repository_intelligence_api_self_explanation_v1.json"
    gate_json = OUT_DIR / "repository_intelligence_api_gate_phase_17c8f.json"
    gate_txt = OUT_DIR / "repository_intelligence_api_gate_phase_17c8f.txt"

    snapshot_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    explanation_path.write_text(json.dumps(explanation, indent=2), encoding="utf-8")

    result = {
        "phase": "17C.8F",
        "feature": "REPOSITORY_INTELLIGENCE_API",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": snapshot["schema"],
        "summary": summary,
        "runtime_query_count": len(runtime_files),
        "development_query_count": len(development_files),
        "self_explanation_found": explanation.get("found"),
        "failures": failures,
        "snapshot_json": snapshot_path.relative_to(ROOT).as_posix(),
        "self_explanation_json": explanation_path.relative_to(ROOT).as_posix(),
        "completion_notice": (
            "PHASE_17C8F_COMPLETE_REPOSITORY_INTELLIGENCE_API_ESTABLISHED"
            if not failures
            else "PHASE_17C8F_BLOCKED"
        ),
        "next_phase": "17C.8G_ARCHITECTURE_VISUALISATION_FOUNDATION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.8F REPOSITORY INTELLIGENCE API",
            "================================================",
            f"passed={result['passed']}",
            f"schema={result['schema']}",
            f"supported_files={summary['supported_files']}",
            f"python_files={summary['python_files']}",
            f"file_nodes={summary['file_nodes']}",
            f"owner_nodes={summary['owner_nodes']}",
            f"subsystem_nodes={summary['subsystem_nodes']}",
            f"resolved_dependency_edges={summary['resolved_dependency_edges']}",
            f"architecture_errors={summary['architecture_errors']}",
            f"architecture_warnings={summary['architecture_warnings']}",
            f"semantic_enriched_files={summary['semantic_enriched_files']}",
            f"runtime_query_count={result['runtime_query_count']}",
            f"development_query_count={result['development_query_count']}",
            f"self_explanation_found={result['self_explanation_found']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"snapshot_json={snapshot_path.relative_to(ROOT)}",
            f"self_explanation_json={explanation_path.relative_to(ROOT)}",
            f"gate_json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C8F_REPOSITORY_INTELLIGENCE_API" if result["passed"] else "FAIL_PHASE_17C8F_REPOSITORY_INTELLIGENCE_API")
    print(f"schema={result['schema']}")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"semantic_enriched_files={summary['semantic_enriched_files']}")
    print(f"runtime_query_count={result['runtime_query_count']}")
    print(f"development_query_count={result['development_query_count']}")
    print(f"snapshot_json={snapshot_path.relative_to(ROOT)}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
