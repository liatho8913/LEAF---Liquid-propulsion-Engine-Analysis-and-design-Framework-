from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_dependency_ownership_graph import (
    SCHEMA,
    build_dependency_ownership_graph,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c8c"
OUT_DIR.mkdir(parents=True, exist_ok=True)

GRAPH_MODULE = ROOT / "project_maintenance" / "repository_architecture" / "repository_dependency_ownership_graph.py"


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(GRAPH_MODULE), doraise=True)
    except Exception as exc:
        failures.append(f"dependency_ownership_graph_compile_failure={exc!r}")

    graph = build_dependency_ownership_graph(ROOT)
    summary = graph["summary"]

    if graph["schema"] != SCHEMA:
        failures.append("graph_schema_invalid")

    if graph["database_schema"] != "LEAF_REPOSITORY_KNOWLEDGE_DATABASE_V1":
        failures.append("database_schema_invalid")

    if graph["metadata_schema"] != "LEAF_REPOSITORY_METADATA_V1":
        failures.append("metadata_schema_invalid")

    if summary["file_nodes"] <= 0:
        failures.append("no_file_nodes")

    if summary["owner_nodes"] <= 0:
        failures.append("no_owner_nodes")

    if summary["subsystem_nodes"] <= 0:
        failures.append("no_subsystem_nodes")

    if "runtime" not in graph["owners"] and "regen" not in graph["owners"]:
        failures.append("expected_runtime_or_regen_owner_missing")

    if summary["resolved_dependency_edges"] <= 0:
        failures.append("no_resolved_dependency_edges")

    graph_path = OUT_DIR / "repository_dependency_ownership_graph_v1.json"
    gate_json = OUT_DIR / "repository_dependency_ownership_graph_gate_phase_17c8c.json"
    gate_txt = OUT_DIR / "repository_dependency_ownership_graph_gate_phase_17c8c.txt"

    graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    result = {
        "phase": "17C.8C",
        "feature": "DEPENDENCY_AND_OWNERSHIP_GRAPH",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": graph["schema"],
        "database_schema": graph["database_schema"],
        "metadata_schema": graph["metadata_schema"],
        "summary": summary,
        "failures": failures,
        "graph_json": graph_path.relative_to(ROOT).as_posix(),
        "completion_notice": (
            "PHASE_17C8C_COMPLETE_DEPENDENCY_AND_OWNERSHIP_GRAPH_ESTABLISHED"
            if not failures
            else "PHASE_17C8C_BLOCKED"
        ),
        "next_phase": "17C.8D_ARCHITECTURE_VALIDATION_ENGINE",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.8C DEPENDENCY AND OWNERSHIP GRAPH",
            "===================================================",
            f"passed={result['passed']}",
            f"schema={result['schema']}",
            f"database_schema={result['database_schema']}",
            f"metadata_schema={result['metadata_schema']}",
            f"file_nodes={summary['file_nodes']}",
            f"owner_nodes={summary['owner_nodes']}",
            f"subsystem_nodes={summary['subsystem_nodes']}",
            f"resolved_dependency_edges={summary['resolved_dependency_edges']}",
            f"unresolved_or_external_import_edges={summary['unresolved_or_external_import_edges']}",
            f"subsystem_dependency_edges={summary['subsystem_dependency_edges']}",
            f"owner_dependency_edges={summary['owner_dependency_edges']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"graph_json={graph_path.relative_to(ROOT)}",
            f"gate_json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C8C_DEPENDENCY_AND_OWNERSHIP_GRAPH" if result["passed"] else "FAIL_PHASE_17C8C_DEPENDENCY_AND_OWNERSHIP_GRAPH")
    print(f"schema={result['schema']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"resolved_dependency_edges={summary['resolved_dependency_edges']}")
    print(f"unresolved_or_external_import_edges={summary['unresolved_or_external_import_edges']}")
    print(f"graph_json={graph_path.relative_to(ROOT)}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
