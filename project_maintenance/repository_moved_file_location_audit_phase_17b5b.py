from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

PHASE = "17B.5B"
PASS_STATUS = "PASS_MOVED_FILE_LOCATION_AUDIT_PHASE_17B5B"
FAIL_STATUS = "FAIL_MOVED_FILE_LOCATION_AUDIT_PHASE_17B5B"

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "_leaf_artifacts" / "phase_17b_repository_architecture_engine"

MANIFESTS = [
    ROOT / "_leaf_artifacts/phase_16y_controlled_cleanup/repository_controlled_cleanup_rollback_manifest_phase_16y3.json",
    ROOT / "_leaf_artifacts/phase_17a_repository_reorganisation/repository_structural_move_rollback_manifest_phase_17a6.json",
    ROOT / "_leaf_artifacts/phase_17b_repository_architecture_engine/repository_root_python_move_rollback_manifest_phase_17b4.json",
]

OUT_JSON = OUT_DIR / "repository_moved_file_location_audit_phase_17b5b.json"
OUT_TXT = OUT_DIR / "repository_moved_file_location_audit_phase_17b5b.txt"

ALLOWED_DEVELOPMENT_TARGETS = (
    "_leaf_repository_cleanup_candidates/",
    "_leaf_reports/",
    "_leaf_packages/",
    "project_maintenance/",
    "_leaf_archive/",
)


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True, "path": path.as_posix(), "rollback_records": []}
    return json.loads(path.read_text(encoding="utf-8"))


def expected_class(path: str) -> str:
    if path.startswith("_leaf_repository_cleanup_candidates/"):
        return "CLEANUP_HOLDING"
    if path.startswith("_leaf_reports/"):
        return "REPORTS"
    if path.startswith("_leaf_packages/"):
        return "PACKAGES"
    if path.startswith("project_maintenance/"):
        return "DEVELOPMENT_MAINTENANCE"
    if path.startswith("_leaf_archive/"):
        return "ARCHIVE"
    return "UNEXPECTED_LOCATION"


def build_audit() -> dict:
    records = []
    failures = []

    for manifest_path in MANIFESTS:
        manifest = load_json(manifest_path)

        if manifest.get("missing"):
            records.append({
                "manifest": manifest_path.as_posix(),
                "status": "MISSING_MANIFEST",
            })
            continue

        for item in manifest.get("rollback_records", []):
            moved_to = item["restore_from"]
            original = item["restore_to"]

            moved_exists = (ROOT / moved_to).exists()
            original_exists = (ROOT / original).exists()
            location_class = expected_class(moved_to)
            allowed_target = moved_to.startswith(ALLOWED_DEVELOPMENT_TARGETS)

            record = {
                "manifest": manifest_path.relative_to(ROOT).as_posix(),
                "original": original,
                "moved_to": moved_to,
                "moved_exists": moved_exists,
                "original_still_exists": original_exists,
                "location_class": location_class,
                "allowed_development_target": allowed_target,
            }
            records.append(record)

            if not moved_exists:
                failures.append(f"Missing moved target: {moved_to}")

            if original_exists:
                failures.append(f"Original still exists after move: {original}")

            if not allowed_target:
                failures.append(f"Moved file is outside approved development target classes: {moved_to}")

    passed = not failures

    return {
        "phase": PHASE,
        "status": PASS_STATUS if passed else FAIL_STATUS,
        "passed": passed,
        "records_checked": len(records),
        "failure_count": len(failures),
        "failures": failures[:200],
        "records": records,
        "brief_compliance": {
            "development_only_governance": True,
            "runtime_pollution_allowed": False,
            "user_package_should_exclude_repository_governance": True,
            "approved_development_targets": list(ALLOWED_DEVELOPMENT_TARGETS),
        },
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "safety": {
            "moves_files": False,
            "deletes_files": False,
            "writes_reports_only": True,
        },
    }


def build_report(result: dict) -> str:
    lines = [
        "LEAF PHASE 17B.5B",
        "MOVED FILE LOCATION + BRIEF COMPLIANCE AUDIT",
        "============================================",
        f"Status: {result['status']}",
        f"Passed: {result['passed']}",
        f"Records checked: {result['records_checked']}",
        f"Failure count: {result['failure_count']}",
        "",
        "BRIEF COMPLIANCE",
        "----------------",
        "Repository organisation is development-only.",
        "Moved development files must not pollute runtime/user package folders.",
        "No files were moved or deleted by this audit.",
    ]

    if result["failures"]:
        lines.extend(["", "FAILURES", "--------"])
        lines.extend(f"- {f}" for f in result["failures"][:100])

    lines.extend(["", "LOCATION CLASS SAMPLE", "---------------------"])
    for r in result["records"][:120]:
        if "moved_to" in r:
            lines.append(f"- {r['original']} -> {r['moved_to']} [{r['location_class']}]")

    return "\n".join(lines)


def write_outputs() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = build_audit()
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_TXT.write_text(build_report(result), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = write_outputs()
    print(result["status"])
    print(f"passed={result['passed']}")
    print(f"records_checked={result['records_checked']}")
    print(f"failure_count={result['failure_count']}")
    print(f"report={OUT_TXT}")
    print(f"json={OUT_JSON}")
