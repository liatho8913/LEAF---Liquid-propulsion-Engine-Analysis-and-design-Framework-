from __future__ import annotations

from pathlib import Path
from typing import Any

from core.architecture.io import read_json_artifact, write_json_artifact, write_text_artifact


MANIFEST_PATH = Path("artifacts/repository_organisation_manifest.json")
OUT_JSON = Path("artifacts/repository_hotspot_audit.json")
OUT_TXT = Path("artifacts/repository_hotspot_audit.txt")


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing organisation manifest: {path}. "
            "Run python leaf_qt/repository_architecture_index.py and "
            "python leaf_qt/repository_organisation_manifest.py first."
        )
    return read_json_artifact(path)


def score_hotspot(item: dict[str, Any]) -> tuple[int, list[str], str]:
    score = 0
    reasons: list[str] = []

    line_count = int(item.get("line_count", 0))
    subsystem = item.get("subsystem", "UNCLASSIFIED")
    role = item.get("role", "MODULE_CODE")
    permanence = item.get("permanence", "REVIEW_REQUIRED")
    action = item.get("recommended_action", "REVIEW_REQUIRED")
    path = item.get("path", "")

    if line_count >= 10000:
        score += 60
        reasons.append("VERY_LARGE_FILE_10000_PLUS_LINES")
    elif line_count >= 3000:
        score += 45
        reasons.append("LARGE_FILE_3000_PLUS_LINES")
    elif line_count >= 1000:
        score += 30
        reasons.append("LARGE_FILE_1000_PLUS_LINES")
    elif line_count >= 500:
        score += 15
        reasons.append("MEDIUM_LARGE_FILE_500_PLUS_LINES")

    if subsystem == "UNCLASSIFIED":
        score += 35
        reasons.append("UNCLASSIFIED_SUBSYSTEM")

    if permanence in {"TEMPORARY_OR_MIGRATION_REVIEW", "LEGACY_OR_BACKUP_REVIEW"}:
        score += 30
        reasons.append(permanence)

    if action in {"ARCHIVE_REVIEW", "CLASSIFY_MANUALLY"}:
        score += 25
        reasons.append(action)

    if role in {"MASTER_GATE", "OWNER", "AUDIT_OWNER"} and line_count >= 500:
        score += 20
        reasons.append("OVERSIZED_CONTROL_OR_OWNERSHIP_FILE")

    if role == "TEST_CODE" and line_count >= 500:
        score += 10
        reasons.append("OVERSIZED_TEST_FILE")

    lowered = path.lower()
    if "phase_" in lowered:
        score += 15
        reasons.append("PHASE_NAMED_ARTIFACT")

    if "backup" in lowered or "legacy" in lowered:
        score += 20
        reasons.append("BACKUP_OR_LEGACY_PATH")

    if line_count >= 3000 and subsystem == "UNCLASSIFIED":
        priority = "CRITICAL"
    elif score >= 80:
        priority = "CRITICAL"
    elif score >= 50:
        priority = "HIGH"
    elif score >= 25:
        priority = "MEDIUM"
    elif score > 0:
        priority = "LOW"
    else:
        priority = "NORMAL"

    return score, reasons, priority


def recommended_next_action(item: dict[str, Any], priority: str, reasons: list[str]) -> str:
    subsystem = item.get("subsystem", "UNCLASSIFIED")
    role = item.get("role", "MODULE_CODE")
    line_count = int(item.get("line_count", 0))
    permanence = item.get("permanence", "")

    if "BACKUP_OR_LEGACY_PATH" in reasons:
        return "ARCHIVE_OR_REMOVE_AFTER_REGRESSION_CONFIRMATION"

    if subsystem == "UNCLASSIFIED":
        return "CLASSIFY_SUBSYSTEM_AND_ASSIGN_OWNER"

    if line_count >= 10000:
        return "SPLIT_INTO_STABLE_CONTRACTS_AND_SUBMODULES"

    if line_count >= 3000:
        return "EXTRACT_MAJOR_RESPONSIBILITIES"

    if permanence == "TEMPORARY_OR_MIGRATION_REVIEW":
        return "CONFIRM_IF_STILL_NEEDED_THEN_DELETE_OR_CONSOLIDATE"

    if role in {"MASTER_GATE", "OWNER", "AUDIT_OWNER"} and line_count >= 500:
        return "SEPARATE_POLICY_EVIDENCE_AND_REPORTING"

    if priority in {"CRITICAL", "HIGH"}:
        return "MANUAL_ARCHITECTURE_REVIEW"

    return "TRACK_ONLY"


