from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from project_maintenance.repository_architecture.intelligent_repository_relocation_phase_17i import (
    build_intelligent_relocation_plan,
)

SCHEMA = "LEAF_REPOSITORY_HEALTH_MONITOR_PHASE_17J_V1"


def _score_from_penalty(start: int, penalty: int) -> int:
    return max(0, min(100, start - penalty))


def build_repository_health_report(root: str | Path = ".") -> dict[str, Any]:
    plan = build_intelligent_relocation_plan(root)
    summary = plan.get("summary", {})
    recommendations = plan.get("recommendations", [])
    locks = plan.get("safety_locks", {})
    policy = plan.get("policy", {})

    file_nodes = int(summary.get("file_nodes_considered", 0) or 0)
    recommendation_count = int(summary.get("recommendations", 0) or 0)
    manual_review_count = int(summary.get("manual_review_required", 0) or 0)
    developer_candidates = int(summary.get("developer_infrastructure_candidates", 0) or 0)
    user_candidates = int(summary.get("user_resource_candidates", 0) or 0)
    migration_candidates = int(summary.get("migration_source_review_candidates", 0) or 0)

    active_execution_flags = [
        key for key, value in locks.items()
        if value is not False
    ]

    missing_policy_flags = [
        key for key, value in policy.items()
        if value is not True
    ]

    dry_run_integrity_score = 100 if not active_execution_flags else 0
    safety_score = 100 if (
        summary.get("execution_allowed") is False
        and summary.get("move_operations_created") == 0
        and summary.get("delete_operations_created") == 0
        and summary.get("archive_operations_created") == 0
        and not active_execution_flags
    ) else 0

    relocation_pressure_penalty = min(45, recommendation_count * 5)
    relocation_pressure_score = _score_from_penalty(100, relocation_pressure_penalty)

    user_architecture_penalty = min(60, user_candidates * 15)
    user_architecture_score = _score_from_penalty(100, user_architecture_penalty)

    developer_architecture_penalty = min(50, developer_candidates * 4)
    developer_architecture_score = _score_from_penalty(100, developer_architecture_penalty)

    migration_pressure_penalty = min(50, migration_candidates * 5)
    migration_pressure_score = _score_from_penalty(100, migration_pressure_penalty)

    manual_review_penalty = min(35, manual_review_count * 3)
    review_burden_score = _score_from_penalty(100, manual_review_penalty)

    policy_score = 100 if not missing_policy_flags else _score_from_penalty(100, len(missing_policy_flags) * 20)

    categories = {
        "safety": {
            "score": safety_score,
            "status": "PASS" if safety_score == 100 else "FAIL",
            "meaning": "No execution, movement, deletion, or archive operation is allowed.",
        },
        "dry_run_integrity": {
            "score": dry_run_integrity_score,
            "status": "PASS" if dry_run_integrity_score == 100 else "FAIL",
            "meaning": "The relocation system remains recommendation-only.",
        },
        "policy_integrity": {
            "score": policy_score,
            "status": "PASS" if policy_score >= 90 else "REVIEW",
            "meaning": "Required architecture policies remain active.",
        },
        "user_architecture_health": {
            "score": user_architecture_score,
            "status": "PASS" if user_architecture_score >= 90 else "REVIEW",
            "meaning": "User-facing resources remain close to obvious canonical locations.",
        },
        "developer_architecture_health": {
            "score": developer_architecture_score,
            "status": "PASS" if developer_architecture_score >= 80 else "REVIEW",
            "meaning": "Developer-facing infrastructure remains close to expected developer roots.",
        },
        "relocation_pressure": {
            "score": relocation_pressure_score,
            "status": "PASS" if relocation_pressure_score >= 75 else "REVIEW",
            "meaning": "Measures how much cleanup or relocation pressure exists.",
        },
        "migration_pressure": {
            "score": migration_pressure_score,
            "status": "PASS" if migration_pressure_score >= 80 else "REVIEW",
            "meaning": "Measures pressure from non-authoritative migration, archive, quarantine, or artifact sources.",
        },
        "manual_review_burden": {
            "score": review_burden_score,
            "status": "PASS" if review_burden_score >= 75 else "REVIEW",
            "meaning": "Measures how many relocation candidates require human architectural review.",
        },
    }

    overall_score = round(sum(item["score"] for item in categories.values()) / len(categories), 3)

    if safety_score < 100 or dry_run_integrity_score < 100:
        overall_status = "FAIL"
    elif overall_score >= 90:
        overall_status = "PASS"
    elif overall_score >= 75:
        overall_status = "PASS_WITH_REVIEW_ITEMS"
    else:
        overall_status = "REVIEW_REQUIRED"

    top_review_items = sorted(
        recommendations,
        key=lambda item: (
            item.get("recommendation_type", ""),
            item.get("path", ""),
        ),
    )[:25]

    return {
        "schema": SCHEMA,
        "phase": "17J",
        "feature": "REPOSITORY_HEALTH_MONITOR",
        "source_relocation_schema": plan.get("schema"),
        "design_principle": "Health monitoring must be read-only and must measure architecture pressure without executing repository changes.",
        "summary": {
            "overall_score": overall_score,
            "overall_status": overall_status,
            "file_nodes_considered": file_nodes,
            "recommendations": recommendation_count,
            "manual_review_required": manual_review_count,
            "developer_infrastructure_candidates": developer_candidates,
            "user_resource_candidates": user_candidates,
            "migration_source_review_candidates": migration_candidates,
            "active_execution_flags": active_execution_flags,
            "missing_policy_flags": missing_policy_flags,
            "read_only_monitor": True,
            "execution_allowed": False,
        },
        "categories": categories,
        "top_review_items": top_review_items,
        "safety_locks": {
            **locks,
            "health_monitor_execution_allowed": False,
            "health_monitor_move_allowed": False,
            "health_monitor_delete_allowed": False,
            "health_monitor_archive_allowed": False,
        },
        "policy": {
            "read_only_health_monitor": True,
            "health_scores_are_advisory": True,
            "review_items_are_not_execution_commands": True,
            "developer_architecture_and_user_architecture_are_scored_separately": True,
            "repository_health_must_include_navigation_and_cognitive_load": True,
        },
    }


def write_repository_health_report(
    root: str | Path = ".",
    output_path: str | Path = "_leaf_artifacts/repository_architecture/phase_17j/repository_health_report_phase_17j.json",
) -> dict[str, Any]:
    report = build_repository_health_report(root)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    report = write_repository_health_report(".")
    summary = report["summary"]

    print("LEAF_REPOSITORY_HEALTH_MONITOR_PHASE_17J")
    print(f"schema={report['schema']}")
    print(f"source_relocation_schema={report['source_relocation_schema']}")
    print(f"overall_score={summary['overall_score']}")
    print(f"overall_status={summary['overall_status']}")
    print(f"recommendations={summary['recommendations']}")
    print(f"manual_review_required={summary['manual_review_required']}")
    print(f"read_only_monitor={summary['read_only_monitor']}")
    print(f"execution_allowed={summary['execution_allowed']}")
