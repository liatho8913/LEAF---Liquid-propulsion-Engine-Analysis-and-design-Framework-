from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.intelligent_repository_relocation_phase_17i import (
    SCHEMA,
    build_intelligent_relocation_plan,
)
from project_maintenance.repository_architecture.roadmap_status_artifact_owner import RoadmapStatusArtifactOwner

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17i"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "repository_architecture" / "repository_semantic_knowledge_graph_phase_17h.py",
    ROOT / "project_maintenance" / "repository_architecture" / "intelligent_repository_relocation_phase_17i.py",
    ROOT / "project_maintenance" / "repository_architecture" / "intelligent_repository_relocation_gate_phase_17i.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    try:
        plan = build_intelligent_relocation_plan(ROOT)
    except Exception as exc:
        plan = {
            "schema": SCHEMA,
            "source_semantic_graph_schema": None,
            "summary": {},
            "safety_locks": {},
            "recommendations": [],
            "policy": {},
        }
        failures.append(f"relocation_plan_build_failure={exc!r}")

    summary = plan.get("summary", {})
    locks = plan.get("safety_locks", {})
    policy = plan.get("policy", {})

    if plan.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if plan.get("source_semantic_graph_schema") != "LEAF_REPOSITORY_SEMANTIC_KNOWLEDGE_GRAPH_PHASE_17H_V1":
        failures.append("source_semantic_graph_schema_invalid")

    if summary.get("file_nodes_considered", 0) <= 0:
        failures.append("no_file_nodes_considered")

    if summary.get("execution_allowed") is not False:
        failures.append("execution_allowed_must_be_false")

    for key in [
        "move_allowed",
        "archive_allowed",
        "delete_allowed",
        "automatic_delete_allowed",
        "automatic_relocation_allowed",
        "deletion_started",
    ]:
        if locks.get(key) is not False:
            failures.append(f"safety_lock_not_false={key}")

    for key in [
        "developer_architecture_is_not_user_architecture",
        "one_authoritative_user_location",
        "quarantine_archive_and_artifact_locations_are_non_authoritative",
        "all_relocation_candidates_require_manual_review",
        "phase_17i_is_dry_run_only",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_missing={key}")

    if summary.get("move_operations_created") != 0:
        failures.append("move_operations_created_nonzero")

    if summary.get("delete_operations_created") != 0:
        failures.append("delete_operations_created_nonzero")

    if summary.get("archive_operations_created") != 0:
        failures.append("archive_operations_created_nonzero")

    for item in plan.get("recommendations", []):
        if item.get("execution_allowed") is not False:
            failures.append(f"recommendation_execution_allowed={item.get('path')}")
        if item.get("requires_manual_review") is not True:
            failures.append(f"recommendation_missing_manual_review={item.get('path')}")

    plan_path = OUT / "intelligent_repository_relocation_plan_phase_17i.json"
    gate_json = OUT / "intelligent_repository_relocation_gate_phase_17i.json"
    gate_txt = OUT / "intelligent_repository_relocation_gate_phase_17i.txt"

    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    roadmap_paths = {"json": "", "report": ""}

    if not failures:
        owner = RoadmapStatusArtifactOwner(ROOT)
        roadmap_status = owner.build_status(
            current_major_feature="Intelligent Repository Relocation",
            current_phase="17I",
            previous_completed_feature="17H Repository Semantic Knowledge Graph",
            current_goal="Complete dry-run relocation intelligence that identifies canonical homes and review candidates without executing file operations.",
            completed=[
                "17A Repository Discovery",
                "17B Repository Classification",
                "17C Shared Snapshot Architecture",
                "17D Repository Intelligence Consolidation",
                "17E Repository Roadmap Visibility System",
                "17F Repository Ownership Graph",
                "17G Universal Repository Index",
                "17H Repository Semantic Knowledge Graph",
                "17I Intelligent Repository Relocation",
            ],
            active_constraints=[
                "No automatic delete, archive, or relocation execution.",
                "17I may only create explainable dry-run recommendations.",
                "Every relocation candidate requires manual review.",
                "User-facing resources must have obvious canonical homes.",
                "Historical, quarantine, cleanup, and artifact locations are non-authoritative recovery or migration sources only.",
            ],
            remaining_work=[
                "17J Repository Health Monitor",
                "17K Repository Architecture Completion",
            ],
            next_phase="17J_REPOSITORY_HEALTH_MONITOR",
            safety_locks=locks,
            metrics={
                "file_nodes_considered": summary.get("file_nodes_considered", 0),
                "recommendations": summary.get("recommendations", 0),
                "manual_review_required": summary.get("manual_review_required", 0),
                "user_resource_candidates": summary.get("user_resource_candidates", 0),
                "developer_infrastructure_candidates": summary.get("developer_infrastructure_candidates", 0),
                "migration_source_review_candidates": summary.get("migration_source_review_candidates", 0),
            },
        )
        roadmap_paths = owner.write_status(roadmap_status)

    result = {
        "phase": "17I",
        "feature": "INTELLIGENT_REPOSITORY_RELOCATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": plan.get("schema"),
        "source_semantic_graph_schema": plan.get("source_semantic_graph_schema"),
        "summary": summary,
        "safety_locks": locks,
        "policy": policy,
        "failures": failures,
        "plan_json": plan_path.relative_to(ROOT).as_posix(),
        "roadmap_json": roadmap_paths["json"],
        "roadmap_report": roadmap_paths["report"],
        "completion_notice": "PHASE_17I_COMPLETE_INTELLIGENT_REPOSITORY_RELOCATION_DRY_RUN_ESTABLISHED" if not failures else "PHASE_17I_BLOCKED",
        "next_phase": "17J_REPOSITORY_HEALTH_MONITOR",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 17I INTELLIGENT REPOSITORY RELOCATION",
        "==================================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_semantic_graph_schema={result['source_semantic_graph_schema']}",
        f"file_nodes_considered={summary.get('file_nodes_considered', 0)}",
        f"recommendations={summary.get('recommendations', 0)}",
        f"manual_review_required={summary.get('manual_review_required', 0)}",
        f"user_resource_candidates={summary.get('user_resource_candidates', 0)}",
        f"developer_infrastructure_candidates={summary.get('developer_infrastructure_candidates', 0)}",
        f"migration_source_review_candidates={summary.get('migration_source_review_candidates', 0)}",
        f"execution_allowed={summary.get('execution_allowed')}",
        f"move_operations_created={summary.get('move_operations_created')}",
        f"delete_operations_created={summary.get('delete_operations_created')}",
        f"archive_operations_created={summary.get('archive_operations_created')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"plan_json={result['plan_json']}",
        f"roadmap_json={result['roadmap_json']}",
        f"roadmap_report={result['roadmap_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_17I_INTELLIGENT_REPOSITORY_RELOCATION" if result["passed"] else "FAIL_PHASE_17I_INTELLIGENT_REPOSITORY_RELOCATION")
    print(f"schema={result['schema']}")
    print(f"source_semantic_graph_schema={result['source_semantic_graph_schema']}")
    print(f"file_nodes_considered={summary.get('file_nodes_considered', 0)}")
    print(f"recommendations={summary.get('recommendations', 0)}")
    print(f"manual_review_required={summary.get('manual_review_required', 0)}")
    print(f"user_resource_candidates={summary.get('user_resource_candidates', 0)}")
    print(f"developer_infrastructure_candidates={summary.get('developer_infrastructure_candidates', 0)}")
    print(f"migration_source_review_candidates={summary.get('migration_source_review_candidates', 0)}")
    print(f"execution_allowed={summary.get('execution_allowed')}")
    print(f"move_operations_created={summary.get('move_operations_created')}")
    print(f"delete_operations_created={summary.get('delete_operations_created')}")
    print(f"archive_operations_created={summary.get('archive_operations_created')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"plan_json={result['plan_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"roadmap_report={result['roadmap_report']}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
