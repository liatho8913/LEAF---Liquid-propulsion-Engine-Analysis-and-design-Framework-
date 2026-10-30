from __future__ import annotations

import json
import py_compile
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_health_monitor_phase_17j import (
    SCHEMA,
    build_repository_health_report,
)
from project_maintenance.repository_architecture.roadmap_status_artifact_owner import RoadmapStatusArtifactOwner

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17j"
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    ROOT / "project_maintenance" / "repository_architecture" / "intelligent_repository_relocation_phase_17i.py",
    ROOT / "project_maintenance" / "repository_architecture" / "repository_health_monitor_phase_17j.py",
    ROOT / "project_maintenance" / "repository_architecture" / "repository_health_monitor_gate_phase_17j.py",
]


def main() -> None:
    failures: list[str] = []

    for module in MODULES:
        try:
            py_compile.compile(str(module), doraise=True)
        except Exception as exc:
            failures.append(f"compile_failure:{module.relative_to(ROOT)}:{exc!r}")

    try:
        report = build_repository_health_report(ROOT)
    except Exception as exc:
        report = {
            "schema": SCHEMA,
            "source_relocation_schema": None,
            "summary": {},
            "categories": {},
            "safety_locks": {},
            "policy": {},
        }
        failures.append(f"health_report_build_failure={exc!r}")

    summary = report.get("summary", {})
    categories = report.get("categories", {})
    locks = report.get("safety_locks", {})
    policy = report.get("policy", {})

    if report.get("schema") != SCHEMA:
        failures.append("schema_invalid")

    if report.get("source_relocation_schema") != "LEAF_INTELLIGENT_REPOSITORY_RELOCATION_PHASE_17I_V1":
        failures.append("source_relocation_schema_invalid")

    if summary.get("file_nodes_considered", 0) <= 0:
        failures.append("no_file_nodes_considered")

    if summary.get("read_only_monitor") is not True:
        failures.append("read_only_monitor_not_true")

    if summary.get("execution_allowed") is not False:
        failures.append("execution_allowed_not_false")

    if summary.get("overall_score", 0) <= 0:
        failures.append("overall_score_invalid")

    if summary.get("overall_status") not in {"PASS", "PASS_WITH_REVIEW_ITEMS", "REVIEW_REQUIRED"}:
        failures.append("overall_status_invalid_or_failed")

    required_categories = [
        "safety",
        "dry_run_integrity",
        "policy_integrity",
        "user_architecture_health",
        "developer_architecture_health",
        "relocation_pressure",
        "migration_pressure",
        "manual_review_burden",
    ]

    for category in required_categories:
        if category not in categories:
            failures.append(f"category_missing={category}")
            continue
        if not isinstance(categories[category].get("score"), (int, float)):
            failures.append(f"category_score_missing={category}")

    for key in [
        "health_monitor_execution_allowed",
        "health_monitor_move_allowed",
        "health_monitor_delete_allowed",
        "health_monitor_archive_allowed",
    ]:
        if locks.get(key) is not False:
            failures.append(f"health_monitor_lock_not_false={key}")

    for key in [
        "read_only_health_monitor",
        "health_scores_are_advisory",
        "review_items_are_not_execution_commands",
        "developer_architecture_and_user_architecture_are_scored_separately",
        "repository_health_must_include_navigation_and_cognitive_load",
    ]:
        if policy.get(key) is not True:
            failures.append(f"policy_missing={key}")

    if categories.get("safety", {}).get("status") != "PASS":
        failures.append("safety_category_not_pass")

    if categories.get("dry_run_integrity", {}).get("status") != "PASS":
        failures.append("dry_run_integrity_not_pass")

    report_path = OUT / "repository_health_report_phase_17j.json"
    gate_json = OUT / "repository_health_monitor_gate_phase_17j.json"
    gate_txt = OUT / "repository_health_monitor_gate_phase_17j.txt"

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    roadmap_paths = {"json": "", "report": ""}

    if not failures:
        owner = RoadmapStatusArtifactOwner(ROOT)
        roadmap_status = owner.build_status(
            current_major_feature="Repository Health Monitor",
            current_phase="17J",
            previous_completed_feature="17I Intelligent Repository Relocation",
            current_goal="Complete a read-only repository health monitor that scores safety, relocation pressure, policy integrity, and user/developer architecture health.",
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
                "17J Repository Health Monitor",
            ],
            active_constraints=[
                "No automatic delete, archive, or relocation execution.",
                "17J is read-only monitoring only.",
                "Health scores are advisory and do not authorise repository operations.",
                "Developer-facing and user-facing architecture health must be scored separately.",
                "Repository health includes navigation clarity and cognitive load, not only code organisation.",
            ],
            remaining_work=[
                "17K Repository Architecture Completion",
            ],
            next_phase="17K_REPOSITORY_ARCHITECTURE_COMPLETION",
            safety_locks={
                "move_allowed": False,
                "archive_allowed": False,
                "delete_allowed": False,
                "automatic_delete_allowed": False,
                "automatic_relocation_allowed": False,
                "health_monitor_execution_allowed": False,
                "deletion_started": False,
            },
            metrics={
                "overall_score": summary.get("overall_score", 0),
                "overall_status": summary.get("overall_status", "UNKNOWN"),
                "recommendations": summary.get("recommendations", 0),
                "manual_review_required": summary.get("manual_review_required", 0),
                "developer_infrastructure_candidates": summary.get("developer_infrastructure_candidates", 0),
                "user_resource_candidates": summary.get("user_resource_candidates", 0),
                "migration_source_review_candidates": summary.get("migration_source_review_candidates", 0),
            },
        )
        roadmap_paths = owner.write_status(roadmap_status)

    result = {
        "phase": "17J",
        "feature": "REPOSITORY_HEALTH_MONITOR",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": report.get("schema"),
        "source_relocation_schema": report.get("source_relocation_schema"),
        "summary": summary,
        "categories": categories,
        "failures": failures,
        "health_report_json": report_path.relative_to(ROOT).as_posix(),
        "roadmap_json": roadmap_paths["json"],
        "roadmap_report": roadmap_paths["report"],
        "completion_notice": "PHASE_17J_COMPLETE_REPOSITORY_HEALTH_MONITOR_ESTABLISHED" if not failures else "PHASE_17J_BLOCKED",
        "next_phase": "17K_REPOSITORY_ARCHITECTURE_COMPLETION",
    }

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text("\n".join([
        "LEAF PHASE 17J REPOSITORY HEALTH MONITOR",
        "==========================================",
        f"passed={result['passed']}",
        f"schema={result['schema']}",
        f"source_relocation_schema={result['source_relocation_schema']}",
        f"overall_score={summary.get('overall_score')}",
        f"overall_status={summary.get('overall_status')}",
        f"file_nodes_considered={summary.get('file_nodes_considered', 0)}",
        f"recommendations={summary.get('recommendations', 0)}",
        f"manual_review_required={summary.get('manual_review_required', 0)}",
        f"developer_infrastructure_candidates={summary.get('developer_infrastructure_candidates', 0)}",
        f"user_resource_candidates={summary.get('user_resource_candidates', 0)}",
        f"migration_source_review_candidates={summary.get('migration_source_review_candidates', 0)}",
        f"read_only_monitor={summary.get('read_only_monitor')}",
        f"execution_allowed={summary.get('execution_allowed')}",
        f"completion_notice={result['completion_notice']}",
        f"next_phase={result['next_phase']}",
        f"health_report_json={result['health_report_json']}",
        f"roadmap_json={result['roadmap_json']}",
        f"roadmap_report={result['roadmap_report']}",
        f"gate_json={gate_json.relative_to(ROOT)}",
    ]), encoding="utf-8")

    print("PASS_PHASE_17J_REPOSITORY_HEALTH_MONITOR" if result["passed"] else "FAIL_PHASE_17J_REPOSITORY_HEALTH_MONITOR")
    print(f"schema={result['schema']}")
    print(f"source_relocation_schema={result['source_relocation_schema']}")
    print(f"overall_score={summary.get('overall_score')}")
    print(f"overall_status={summary.get('overall_status')}")
    print(f"file_nodes_considered={summary.get('file_nodes_considered', 0)}")
    print(f"recommendations={summary.get('recommendations', 0)}")
    print(f"manual_review_required={summary.get('manual_review_required', 0)}")
    print(f"developer_infrastructure_candidates={summary.get('developer_infrastructure_candidates', 0)}")
    print(f"user_resource_candidates={summary.get('user_resource_candidates', 0)}")
    print(f"migration_source_review_candidates={summary.get('migration_source_review_candidates', 0)}")
    print(f"read_only_monitor={summary.get('read_only_monitor')}")
    print(f"execution_allowed={summary.get('execution_allowed')}")
    print(f"completion_notice={result['completion_notice']}")
    print(f"health_report_json={result['health_report_json']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"roadmap_report={result['roadmap_report']}")
    print(f"next_phase={result['next_phase']}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
