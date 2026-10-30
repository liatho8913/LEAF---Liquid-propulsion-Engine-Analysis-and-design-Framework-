from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.roadmap_status_artifact_owner import RoadmapStatusArtifactOwner
from project_maintenance.repository_architecture.universal_repository_index_phase_17g import (
    SCHEMA,
    build_universal_repository_index,
    search_index,
)

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17g"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "repository_architecture" / "repository_ownership_graph_phase_17f.py",
    ROOT / "project_maintenance" / "repository_architecture" / "universal_repository_index_phase_17g.py",
    ROOT / "project_maintenance" / "repository_architecture" / "universal_repository_index_gate_phase_17g.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    try:
        index = build_universal_repository_index(ROOT)
    except Exception as exc:
        index = {
            "schema": SCHEMA,
            "summary": {},
            "entries": {},
            "lookup_tables": {},
            "source_graph_schema": None,
        }
        failures.append(f"index_build_failure={exc!r}")

    summary = index.get("summary", {})
    lookup = index.get("lookup_tables", {})

    if index.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if index.get("source_graph_schema") != "LEAF_REPOSITORY_OWNERSHIP_GRAPH_PHASE_17F_V1":
        failures.append("source_graph_schema_invalid")

    if summary.get("indexed_files", 0) <= 0:
        failures.append("no_indexed_files")

    if summary.get("lookup_tables", 0) < 10:
        failures.append("lookup_table_count_too_low")

    for table in [
        "by_owner",
        "by_subsystem",
        "by_audience",
        "by_visibility",
        "by_lifecycle",
        "by_authority",
        "by_root",
        "by_role",
        "by_status",
        "by_layer",
        "by_canonical_location",
        "by_token",
    ]:
        if table not in lookup:
            failures.append(f"lookup_table_missing={table}")

    if "developer" not in lookup.get("by_audience", {}):
        failures.append("developer_audience_missing")

    if "engineer_user" not in lookup.get("by_audience", {}):
        failures.append("engineer_user_audience_missing")

    if "canonical" not in lookup.get("by_authority", {}):
        failures.append("canonical_authority_missing")

    if not summary.get("dependency_enabled"):
        failures.append("dependency_index_not_enabled")

    if not summary.get("developer_layer_enabled"):
        failures.append("developer_layer_not_enabled")

    if not summary.get("user_resource_layer_enabled"):
        failures.append("user_resource_layer_not_enabled")

    sample_searches = {
        "repository": search_index(index, "repository", limit=10),
        "owner": search_index(index, "owner", limit=10),
        "developer": search_index(index, "developer", limit=10),
        "designs": search_index(index, "designs", limit=10),
    }

    if not sample_searches["repository"]:
        failures.append("repository_search_empty")

    if not sample_searches["developer"]:
        failures.append("developer_search_empty")

    index_path = OUT / "universal_repository_index_phase_17g.json"
    gate_json = OUT / "universal_repository_index_gate_phase_17g.json"
    gate_txt = OUT / "universal_repository_index_gate_phase_17g.txt"

    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    roadmap_paths = {"json": "", "report": ""}

    if not failures:
        owner = RoadmapStatusArtifactOwner(ROOT)
        roadmap_status = owner.build_status(
            current_major_feature="Universal Repository Index",
            current_phase="17G",
            previous_completed_feature="17F Repository Ownership Graph",
            current_goal="Complete a searchable universal repository index built from the ownership graph without adding duplicate repository scanners.",
            completed=[
                "17A Repository Discovery",
                "17B Repository Classification",
                "17C Shared Snapshot Architecture",
                "17D Repository Intelligence Consolidation",
                "17E Repository Roadmap Visibility System",
                "17F Repository Ownership Graph",
                "17G Universal Repository Index",
            ],
            active_constraints=[
                "No automatic delete, archive, or relocation execution.",
                "The ownership graph remains the source of truth.",
                "The universal index is an access layer, not a duplicate scanner.",
                "Developer infrastructure and user-facing assets remain separate indexed domains.",
                "Frequently used user resources must remain discoverable through canonical root-level homes.",
            ],
            remaining_work=[
                "17H Repository Semantic Knowledge Graph",
                "17I Intelligent Repository Relocation",
                "17J Repository Health Monitor",
                "17K Repository Architecture Completion",
            ],
            next_phase="17H_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH",
            safety_locks={
                "move_allowed": False,
                "archive_allowed": False,
                "delete_allowed": False,
                "automatic_delete_allowed": False,
                "deletion_started": False,
            },
            metrics={
                "indexed_files": summary.get("indexed_files", 0),
                "lookup_tables": summary.get("lookup_tables", 0),
                "owners_indexed": summary.get("owners_indexed", 0),
                "subsystems_indexed": summary.get("subsystems_indexed", 0),
                "audiences_indexed": summary.get("audiences_indexed", 0),
                "roots_indexed": summary.get("roots_indexed", 0),
                "tokens_indexed": summary.get("tokens_indexed", 0),
            },
        )
        roadmap_paths = owner.write_status(roadmap_status)

    result = {
        "phase": "17G",
        "feature": "UNIVERSAL_REPOSITORY_INDEX",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": index.get("schema"),
        "source_graph_schema": index.get("source_graph_schema"),
        "summary": summary,
        "sample_searches": {
            key: [item["path"] for item in value]
            for key, value in sample_searches.items()
        },
        "failures": failures,
        "index_json": index_path.relative_to(ROOT).as_posix(),
        "roadmap_json": roadmap_paths["json"],
        "roadmap_report": roadmap_paths["report"],
        "completion_notice": "PHASE_17G_COMPLETE_UNIVERSAL_REPOSITORY_INDEX_ESTABLISHED" if not failures else "PHASE_17G_BLOCKED",
        "next_phase": "17H_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 17G UNIVERSAL REPOSITORY INDEX",
        "==========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_graph_schema={result['source_graph_schema']}",
        f"indexed_files={summary.get('indexed_files', 0)}",
        f"lookup_tables={summary.get('lookup_tables', 0)}",
        f"owners_indexed={summary.get('owners_indexed', 0)}",
        f"subsystems_indexed={summary.get('subsystems_indexed', 0)}",
        f"audiences_indexed={summary.get('audiences_indexed', 0)}",
        f"roots_indexed={summary.get('roots_indexed', 0)}",
        f"tokens_indexed={summary.get('tokens_indexed', 0)}",
        f"developer_layer_enabled={summary.get('developer_layer_enabled')}",
        f"user_resource_layer_enabled={summary.get('user_resource_layer_enabled')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"index_json={result['index_json']}",
        f"roadmap_json={result['roadmap_json']}",
        f"roadmap_report={result['roadmap_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_17G_UNIVERSAL_REPOSITORY_INDEX" if result["passed"] else "FAIL_PHASE_17G_UNIVERSAL_REPOSITORY_INDEX")
    print(f"schema={result['schema']}")
    print(f"source_graph_schema={result['source_graph_schema']}")
    print(f"indexed_files={summary.get('indexed_files', 0)}")
    print(f"lookup_tables={summary.get('lookup_tables', 0)}")
    print(f"owners_indexed={summary.get('owners_indexed', 0)}")
    print(f"subsystems_indexed={summary.get('subsystems_indexed', 0)}")
    print(f"audiences_indexed={summary.get('audiences_indexed', 0)}")
    print(f"roots_indexed={summary.get('roots_indexed', 0)}")
    print(f"tokens_indexed={summary.get('tokens_indexed', 0)}")
    print(f"developer_layer_enabled={summary.get('developer_layer_enabled')}")
    print(f"user_resource_layer_enabled={summary.get('user_resource_layer_enabled')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"index_json={result['index_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"roadmap_report={result['roadmap_report']}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