def build_repository_hotspot_audit(manifest: dict[str, Any]) -> dict[str, Any]:
    hotspots: list[dict[str, Any]] = []

    for item in manifest.get("files", []):
        score, reasons, priority = score_hotspot(item)

        if score <= 0:
            continue

        hotspots.append(
            {
                "path": item.get("path"),
                "subsystem": item.get("subsystem"),
                "role": item.get("role"),
                "permanence": item.get("permanence"),
                "recommended_action_from_manifest": item.get("recommended_action"),
                "recommended_folder": item.get("recommended_folder"),
                "line_count": item.get("line_count", 0),
                "hotspot_score": score,
                "priority": priority,
                "reasons": reasons,
                "next_action": recommended_next_action(item, priority, reasons),
            }
        )

    hotspots.sort(
        key=lambda item: (
            item["hotspot_score"],
            item["line_count"],
            item["path"] or "",
        ),
        reverse=True,
    )

    priority_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    subsystem_counts: dict[str, int] = {}

    for item in hotspots:
        priority_counts[item["priority"]] = priority_counts.get(item["priority"], 0) + 1
        action_counts[item["next_action"]] = action_counts.get(item["next_action"], 0) + 1
        subsystem_counts[item["subsystem"]] = subsystem_counts.get(item["subsystem"], 0) + 1

    return {
        "schema": "LEAF_REPOSITORY_HOTSPOT_AUDIT_V1",
        "source_schema": manifest.get("schema"),
        "summary": {
            "hotspots": len(hotspots),
            "critical": priority_counts.get("CRITICAL", 0),
            "high": priority_counts.get("HIGH", 0),
            "medium": priority_counts.get("MEDIUM", 0),
            "low": priority_counts.get("LOW", 0),
            "priority_counts": dict(sorted(priority_counts.items())),
            "next_action_counts": dict(sorted(action_counts.items())),
            "subsystem_counts": dict(sorted(subsystem_counts.items())),
        },
        "top_hotspots": hotspots[:100],
        "hotspots": hotspots,
        "safe_to_modify_files": False,
        "note": (
            "This audit is advisory only. It ranks structural risk and does not "
            "edit, move, delete, or import runtime modules."
        ),
    }


def build_text_report(audit: dict[str, Any]) -> str:
    summary = audit["summary"]

    lines = [
        "LEAF REPOSITORY HOTSPOT AUDIT",
        "=============================",
        f"schema={audit['schema']}",
        f"safe_to_modify_files={audit['safe_to_modify_files']}",
        f"hotspots={summary['hotspots']}",
        f"critical={summary['critical']}",
        f"high={summary['high']}",
        f"medium={summary['medium']}",
        f"low={summary['low']}",
        "",
        "NEXT ACTION COUNTS",
        "------------------",
    ]

    for key, value in summary["next_action_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "TOP 25 HOTSPOTS", "---------------"])

    for item in audit["top_hotspots"][:25]:
        lines.append(
            f"{item['hotspot_score']:>3} | "
            f"{item['priority']:<8} | "
            f"{item['line_count']:>6} lines | "
            f"{item['subsystem']} | "
            f"{item['role']} | "
            f"{item['next_action']} | "
            f"{item['path']}"
        )

    return "\n".join(lines)


def write_repository_hotspot_audit() -> dict[str, Any]:
    manifest = load_manifest()
    audit = build_repository_hotspot_audit(manifest)

    write_json_artifact(audit, OUT_JSON)
    write_text_artifact(build_text_report(audit), OUT_TXT)

    return audit


if __name__ == "__main__":
    result = write_repository_hotspot_audit()
    print(build_text_report(result))
    print("")
    print(f"json={OUT_JSON}")
    print(f"txt={OUT_TXT}")
    print("PASS_REPOSITORY_HOTSPOT_AUDIT")
