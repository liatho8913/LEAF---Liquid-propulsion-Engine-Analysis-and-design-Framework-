from __future__ import annotations

from pathlib import Path
from typing import Any

from core.architecture.io import read_json_artifact, write_json_artifact, write_text_artifact


INDEX_PATH = Path("artifacts/repository_architecture_index.json")
OUT_JSON = Path("artifacts/repository_organisation_manifest.json")
OUT_TXT = Path("artifacts/repository_organisation_manifest.txt")


TARGET_FOLDERS = {
    "REGEN": "leaf_qt/modules/regen",
    "MATERIALS": "leaf_qt/modules/materials",
    "COATINGS": "leaf_qt/modules/coatings",
    "COOLANT": "leaf_qt/modules/coolant",
    "SOLVER": "leaf_qt/core/solvers",
    "REGISTRY": "leaf_qt/core/registry",
    "VALIDATION": "leaf_qt/core/validation",
    "REPORTING": "leaf_qt/core/reporting",
    "HISTORY": "leaf_qt/core/history",
    "BENCHMARKING": "leaf_qt/core/benchmarking",
    "OPTIMISATION": "leaf_qt/core/optimisation",
    "CANDIDATE_SELECTION": "leaf_qt/core/candidate_selection",
    "UI": "leaf_qt/ui",
    "UI_VIEWER": "leaf_qt/ui/viewers",
    "UI_GRAPHING": "leaf_qt/ui/graphing",
    "TESTS": "tests",
    "AUDIT": "project_maintenance/audits",
    "GATE": "project_maintenance/gates",
    "UNCLASSIFIED": "project_maintenance/review_required",
}


TEMPORARY_ROLE_HINTS = {
    "PHASE_ARTIFACT",
    "BACKUP_OR_LEGACY",
}

PERMANENT_ROLE_HINTS = {
    "MODULE_CODE",
    "SOLVER",
    "REGISTRY",
    "VALIDATION_OWNER",
    "REPORT_OWNER",
    "OWNER",
    "CONTROLLER",
    "DATABASE",
    "UI_PANEL",
    "UI_WINDOW",
    "UI_VIEWER",
}


def load_index(path: Path = INDEX_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing architecture index: {path}. "
            "Run python leaf_qt/repository_architecture_index.py first."
        )
    return read_json_artifact(path)


def classify_file(entry: dict[str, Any]) -> dict[str, Any]:
    path = entry["path"]
    subsystem = entry["subsystem"]
    role = entry["role"]
    target_folder = TARGET_FOLDERS.get(subsystem, TARGET_FOLDERS["UNCLASSIFIED"])

    lowered = path.lower()

    if role in TEMPORARY_ROLE_HINTS or "phase_" in lowered:
        permanence = "TEMPORARY_OR_MIGRATION_REVIEW"
    elif role in PERMANENT_ROLE_HINTS:
        permanence = "PERMANENT_REVIEW"
    elif role == "TEST_CODE":
        permanence = "TEST_INFRASTRUCTURE"
    elif role in {"AUDIT_OWNER", "MASTER_GATE"}:
        permanence = "MAINTENANCE_INFRASTRUCTURE"
    else:
        permanence = "REVIEW_REQUIRED"

    if subsystem == "UNCLASSIFIED":
        action = "CLASSIFY_MANUALLY"
    elif path.startswith(target_folder + "/"):
        action = "KEEP"
    else:
        action = "PROPOSE_MOVE"

    if "backup" in lowered or "legacy" in lowered:
        action = "ARCHIVE_REVIEW"
        permanence = "LEGACY_OR_BACKUP_REVIEW"

    return {
        "path": path,
        "subsystem": subsystem,
        "role": role,
        "permanence": permanence,
        "recommended_action": action,
        "recommended_folder": target_folder,
        "line_count": entry.get("line_count", 0),
        "classes": entry.get("classes", []),
        "functions": entry.get("functions", []),
        "imports": entry.get("imports", []),
        "from_imports": entry.get("from_imports", []),
    }


def build_repository_organisation_manifest(index: dict[str, Any]) -> dict[str, Any]:
    files = [classify_file(entry) for entry in index["files"]]

    action_counts: dict[str, int] = {}
    permanence_counts: dict[str, int] = {}
    subsystem_counts: dict[str, int] = {}

    for item in files:
        action_counts[item["recommended_action"]] = action_counts.get(item["recommended_action"], 0) + 1
        permanence_counts[item["permanence"]] = permanence_counts.get(item["permanence"], 0) + 1
        subsystem_counts[item["subsystem"]] = subsystem_counts.get(item["subsystem"], 0) + 1

    largest_files = sorted(files, key=lambda item: item["line_count"], reverse=True)[:50]

    return {
        "schema": "LEAF_REPOSITORY_ORGANISATION_MANIFEST_V1",
        "source_schema": index.get("schema"),
        "summary": {
            "files_classified": len(files),
            "action_counts": dict(sorted(action_counts.items())),
            "permanence_counts": dict(sorted(permanence_counts.items())),
            "subsystem_counts": dict(sorted(subsystem_counts.items())),
        },
        "target_folders": TARGET_FOLDERS,
        "largest_files": largest_files,
        "files": files,
        "safe_to_apply_moves": False,
        "note": (
            "This manifest is advisory only. It does not move files. "
            "Movement requires a separate dry-run organiser and regression gate."
        ),
    }


def build_text_report(manifest: dict[str, Any]) -> str:
    summary = manifest["summary"]

    lines = [
        "LEAF REPOSITORY ORGANISATION MANIFEST",
        "=====================================",
        f"schema={manifest['schema']}",
        f"files_classified={summary['files_classified']}",
        f"safe_to_apply_moves={manifest['safe_to_apply_moves']}",
        "",
        "ACTION COUNTS",
        "-------------",
    ]

    for key, value in summary["action_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "PERMANENCE COUNTS", "-----------------"])

    for key, value in summary["permanence_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "TOP 20 LARGEST FILES", "--------------------"])

    for item in manifest["largest_files"][:20]:
        lines.append(
            f"{item['line_count']:>6} lines | "
            f"{item['subsystem']} | "
            f"{item['role']} | "
            f"{item['recommended_action']} | "
            f"{item['path']}"
        )

    return "\n".join(lines)


def write_repository_organisation_manifest() -> dict[str, Any]:
    index = load_index()
    manifest = build_repository_organisation_manifest(index)

    write_json_artifact(manifest, OUT_JSON)
    write_text_artifact(build_text_report(manifest), OUT_TXT)

    return manifest


if __name__ == "__main__":
    result = write_repository_organisation_manifest()
    print(build_text_report(result))
    print("")
    print(f"json={OUT_JSON}")
    print(f"txt={OUT_TXT}")
    print("PASS_REPOSITORY_ORGANISATION_MANIFEST")
