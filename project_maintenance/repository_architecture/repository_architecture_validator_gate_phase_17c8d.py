from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_architecture_validator import (
    SCHEMA,
    build_architecture_validation,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c8d"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VALIDATOR_MODULE = ROOT / "project_maintenance" / "repository_architecture" / "repository_architecture_validator.py"


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(VALIDATOR_MODULE), doraise=True)
    except Exception as exc:
        failures.append(f"repository_architecture_validator_compile_failure={exc!r}")

    validation = build_architecture_validation(ROOT)
    summary = validation["summary"]

    if validation["schema"] != SCHEMA:
        failures.append("validation_schema_invalid")

    if validation["graph_schema"] != "LEAF_REPOSITORY_DEPENDENCY_OWNERSHIP_GRAPH_V1":
        failures.append("graph_schema_invalid")

    if validation["database_schema"] != "LEAF_REPOSITORY_KNOWLEDGE_DATABASE_V1":
        failures.append("database_schema_invalid")

    if validation["metadata_schema"] != "LEAF_REPOSITORY_METADATA_V1":
        failures.append("metadata_schema_invalid")

    if summary["file_nodes"] <= 0:
        failures.append("no_file_nodes_validated")

    if summary["owner_nodes"] <= 0:
        failures.append("no_owner_nodes_validated")

    if summary["subsystem_nodes"] <= 0:
        failures.append("no_subsystem_nodes_validated")

    if summary["error_count"] != 0:
        failures.append("architecture_errors_present")

    validation_path = OUT_DIR / "repository_architecture_validation_v1.json"
    gate_json = OUT_DIR / "repository_architecture_validator_gate_phase_17c8d.json"
    gate_txt = OUT_DIR / "repository_architecture_validator_gate_phase_17c8d.txt"

    validation_path.write_text(json.dumps(validation, indent=2), encoding="utf-8")

    result = {
        "phase": "17C.8D",
        "feature": "ARCHITECTURE_VALIDATION_ENGINE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": validation["schema"],
        "graph_schema": validation["graph_schema"],
        "database_schema": validation["database_schema"],
        "metadata_schema": validation["metadata_schema"],
        "summary": summary,
        "failures": failures,
        "validation_json": validation_path.relative_to(ROOT).as_posix(),
        "completion_notice": (
            "PHASE_17C8D_COMPLETE_ARCHITECTURE_VALIDATION_ENGINE_ESTABLISHED"
            if not failures
            else "PHASE_17C8D_BLOCKED"
        ),
        "next_phase": "17C.8E_SEMANTIC_CLASSIFICATION_ENGINE",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.8D ARCHITECTURE VALIDATION ENGINE",
            "==================================================",
            f"passed={result['passed']}",
            f"schema={result['schema']}",
            f"graph_schema={result['graph_schema']}",
            f"database_schema={result['database_schema']}",
            f"metadata_schema={result['metadata_schema']}",
            f"file_nodes={summary['file_nodes']}",
            f"owner_nodes={summary['owner_nodes']}",
            f"subsystem_nodes={summary['subsystem_nodes']}",
            f"resolved_dependency_edges={summary['resolved_dependency_edges']}",
            f"errors={summary['error_count']}",
            f"warnings={summary['warning_count']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"validation_json={validation_path.relative_to(ROOT)}",
            f"gate_json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C8D_ARCHITECTURE_VALIDATION_ENGINE" if result["passed"] else "FAIL_PHASE_17C8D_ARCHITECTURE_VALIDATION_ENGINE")
    print(f"schema={result['schema']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"resolved_dependency_edges={summary['resolved_dependency_edges']}")
    print(f"errors={summary['error_count']}")
    print(f"warnings={summary['warning_count']}")
    print(f"validation_json={validation_path.relative_to(ROOT)}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
