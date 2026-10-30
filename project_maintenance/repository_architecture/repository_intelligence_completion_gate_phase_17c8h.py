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
    RepositoryIntelligenceAPI,
    build_repository_intelligence_snapshot,
)
from project_maintenance.repository_architecture.repository_architecture_visualisation import (
    build_architecture_visualisation,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c8h"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_MODULES = [
    "leaf_qt/core/architecture/repository_metadata.py",
    "project_maintenance/repository_architecture/repository_knowledge_database.py",
    "project_maintenance/repository_architecture/repository_dependency_ownership_graph.py",
    "project_maintenance/repository_architecture/repository_architecture_validator.py",
    "project_maintenance/repository_architecture/repository_semantic_classification_engine.py",
    "project_maintenance/repository_architecture/repository_intelligence_api.py",
    "project_maintenance/repository_architecture/repository_architecture_visualisation.py",
]

EXPECTED_SCHEMAS = {
    "metadata_schema": "LEAF_REPOSITORY_METADATA_V1",
    "database_schema": "LEAF_REPOSITORY_KNOWLEDGE_DATABASE_V1",
    "graph_schema": "LEAF_REPOSITORY_DEPENDENCY_OWNERSHIP_GRAPH_V1",
    "validation_schema": "LEAF_REPOSITORY_ARCHITECTURE_VALIDATION_V1",
    "semantic_schema": "LEAF_REPOSITORY_SEMANTIC_CLASSIFICATION_ENGINE_V1",
}


def main() -> None:
    failures: list[str] = []
    compile_results: dict[str, str] = {}

    for rel in REQUIRED_MODULES:
        path = ROOT / rel
        if not path.exists():
            failures.append(f"missing_required_module={rel}")
            compile_results[rel] = "MISSING"
            continue

        try:
            py_compile.compile(str(path), doraise=True)
            compile_results[rel] = "PASS"
        except Exception as exc:
            failures.append(f"compile_failure={rel}:{exc!r}")
            compile_results[rel] = "FAIL"

    api = RepositoryIntelligenceAPI(ROOT)
    snapshot = build_repository_intelligence_snapshot(ROOT)
    visualisation = build_architecture_visualisation(ROOT)

    summary = snapshot["summary"]

    if snapshot["schema"] != "LEAF_REPOSITORY_INTELLIGENCE_API_V1":
        failures.append("repository_intelligence_api_schema_invalid")

    for key, expected in EXPECTED_SCHEMAS.items():
        if snapshot.get(key) != expected:
            failures.append(f"{key}_invalid")

    if visualisation["schema"] != "LEAF_REPOSITORY_ARCHITECTURE_VISUALISATION_V1":
        failures.append("visualisation_schema_invalid")

    if summary["supported_files"] <= 0:
        failures.append("no_supported_files")

    if summary["python_files"] <= 0:
        failures.append("no_python_files")

    if summary["file_nodes"] <= 0:
        failures.append("no_file_nodes")

    if summary["owner_nodes"] <= 0:
        failures.append("no_owner_nodes")

    if summary["subsystem_nodes"] <= 0:
        failures.append("no_subsystem_nodes")

    if summary["resolved_dependency_edges"] <= 0:
        failures.append("no_resolved_dependency_edges")

    if summary["architecture_errors"] != 0:
        failures.append("architecture_errors_present")

    if summary["semantic_enriched_files"] <= 0:
        failures.append("semantic_enrichment_missing")

    runtime_files = api.files_by_layer("runtime")
    development_files = api.files_by_layer("development")
    warnings = api.architecture_warnings()

    if not runtime_files:
        failures.append("runtime_query_empty")

    if not development_files:
        failures.append("development_query_empty")

    self_explanation = api.explain_file(
        "project_maintenance/repository_architecture/repository_intelligence_completion_gate_phase_17c8h.py"
    )

    if not self_explanation.get("found"):
        failures.append("completion_gate_self_explanation_missing")

    result = {
        "phase": "17C.8H",
        "feature": "REPOSITORY_INTELLIGENCE_COMPLETION_GATE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "compile_results": compile_results,
        "snapshot": snapshot,
        "visualisation_schema": visualisation["schema"],
        "runtime_query_count": len(runtime_files),
        "development_query_count": len(development_files),
        "architecture_warning_count": len(warnings),
        "self_explanation_found": self_explanation.get("found"),
        "failures": failures,
        "completion_notice": (
            "PHASE_17C8H_COMPLETE_REPOSITORY_INTELLIGENCE_FOUNDATION_CERTIFIED"
            if not failures
            else "PHASE_17C8H_BLOCKED"
        ),
        "next_phase": "17C.9A_UNIVERSAL_SORTER_INTEGRATION_WITH_REPOSITORY_INTELLIGENCE",
    }

    gate_json = OUT_DIR / "repository_intelligence_completion_gate_phase_17c8h.json"
    gate_txt = OUT_DIR / "repository_intelligence_completion_gate_phase_17c8h.txt"
    self_json = OUT_DIR / "repository_intelligence_completion_gate_self_explanation.json"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    self_json.write_text(json.dumps(self_explanation, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.8H REPOSITORY INTELLIGENCE COMPLETION GATE",
            "===========================================================",
            f"passed={result['passed']}",
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
            f"required_modules={len(REQUIRED_MODULES)}",
            f"compile_passes={sum(1 for v in compile_results.values() if v == 'PASS')}",
            f"compile_failures={sum(1 for v in compile_results.values() if v == 'FAIL')}",
            f"missing_modules={sum(1 for v in compile_results.values() if v == 'MISSING')}",
            f"self_explanation_found={result['self_explanation_found']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={gate_json.relative_to(ROOT)}",
            f"self_explanation_json={self_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C8H_REPOSITORY_INTELLIGENCE_COMPLETION_GATE" if result["passed"] else "FAIL_PHASE_17C8H_REPOSITORY_INTELLIGENCE_COMPLETION_GATE")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"resolved_dependency_edges={summary['resolved_dependency_edges']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"semantic_enriched_files={summary['semantic_enriched_files']}")
    print(f"runtime_query_count={result['runtime_query_count']}")
    print(f"development_query_count={result['development_query_count']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
